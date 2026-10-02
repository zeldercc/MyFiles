"""Generate fixed-path candidates. No network or subscription secrets are needed."""
from __future__ import annotations

import argparse
import copy
import hashlib
import ipaddress
import json
import re
import subprocess
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
PLATFORMS = ("clash", "openclash", "clashmi", "stash")
FILES = dict(zip(PLATFORMS, (
    "clash-ios-routing-overwrite.js", "openclash-routing-overwrite.yaml",
    "clashmi-routing-overwrite.yaml", "stash-routing-overwrite.yaml")))
RULE_TYPES = {"DOMAIN", "DOMAIN-SUFFIX", "DOMAIN-KEYWORD", "IP-CIDR", "IP-CIDR6", "RULE-SET"}


class Invalid(ValueError):
    pass


class StrictLoader(yaml.SafeLoader):
    def compose_node(self, parent, index):
        if self.check_event(yaml.AliasEvent):
            raise Invalid("不允许 YAML 锚点或别名，请直接填写内容")
        return super().compose_node(parent, index)


def unique_mapping(loader, node, deep=False):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if not isinstance(key, str) or key in result:
            raise Invalid(f"键名必须是唯一字符串，第 {key_node.start_mark.line + 1} 行")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


StrictLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)


def load(text):
    try:
        return yaml.load(text, Loader=StrictLoader)
    except yaml.YAMLError as exc:
        raise Invalid(f"YAML 解析失败：{exc}") from exc


def require(condition, message):
    if not condition:
        raise Invalid(message)


def fields(obj, allowed, required, label):
    require(isinstance(obj, dict), f"{label} 必须是对象")
    require(set(obj) <= set(allowed), f"{label} 含未知字段：{set(obj) - set(allowed)}")
    require(set(required) <= set(obj), f"{label} 缺少字段：{set(required) - set(obj)}")


def string(value, label):
    require(isinstance(value, str) and value.strip() == value and bool(value), f"{label} 必须是非空字符串，不能有首尾空格")
    require(not any(ord(c) < 32 for c in value), f"{label} 不允许控制字符")


def platform_list(value, label):
    require(isinstance(value, list) and bool(value), f"{label} 需要非空平台列表")
    require(all(isinstance(x, str) and x in PLATFORMS for x in value), f"{label} 包含未知平台")
    require(len(set(value)) == len(value), f"{label} 平台重复")


