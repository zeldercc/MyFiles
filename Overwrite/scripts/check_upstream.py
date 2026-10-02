"""Fail closed when upstream versions or recorded normative content change."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import time
import urllib.request
from pathlib import Path
from html.parser import HTMLParser

ROOT = Path(__file__).resolve().parents[2]


class VisibleText(HTMLParser):
    def __init__(self):
        super().__init__(); self.hidden = 0; self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style"}: self.hidden += 1

    def handle_endtag(self, tag):
        if tag in {"script", "style"}: self.hidden = max(0, self.hidden - 1)

    def handle_data(self, data):
        if not self.hidden: self.parts.append(data)


def fetch(url):
    headers = {"User-Agent": "MyFiles-Overwrite-Validation", "Accept": "*/*"}
    # GITHUB_TOKEN is used only for GitHub API requests; it is never printed.
    token = os.environ.get("GITHUB_TOKEN")
    if url.startswith("https://api.github.com/") and token:
        headers["Authorization"] = "Bearer " + token
    last = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30) as response:
                data = response.read(4 * 1024 * 1024 + 1)
            if len(data) > 4 * 1024 * 1024: raise ValueError("规范文件超过大小限制")
            return data
        except Exception as exc:
            last = exc
            if attempt < 2: time.sleep(attempt + 1)
    raise RuntimeError("上游查询失败，保留旧输出：" + url) from last


def fingerprint(raw, mode):
    if mode == "visible_text":
        parser = VisibleText(); parser.feed(raw.decode("utf-8"))
        raw = " ".join(" ".join(parser.parts).split()).encode()
    elif mode != "bytes":
        raise ValueError("未知规范摘要方式")
    return hashlib.sha256(raw).hexdigest()


def latest(entry):
    doc = json.loads(fetch(entry["version_url"]))
    if entry["version_kind"] == "github_release":
        if doc.get("draft") or doc.get("prerelease"): raise ValueError("不接受预发布版本")
        return doc["tag_name"]
    if entry["version_kind"] == "apple":
        if len(doc.get("results", [])) != 1: raise ValueError("商店版本查询不唯一")
        return doc["results"][0]["version"]
    raise ValueError("未知版本来源")


def check(registry):
    result = {"versions": {}, "normative_sources": [], "native_verified": False}
    for name, entry in registry["versions"].items():
        actual = latest(entry)
        result["versions"][name] = actual
        if actual != entry["reviewed_version"]:
            raise ValueError(f"{name} 最新版本 {actual} 未复核，已记录版本为 {entry['reviewed_version']}，停止发布")
    for entry in registry["normative_sources"]:
        actual = fingerprint(fetch(entry["url"]), entry["mode"])
        if actual != entry["sha256"]:
            raise ValueError("官方规范或解析实现变化，须复核：" + entry["name"])
        result["normative_sources"].append({"name": entry["name"], "url": entry["url"], "sha256": actual})
    result["note"] = "源码及文档核查不等于原生客户端实测；Clash 应用版本仍需确认。"
    return result


def publication_problems(registry):
    policy = registry.get("publication_policy", {"mode": "native_required"})
    if policy.get("mode") == "automated_checks_only":
        if policy.get("native_tests_skipped_by_user") is not True or not policy.get("reason"):
            return ["跳过原生实测的发布策略缺少明确记录"]
        # This waives only native acceptance. Latest normative checks, unit
        # tests and kernel parsing remain mandatory workflow steps.
        return []
    if policy.get("mode") != "native_required":
        return ["未知发布策略，停止发布"]
    problems = []
    for platform in ("clash", "openclash", "clashmi", "stash"):
        item = registry["native_acceptance"][platform]
        if item.get("accepted") is not True:
            problems.append(platform + " 原生客户端验收未完成")
            continue
        if not item.get("app_version") or not item.get("evidence_file"):
            problems.append(platform + " 缺少版本或验收记录")
            continue
        path = Path(item["evidence_file"])
        if path.is_absolute() or ".." in path.parts or not path.parts or path.parts[:3] != ("Overwrite", "compatibility", "evidence"):
            problems.append(platform + " 验收记录路径错误"); continue
        try:
            doc = json.loads((ROOT / path).read_text(encoding="utf-8"))
            checks = ("import", "update", "add", "modify", "delete", "empty", "base_preserved", "fixed_url")
            if doc.get("app_version") != item["app_version"] or any(doc.get("checks", {}).get(c) is not True for c in checks):
                problems.append(platform + " 原生验收项目不完整")
            key = {"openclash": "OpenClash", "clashmi": "ClashMi", "stash": "Stash"}.get(platform)
            if key and item["app_version"] != registry["versions"][key]["reviewed_version"]:
                problems.append(platform + " 验收版本与规范版本不一致")
            if not doc.get("tested_at") or not doc.get("evidence") or not isinstance(doc["evidence"], list):
                problems.append(platform + " 缺少实测时间和可核查证据")
        except (OSError, ValueError):
            problems.append(platform + " 无法读取验收记录")
    # Source audit alone cannot identify the installed Clash/Hako App Store app.
    if "Clash" not in registry["versions"]:
        problems.append("尚未配置确认后的 Clash 应用最新版本查询入口")
    return problems


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--publication-check", action="store_true")
    args = parser.parse_args()
    registry = json.loads((ROOT / "Overwrite/compatibility/verified.json").read_text(encoding="utf-8"))
    if args.publication_check:
        problems = publication_problems(registry)
        if problems:
            print("正式发布尚未启用：\n" + "\n".join(problems)); raise SystemExit(2)
        if registry.get("publication_policy", {}).get("mode") == "automated_checks_only":
            print("用户要求跳过原生实测；允许在自动校验全部通过后发布。原生实测状态仍为未验证。")
        else:
            print("四端原生验收记录通过")
        return
    result = check(registry)
    out = ROOT / ".build/upstream-report.json"; out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("本次最新版本及官方规范指纹核查通过；原生验收状态另行检查。")


if __name__ == "__main__": main()
