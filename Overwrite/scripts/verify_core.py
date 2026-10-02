"""Run the official Mihomo parser on reconstructed test configurations.

This checks kernel syntax, not Clash Mi/Stash/Hako native merge behavior.
"""
from __future__ import annotations
import copy
import gzip
import hashlib
import json
import platform
import subprocess
import tempfile
import urllib.request
from pathlib import Path

from generate import ROOT, FILES, load, routing, yaml
from check_upstream import fetch


def core_binary(registry):
    entry = registry['versions']['Mihomo']
    release = json.loads(fetch(entry['version_url']))
    version = release['tag_name']
    if version != entry['reviewed_version']: raise ValueError('Mihomo 最新版未复核')
    system, machine = platform.system(), platform.machine().lower()
    if system == 'Darwin' and machine in {'arm64', 'aarch64'}:
        name = f'mihomo-darwin-arm64-{version}.gz'
    elif system == 'Linux' and machine in {'x86_64', 'amd64'}:
        name = f'mihomo-linux-amd64-compatible-{version}.gz'
    else:
        raise ValueError('尚未验证当前检查平台：' + system + '/' + machine)
    asset = next(a for a in release['assets'] if a['name'] == name)
    digest = asset.get('digest', '')
    if not digest.startswith('sha256:'): raise ValueError('官方资产缺少 SHA256，停止检查')
    cache = ROOT / '.build/tools'; cache.mkdir(parents=True, exist_ok=True)
    archive = cache / name
    if archive.exists(): data = archive.read_bytes()
    else:
        with urllib.request.urlopen(asset['browser_download_url'], timeout=60) as response:
            data = response.read(64 * 1024 * 1024 + 1)
    if len(data) > 64 * 1024 * 1024 or hashlib.sha256(data).hexdigest() != digest[7:]:
        raise ValueError('核心下载大小或 SHA256 错误')
    archive.write_bytes(data)
    binary = cache / ('mihomo-' + version)
    binary.write_bytes(gzip.decompress(data)); binary.chmod(0o755)
    return binary, version


def openclash_merge(base, override, directory):
    b = directory / 'base.json'; o = directory / 'override.json'
    b.write_text(json.dumps(base)); o.write_text(json.dumps({'+' + k: v for k, v in override.items()}))
    code = "require 'yaml'; require 'json'; require ARGV[0]; puts JSON.generate(YAML.overwrite(JSON.parse(File.read(ARGV[1])), JSON.parse(File.read(ARGV[2]))))"
    result = subprocess.run(['ruby', '-e', code, str(ROOT / 'Overwrite/compatibility/vendor/OpenClash-YAML.rb'), str(b), str(o)], text=True, capture_output=True, check=True, timeout=10)
    return json.loads(result.stdout)


def documented_stash_merge(base, override):
    if isinstance(base, dict) and isinstance(override, dict):
        result = copy.deepcopy(base)
        for k, v in override.items(): result[k] = documented_stash_merge(result.get(k), v)
        return result
    if isinstance(base, list) and isinstance(override, list): return copy.deepcopy(override + base)
    return copy.deepcopy(override)


def main():
    registry = json.loads((ROOT / 'Overwrite/compatibility/verified.json').read_text())
    binary, version = core_binary(registry)
    source = load((ROOT / 'Overwrite/source/routing.yaml').read_text())
    base = json.loads((ROOT / 'Overwrite/tests/fixtures/base.json').read_text())
    provider_bytes = {}
    provider_rules = []
    used = {k for p in FILES for k in routing(source, p)['rule-providers']}
    for name in sorted(used):
        data = fetch(source['providers'][name]['url'])
        if source['providers'][name].get('format', 'yaml') == 'yaml':
            doc = load(data.decode('utf-8'))
            if not isinstance(doc, dict) or not isinstance(doc.get('payload'), list) or not doc['payload']:
                raise ValueError(name + ' 规则集没有有效 payload')
            if any(not isinstance(r, str) or not r.strip() for r in doc['payload']):
                raise ValueError(name + ' payload 项错误')
            entries = doc['payload']
        else:
            entries = [x.strip() for x in data.decode('utf-8').splitlines() if x.strip() and not x.lstrip().startswith(('#', '//'))]
            if not entries:
                raise ValueError(name + ' 文本规则集为空')
        # -t may not initialize provider resources. Parse every classical entry
        # as a standalone route rule as well, preserving no-resolve placement.
        for entry_rule in entries:
            entry_rule = entry_rule.strip()
            if entry_rule.endswith(',no-resolve'):
                provider_rules.append(entry_rule[:-len(',no-resolve')] + ',DIRECT,no-resolve')
            else:
                provider_rules.append(entry_rule + ',DIRECT')
        provider_bytes[name] = data
    report = {'core_version': version, 'provider_count': len(used), 'provider_sha256': {k: hashlib.sha256(v).hexdigest() for k, v in provider_bytes.items()}, 'checks': []}
    with tempfile.TemporaryDirectory() as temp:
        directory = Path(temp); config = directory / 'config.yaml'
        config.write_text(yaml.safe_dump({'mode': 'rule', 'rules': provider_rules + ['MATCH,DIRECT']}, sort_keys=False))
        result = subprocess.run([str(binary), '-t', '-d', str(directory), '-f', str(config)], capture_output=True, text=True, timeout=30)
        if result.returncode:
            raise ValueError('实时规则集条目解析失败：\n' + result.stdout[-3000:] + result.stderr[-3000:])
        report['provider_entry_count'] = len(provider_rules)
        print(f'{len(used)} 个实时规则集、{len(provider_rules)} 条条目通过核心规则解析')
    for p in FILES:
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            r = routing(source, p)
            if p == 'clash':
                b = directory / 'base.json'; b.write_text(json.dumps(base))
                result = subprocess.run(['node', str(ROOT / 'Overwrite/tests/run_js.cjs'), str(ROOT / '.build/Overwrite' / FILES[p]), str(b)], capture_output=True, text=True, check=True, timeout=10)
                merged = json.loads(result.stdout); method = 'generated JS executed by Node; native engine pending'
            elif p == 'openclash':
                merged = openclash_merge(base, r, directory); method = 'official OpenClash YAML.overwrite'
            elif p == 'stash':
                merged = documented_stash_merge(base, r); method = 'documented Stash merge simulation; native pending'
            else:
                merged = copy.deepcopy(base); merged.update(r); method = 'Clash Mi patch standalone kernel syntax only; native merge unresolved'
            # Use downloaded provider bytes without external fetches during core parsing.
            for name, provider in merged['rule-providers'].items():
                local = directory / 'providers' / (name + '.rules'); local.parent.mkdir(exist_ok=True)
                local.write_bytes(provider_bytes[name])
                provider['type'] = 'file'; provider['path'] = './providers/' + local.name
                provider.pop('url', None)
            config = directory / 'config.yaml'; config.write_text(yaml.safe_dump(merged, allow_unicode=True, sort_keys=False))
            result = subprocess.run([str(binary), '-t', '-d', str(directory), '-f', str(config)], capture_output=True, text=True, timeout=30)
            if result.returncode:
                raise ValueError(p + ' 官方核心配置检查失败：\n' + result.stdout[-3000:] + result.stderr[-3000:])
            report['checks'].append({'platform': p, 'kernel_parse': 'passed', 'merge_check': method, 'native_verified': False})
            print(p + ' 官方 Mihomo 核心解析通过')
    report['scope'] = '核查实时规则集及 Mihomo 语法；不能替代各客户端原生导入和更新验收。'
    (ROOT / '.build/core-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__': main()