def validate(source):
    fields(source, {"schema_version", "targets", "managed_targets", "providers", "groups", "rules", "platforms"},
           {"schema_version", "targets", "managed_targets", "providers", "groups", "rules", "platforms"}, "源文件")
    require(type(source["schema_version"]) is int and source["schema_version"] == 1, "schema_version 必须为 1")
    targets = source["targets"]
    require(isinstance(targets, dict), "targets 必须是对象")
    for alias, name in targets.items():
        require(bool(re.fullmatch(r"[a-z][a-z0-9_]*", alias)), f"目标别名错误：{alias}")
        string(name, f"targets.{alias}")
        require("," not in name, f"策略名不能包含逗号：{alias}")
    require(targets.get("direct") == "DIRECT" and targets.get("reject") == "REJECT", "direct/reject 必须映射到 DIRECT/REJECT")
    require(len(set(targets.values())) == len(targets), "策略名称重复")
    require(isinstance(source["managed_targets"], list) and all(isinstance(t, str) and t in targets for t in source["managed_targets"]), "managed_targets 必须列出自定义策略的别名")
    managed_names = {targets[t] for t in source["managed_targets"]}
    providers = source["providers"]
    require(isinstance(providers, dict), "providers 必须是对象")
    paths = []
    for name, provider in providers.items():
        require(bool(re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", name)), f"provider 名称错误：{name}")
        fields(provider, {"type", "behavior", "format", "url", "path", "interval"},
               {"type", "behavior", "url", "path", "interval"}, name)
        require(provider["type"] == "http" and provider["behavior"] == "classical", f"{name} 当前仅验证 http/classical")
        require(provider.get("format", "yaml") in {"yaml", "text"}, f"{name} format 不支持")
        string(provider["url"], name + ".url")
        from urllib.parse import urlsplit
        parsed = urlsplit(provider["url"])
        require(parsed.scheme == "https" and bool(parsed.netloc) and not parsed.username and not parsed.password and not parsed.fragment,
                f"{name} 需要不含账号和片段的 HTTPS URL")
        path = provider["path"]
        string(path, name + ".path")
        require(bool(re.fullmatch(r"\./(?:ruleset|rule_provider)/[A-Za-z0-9_.-]+", path)) and ".." not in path[2:], f"{name} 缓存路径错误")
        paths.append(path)
        require(type(provider["interval"]) is int and 60 <= provider["interval"] <= 604800, f"{name} interval 需要 60 至 604800 秒")
    require(len(set(paths)) == len(paths), "provider 缓存路径重复")
    require(isinstance(source["groups"], list), "groups 必须是列表，空列表写 []")
    group_names = []
    for group in source["groups"]:
        fields(group, {"name", "type", "targets", "url", "interval", "platforms"},
               {"name", "type", "targets", "url", "interval", "platforms"}, "group")
        string(group["name"], "group.name")
        require(group["name"] not in {"DIRECT", "REJECT"} and "," not in group["name"], "group.name 非法")
        group_names.append(group["name"])
        require(group["name"] in managed_names, "自定义组必须在 managed_targets 中登记")
        platform_list(group["platforms"], "group.platforms")
        require(group["type"] == "fallback", "目前只验证 fallback 自定义组")
        require(isinstance(group["targets"], list) and len(group["targets"]) >= 2, "fallback 需要至少两个目标")
        require(all(isinstance(t, str) and t in targets for t in group["targets"]), "group.targets 存在未知目标")
        require(not any(t in source["managed_targets"] for t in group["targets"]), "当前不接受自定义组相互引用")
        require(len(set(group["targets"])) == len(group["targets"]), "group.targets 重复")
        require(group["name"] not in [targets[t] for t in group["targets"]], "策略组不能引用自身")
        string(group["url"], "group.url")
        require(group["url"].startswith(("https://", "http://")), "group.url 必须为 HTTP(S)")
        require(type(group["interval"]) is int and 60 <= group["interval"] <= 604800, "group.interval 错误")
    require(len(set(group_names)) == len(group_names), "自定义策略组名称重复")
    require(isinstance(source["rules"], list), "rules 必须是列表，空列表写 []")
    ids = []
    for rule in source["rules"]:
        fields(rule, {"id", "type", "value", "target", "no_resolve", "platforms"},
               {"id", "type", "value", "target"}, "rule")
        require(isinstance(rule["id"], str) and bool(re.fullmatch(r"[A-Za-z0-9_-]+", rule["id"])), "rule.id 只能使用字母、数字、下划线及连字符")
        ids.append(rule["id"])
        require(isinstance(rule["type"], str) and rule["type"] in RULE_TYPES, f"{rule['id']} 规则类型未经验证")
        string(rule["value"], rule["id"] + ".value")
        require("," not in rule["value"], f"{rule['id']} value 不能含逗号")
        require(isinstance(rule["target"], str) and rule["target"] in targets, f"{rule['id']} 目标不存在")
        require(type(rule.get("no_resolve", False)) is bool, "no_resolve 必须是 true/false")
        if "platforms" in rule:
            platform_list(rule["platforms"], rule["id"])
        if rule["type"] == "RULE-SET":
            require(rule["value"] in providers, f"{rule['id']} 引用的 provider 不存在")
            require(not rule.get("no_resolve", False), "当前 RULE-SET 不接受 no_resolve")
        elif rule["type"] in {"IP-CIDR", "IP-CIDR6"}:
            try:
                network = ipaddress.ip_network(rule["value"], strict=True)
            except ValueError as exc:
                raise Invalid(f"{rule['id']} CIDR 错误：{exc}") from exc
            require(rule["type"] != "IP-CIDR6" or network.version == 6, "IP-CIDR6 必须是 IPv6")
        else:
            require(not rule.get("no_resolve", False), "域名规则不能使用 no_resolve")
            require(not any(c.isspace() for c in rule["value"]), "域名规则不能含空白")
            if rule["type"] != "DOMAIN-KEYWORD":
                require(bool(re.fullmatch(r"[A-Za-z0-9_-]+(?:\.[A-Za-z0-9_-]+)*", rule["value"])), "域名语法错误")
    require(len(set(ids)) == len(ids), "rule.id 重复")
    fields(source["platforms"], PLATFORMS, PLATFORMS, "platforms")
    for p, options in source["platforms"].items():
        fields(options, {"dns"}, set(), p)
        if "dns" in options:
            require(options["dns"] == {"enable": True, "enhanced-mode": "fake-ip"}, f"{p} DNS 设置未经验证")
    for p in PLATFORMS:
        active_groups = {g["name"] for g in source["groups"] if p in g["platforms"]}
        for rule in source["rules"]:
            if p in rule.get("platforms", list(PLATFORMS)):
                target = targets[rule["target"]]
                require(target not in managed_names or target in active_groups, f"{p} 缺少规则依赖的自定义策略组：{target}")


def routing(source, platform):
    active = [r for r in source["rules"] if platform in r.get("platforms", PLATFORMS)]
    provider_names = {r["value"] for r in active if r["type"] == "RULE-SET"}
    providers = {k: copy.deepcopy(v) for k, v in source["providers"].items() if k in provider_names}
    groups = [{"name": g["name"], "type": g["type"], "proxies": [source["targets"][t] for t in g["targets"]],
               "url": g["url"], "interval": g["interval"]} for g in source["groups"] if platform in g["platforms"]]
    rules = []
    for r in active:
        entry = ",".join([r["type"], r["value"], source["targets"][r["target"]]])
        if r.get("no_resolve", False):
            entry += ",no-resolve"
        require(entry not in rules, f"{platform} 重复规则：{r['id']}")
        rules.append(entry)
    result = {"rule-providers": providers, "rules": rules}
    if groups:
        result["proxy-groups"] = groups
    if "dns" in source["platforms"][platform]:
        result["dns"] = copy.deepcopy(source["platforms"][platform]["dns"])
    return result


JS_TEMPLATE = '''function main(config) {
  if (!config || typeof config !== "object" || Array.isArray(config)) {
    throw new Error("需要原始订阅配置对象");
  }
  var routing = __ROUTING__;
  var original = JSON.parse(JSON.stringify(config));
  ["rules", "proxies", "proxy-groups"].forEach(function (key) {
    if (original[key] !== undefined && !Array.isArray(original[key])) throw new Error(key + " 必须是数组");
  });
  ["rule-providers", "dns"].forEach(function (key) {
    if (original[key] !== undefined && (!original[key] || typeof original[key] !== "object" || Array.isArray(original[key]))) throw new Error(key + " 必须是对象");
  });
  var groups = original["proxy-groups"] || [];
  var newGroups = routing["proxy-groups"] || [];
  var names = ["DIRECT", "REJECT"];
  (original.proxies || []).concat(groups, newGroups).forEach(function (item) {
    if (item && typeof item.name === "string") names.push(item.name);
  });
  var targets = routing.rules.map(function (rule) { return rule.split(",")[2]; });
  newGroups.forEach(function (group) { targets = targets.concat(group.proxies || []); });
  var missing = targets.filter(function (name, index, all) { return names.indexOf(name) < 0 && all.indexOf(name) === index; });
  if (missing.length) throw new Error("基础订阅缺少策略组或节点：" + missing.join(", "));
  original["rule-providers"] = Object.assign({}, original["rule-providers"] || {}, routing["rule-providers"]);
  var replaced = newGroups.map(function (group) { return group.name; });
  original["proxy-groups"] = newGroups.concat(groups.filter(function (group) { return replaced.indexOf(group.name) < 0; }));
  original.rules = routing.rules.concat((original.rules || []).filter(function (rule) { return routing.rules.indexOf(rule) < 0; }));
  if (routing.dns) original.dns = Object.assign({}, original.dns || {}, routing.dns);
  return original;
}
'''


def render(source):
    validate(source)
    digest = hashlib.sha256(json.dumps(source, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    outputs = {}
    for p in PLATFORMS:
        r = routing(source, p)
        comment = f"自动生成。仅编辑 Overwrite/source/routing.yaml。source-sha256: {digest}\n"
        if p == "clash":
            text = "// " + comment + "// 每次从原始订阅应用；不要将旧运行配置作为输入。\n" + JS_TEMPLATE.replace("__ROUTING__", json.dumps(r, ensure_ascii=False, indent=2))
        elif p == "openclash":
            body = {("+" + k if k in {"rules", "proxy-groups", "rule-providers"} else k): v for k, v in r.items()}
            text = "# " + comment + "[YAML]\n" + yaml.safe_dump(body, allow_unicode=True, sort_keys=False, width=1000)
        else:
            body = r if p == "clashmi" else {"name": "Routing Override", "desc": "自定义分流及 Apple Push 回退规则", **r}
            text = "# " + comment + yaml.safe_dump(body, allow_unicode=True, sort_keys=False, width=1000)
        outputs[FILES[p]] = text
    require(set(outputs) == set(FILES.values()), "输出文件路径清单不一致")
    return outputs


def verify_outputs(source, outputs):
    require(set(outputs) == set(FILES.values()), "输出文件名称不正确")
    for p, name in FILES.items():
        if p == "clash":
            continue
        text = outputs[name]
        if p == "openclash":
            require(text.count("[YAML]") == 1, "OpenClash 模块入口错误")
            doc = load(text.split("[YAML]\n", 1)[1])
            doc = {k.removeprefix("+"): v for k, v in doc.items()}
        else:
            doc = load(text)
            if p == "stash":
                doc.pop("name"); doc.pop("desc")
        require(doc == routing(source, p), f"{name} 序列化后内容不一致")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=ROOT / "Overwrite/source/routing.yaml")
    parser.add_argument("--out", type=Path, default=ROOT / ".build/Overwrite")
    args = parser.parse_args()
    source = load(args.source.read_text(encoding="utf-8"))
    outputs = render(source)
    verify_outputs(source, outputs)
    # Write only after every source and serialization check passed.
    args.out.mkdir(parents=True, exist_ok=True)
    for name, text in outputs.items():
        (args.out / name).write_text(text, encoding="utf-8")
    subprocess.run(["node", "--check", str(args.out / FILES["clash"])], check=True)
    print(f"已生成并校验四份候选文件：{args.out}")


if __name__ == "__main__":
    main()
