# 单源覆写自动生成

日常只编辑 `Overwrite/source/routing.yaml`。四个正式输出的文件名和路径保持不变。

当前交付状态：本地生成、自动校验及 GitHub Actions 工作流已准备；未在 GitHub 运行。四端原生客户端验收尚未完成，因此工作流先生成候选附件，不覆盖正式输出。

## 自动流程

源文件提交到 main 后，工作流先查询官方最新版本及规范指纹，再运行增删测试、生成四份候选、下载公开规则集，使用官方 Mihomo 核心检查。所有检查成功后保存候选附件。只有四端原生验收记录完整时，才将四份正式输出作为一个提交发布。

上游版本变化、文档或解析代码指纹变化、查询失败、源文件错误、规则集下载失败、核心检查失败都会停止本次生成或发布，保留原正式输出。

## 固定输出地址

```text
https://raw.githubusercontent.com/zeldercc/MyFiles/main/Overwrite/clash-ios-routing-overwrite.js
https://raw.githubusercontent.com/zeldercc/MyFiles/main/Overwrite/openclash-routing-overwrite.yaml
https://raw.githubusercontent.com/zeldercc/MyFiles/main/Overwrite/clashmi-routing-overwrite.yaml
https://raw.githubusercontent.com/zeldercc/MyFiles/main/Overwrite/stash-routing-overwrite.yaml
```

不要使用固定提交号作为持续更新地址。

## 日常增加、删除和修改

普通规则由 `id/type/value/target` 组成，匹配顺序按列表顺序。例如添加：

```yaml
- id: example_direct
  type: DOMAIN-SUFFIX
  value: example.com
  target: direct
```

删除规则时删除完整条目。改变目标时修改 `target`。当前支持 `direct/reject/us/jp/hk/game/apple_push`，完整策略组名称由 `targets` 映射，需与基础订阅一致。`apple_push` 只用于启用了对应组的平台。

新增规则集时，在同一源文件的 `providers` 定义 HTTPS 规则集，再添加 `RULE-SET` 规则。删除引用后，该平台不再使用的 provider 不会写入输出；定义可保留或一起删除。删除仍被引用的 provider 会校验失败。

目前只接受已建立验证用例的 DOMAIN、DOMAIN-SUFFIX、DOMAIN-KEYWORD、IP-CIDR、IP-CIDR6、RULE-SET、HTTP classical YAML/text provider、fallback 自定义组。其他类型需要先增加兼容验证。

## 删除的前提

每次从原始订阅重新应用最新覆写。不要将已经覆写的旧运行配置作为基础配置。删除只清理源文件管理的内容；原订阅自带相同规则时不会自动删除它。

## 验证范围

- 源文件重复键、未知字段、重复 ID、引用、CIDR、规则及缓存路径检查。
- YAML 序列化往返及固定路径检查。
- Node 执行 JS，检查合并、订阅保留、缺失策略、重复应用。
- 使用 OpenClash v0.47.156 的官方 `YAML.overwrite` 实现验证模块合并。
- 实时下载规则集，逐条交给官方 Mihomo 核心解析，记录内容摘要。
- Stash 使用官方文档描述的合并模型，仍需原生实测。
- Clash Mi 候选仅验证 YAML 和核心语法，实际数组合并由其服务层处理，尚未确认。
- Mihomo 检查不能代表 Stash 或 Hako 原生内核检查通过。

## 正式发布验收

`compatibility/verified.json` 的 `native_acceptance` 初始为 false。不得直接改成 true 来跳过验收。

需记录每端版本、导入、更新、新增、修改、删除、删空、基础订阅保留及固定 URL 成功的真实结果。验收证据以 JSON 保存在 `Overwrite/compatibility/evidence/`，包含 `app_version`、`tested_at`、`checks` 和具体 `evidence` 列表。还需确认 Clash 对应应用并添加其官方最新版本查询入口。版本与已核查规范不同，验收不能用于开启发布。

Stash 文档规定 `.stoverride`，本项目按用户要求保留 `.yaml` 文件名。必须实测所用远程导入及更新入口是否接受此固定地址。

## 本地检查

```sh
python -m pip install -r Overwrite/requirements.txt
python Overwrite/scripts/check_upstream.py
python -m unittest discover -s Overwrite/tests -v
python Overwrite/scripts/generate.py
python Overwrite/scripts/verify_core.py
python Overwrite/scripts/check_upstream.py --publication-check
```

最后一条在原生验收未完成时返回 2，表示正式发布尚未启用。生成默认写入 `.build/Overwrite`，不会覆盖现有四份文件。

## 来源

- 原始配置： https://github.com/zeldercc/MyFiles/tree/9b7c466e032f98841fe186a49399f7129698b0c4/Overwrite
- OpenClash： https://github.com/vernesong/OpenClash/releases/tag/v0.47.156
- Clash Mi： https://github.com/KaringX/clashmi/releases/tag/v1.0.30.1605
- Clash Mi 简体中文规范： https://clashmi.app/guide/faq
- Stash 英文覆写规范： https://stash.wiki/en/configuration/override
- Stash 繁体中文发布信息： https://apps.apple.com/tw/app/stash/id1596063349
- Hako JS 引擎： https://github.com/TokenPLS/Hako-Client/blob/main/apple/HakoClient/Sources/ConfigUI/ScriptEngine.swift
- GitHub Actions： https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax

规范与版本检查记录在 `compatibility/verified.json`；改变基线需要核查差异并重新验证，不能仅更新摘要来解除阻止发布的限制。
