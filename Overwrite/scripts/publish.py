"""Publish only reviewed, unchanged candidates; never force push."""
import hashlib
import json
import os
import subprocess
import time
import urllib.request
from generate import ROOT, FILES, load, render


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()


def main():
    from check_upstream import publication_problems
    registry = json.loads((ROOT / 'Overwrite/compatibility/verified.json').read_text())
    if publication_problems(registry): raise ValueError('未完成原生验收，不发布')
    expected = render(load((ROOT / 'Overwrite/source/routing.yaml').read_text()))
    for name, content in expected.items():
        if (ROOT / '.build/Overwrite' / name).read_text() != content:
            raise ValueError('候选内容与当前源文件不一致：' + name)
    git('fetch', 'origin', 'main')
    if git('rev-parse', 'origin/main') != git('rev-parse', 'HEAD'):
        raise ValueError('main 已有新提交，停止旧任务发布')
    for name, content in expected.items():
        (ROOT / 'Overwrite' / name).write_text(content, encoding='utf-8')
    paths = ['Overwrite/' + n for n in FILES.values()]
    git('add', '--', *paths)
    changed = git('diff', '--cached', '--name-only').splitlines()
    if not set(changed) <= set(paths): raise ValueError('暂存区含非固定输出文件')
    if not changed:
        print('四份正式文件无需更新'); return
    git('config', 'user.name', 'github-actions[bot]')
    git('config', 'user.email', '41898282+github-actions[bot]@users.noreply.github.com')
    git('commit', '-m', 'Generate four validated overrides')
    git('push', 'origin', 'HEAD:main')
    repo = os.environ['GITHUB_REPOSITORY']
    for name, content in expected.items():
        wanted = hashlib.sha256(content.encode()).hexdigest()
        url = 'https://raw.githubusercontent.com/' + repo + '/main/Overwrite/' + name
        matched = False
        for attempt in range(6):
            try:
                req = urllib.request.Request(url, headers={'Cache-Control': 'no-cache', 'User-Agent': 'MyFiles-Overwrite-Validation'})
                with urllib.request.urlopen(req, timeout=20) as response: actual = response.read()
                if hashlib.sha256(actual).hexdigest() == wanted:
                    matched = True; break
            except OSError:
                pass
            time.sleep(5)
        if not matched: raise ValueError('提交已推送，但固定 URL 内容尚未核对成功：' + name)
    print('四份固定地址内容核对成功')


if __name__ == '__main__': main()
