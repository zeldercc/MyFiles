---
name: A股相关研报_skill
description: >
  每周日18:00自动抓取宏观/策略/行业研报，聚焦A股市场，
  总结研报核心观点，提取相关标的（含行业龙头股票和ETF，仅限A股可买标的），
  结合研报逻辑给出有来源支撑的投资建议，并参考YouTube频道研报分析视频结论。
version: "2.0"
focus: "A股（含科创板、创业板）"
---

## 一、每周定时任务（cron: 0 0 18 * * 0，每周日 18:00 执行一次）

执行顺序：
1. 拉取下方所有 RSS 源，过去 **7 天（168 小时）** 新内容
2. 过滤：只保留涉及 A股、中国宏观、人民币 的条目
3. 对每篇研报/文章生成结构化摘要（见第八节 Prompt 模板）
4. 提取相关标的：行业龙头个股（仅A股代码）+ ETF（仅A股上市ETF）
5. 结合研报逻辑输出投资建议（每条建议必须注明支撑研报名称和机构，不得给无来源结论）
6. 参考 YouTube 频道 @oldpowerful 过去7天视频结论（见第十节）
7. 推送 Markdown 格式周报到 Telegram

---

## 二、RSS 源配置（全部免费，聚焦A股市场）

### 宏观与策略快讯

```
华尔街见闻-要闻:        https://wallstreetcn.com/rss/news
财联社电报(全量):        https://rsshub.app/cls/telegraph
财联社-热门:             https://rsshub.app/cls/hot
格隆汇-研报:             https://rsshub.app/gelonghui/home/research
格隆汇-A股热点:          https://rsshub.app/gelonghui/home
36氪-商业:               https://36kr.com/feed
虎嗅:                    https://www.huxiu.com/rss/0.xml
彭博中港宏观(免费摘要):  https://feeds.bloomberg.com/markets/news.rss
FT中文网:                https://www.ftchinese.com/rss/feed
MacroMicro财经M平方:     https://sc.macromicro.me/feed
```

### 东方财富研报（RSSHub路由）

```
A股策略研究:    https://rsshub.app/eastmoney/search/策略研究
宏观研究:       https://rsshub.app/eastmoney/search/宏观研究
半导体:         https://rsshub.app/eastmoney/search/半导体
AI大模型:       https://rsshub.app/eastmoney/search/大模型
新能源/储能:    https://rsshub.app/eastmoney/search/新能源
消费复苏:       https://rsshub.app/eastmoney/search/消费复苏
医药生物:       https://rsshub.app/eastmoney/search/医药生物
军工:           https://rsshub.app/eastmoney/search/军工
银行金融:       https://rsshub.app/eastmoney/search/银行股
红利资产:       https://rsshub.app/eastmoney/search/红利
央企国企:       https://rsshub.app/eastmoney/search/央企改革
```

> 自建RSSHub（推荐）：docker run -d -p 1200:1200 diygod/rsshub
> 将上方 rsshub.app 替换为 localhost:1200 以提升稳定性

---

## 三、关键词过滤（只保留涉及A股市场的内容）

**保留条目，须含以下词之一：**
```
中国, A股, 沪深, 人民币, MSCI, 北向资金, 中证, 上证, 创业板, 科创板,
大宗商品(与中国相关), 新兴市场, 亚太
```

**排除条目，含以下词则过滤掉：**
```
美股个股(非中概), 欧洲市场, 日股(与A股无关联),
加密货币, 房产中介广告, 港股(纯港股个股，不含A+H股)
```

---

## 四、重点追踪分析师

每周日 18:00 用 Fetch 工具抓取以下页面，提取过去7天研报标题和摘要：
抓取地址：https://data.eastmoney.com/report/zw_strategy.jshtml

重点筛选以下作者署名的报告：

### A股策略首席

| 分析师 | 机构 | 专长方向 |
|--------|------|---------|
| 裘翔   | 中信证券 | A股整体策略、盈利预测框架 |
| 李求索 | 中金公司 | 全球资产配置、外资定价 |
| 彭文生 | 中金公司 | 中国宏观经济、货币政策 |
| 张夏   | 招商证券 | 风格轮动、主题投资方向 |
| 张启尧 | 兴业证券 | 市场情绪、北向资金面 |
| 傅静涛 | 申万宏源 | 行业景气度量化追踪 |
| 燕翔   | 国信证券 | 中小盘、成长股逻辑 |

---

## 五、行业研报 → 机构矩阵（聚焦A股影响）

```yaml
行业覆盖矩阵:

  半导体/科技硬件:
    机构: [中信证券, 华泰证券, 东吴证券]
    RSS: https://rsshub.app/eastmoney/search/半导体
    相关指数: 科创50, 中证半导体
    行业龙头参考(仅A股):
      - 中芯国际(688981.SH)
      - 北方华创(002371.SZ)
      - 澜起科技(688008.SH)
      - 寒武纪(688256.SH)

  AI/大模型/云计算:
    机构: [中信证券, 国盛证券, 华创证券]
    RSS: https://rsshub.app/eastmoney/search/大模型
    相关指数: 科创100, 中证人工智能
    行业龙头参考(仅A股):
      - 科大讯飞(002230.SZ)
      - 中科曙光(603019.SH)
      - 浪潮信息(000977.SZ)

  新能源/电池/储能:
    机构: [天风证券, 平安证券, 招商证券]
    RSS: https://rsshub.app/eastmoney/search/新能源
    相关指数: 中证新能源, 创业板指
    行业龙头参考(仅A股):
      - 宁德时代(300750.SZ)
      - 比亚迪(002594.SZ)
      - 阳光电源(300274.SZ)
      - 亿纬锂能(300014.SZ)

  消费/零售/可选消费:
    机构: [华创证券, 兴业证券, 中泰证券]
    RSS: https://rsshub.app/eastmoney/search/消费复苏
    相关指数: 中证消费
    行业龙头参考(仅A股):
      - 贵州茅台(600519.SH)
      - 美的集团(000333.SZ)
      - 海天味业(603288.SH)

  医药/生物/CXO:
    机构: [中泰证券, 国泰海通, 天风证券]
    RSS: https://rsshub.app/eastmoney/search/医药生物
    相关指数: 中证医疗, 创新药ETF
    行业龙头参考(仅A股):
      - 药明康德(603259.SH)
      - 恒瑞医药(600276.SH)
      - 迈瑞医疗(300760.SZ)
      - 百济神州(688235.SH)

  军工/航天/船舶:
    机构: [申万宏源, 招商证券, 中信证券]
    RSS: https://rsshub.app/eastmoney/search/军工
    相关指数: 中证军工
    行业龙头参考(仅A股):
      - 中航沈飞(600760.SH)
      - 中直股份(600038.SH)
      - 航发动力(600893.SH)
      - 中船防务(600685.SH)

  银行/非银金融:
    机构: [中信建投, 中金公司, 招商证券]
    RSS: https://rsshub.app/eastmoney/search/银行股
    相关指数: 中证银行, 沪深300金融
    行业龙头参考(仅A股):
      - 招商银行(600036.SH)
      - 工商银行(601398.SH)
      - 平安保险(601318.SH)
      - 东方财富(300059.SZ)

  红利/央企/高股息:
    机构: [申万宏源, 中金公司, 华泰证券]
    RSS: https://rsshub.app/eastmoney/search/红利
    相关指数: 中证红利, 上证红利, 央企红利ETF
    行业龙头参考(仅A股):
      - 长江电力(600900.SH)
      - 中国神华(601088.SH)
      - 中国移动(600941.SH)
      - 中国海油(600938.SH)

  宏观/大类资产配置:
    机构: [中金公司, 中信证券, 海通证券]
    RSS:
      - https://rsshub.app/eastmoney/search/宏观研究
      - https://wallstreetcn.com/rss/news
      - https://sc.macromicro.me/feed
```

---

## 六、研报摘要与投资建议输出格式

每篇研报按以下结构处理：

```
【研报名称】来自：{机构} | {分析师（若有）} | {发布时间}

核心观点：（2-3句话，提炼研报主要判断）

涉及标的（仅列A股可买标的，港股纯港股代码不列出）：
- A股龙头个股：{股票名称(A股代码)} — 理由：{一句话}
- 相关ETF（A股上市）：{ETF名称(代码)} — 适合：{持有逻辑}

投资建议（基于研报逻辑）：
- 操作方向：做多 / 观望 / 规避
- 参考仓位：{轻仓/中仓/重仓}
- 时间维度：{短期(<1月) / 中期(1-3月) / 长期(>3月)}
- 风险提示：{研报中提到的主要风险}
```

> 注意：投资建议仅基于研报原文逻辑推演，不构成实际投资指导，决策前需结合个人风险偏好判断。

---

## 七、Memory 配置命令（首次使用时执行）

```
/memory set focus_market ["A股"]
/memory set watchlist_analyst ["裘翔", "李求索", "彭文生", "张夏", "张启尧", "傅静涛", "刘刚"]
/memory set watchlist_sector ["半导体", "AI大模型", "新能源", "消费", "红利", "军工"]
/memory set watchlist_index ["沪深300", "科创50", "中证红利", "中证半导体", "创业板指"]
/memory set report_push_time "每周日18:00"
/memory set output_language "简体中文"
/memory set push_channel "Telegram"
/memory set stock_filter "仅输出A股（沪深京交易所）可买标的，港股纯港股代码不列出"
```

---

## 八、完整每周 Prompt（复制进 OpenClaw 任务直接使用）

```
你是我的A股投研助手，专注中国A股资本市场（含沪市、深市、科创板、创业板）。每周日18:00执行以下任务：

【Step 1 - 拉取RSS】
从以下源拉取过去7天（168小时）内的新内容：
- https://wallstreetcn.com/rss/news
- https://rsshub.app/cls/hot
- https://rsshub.app/gelonghui/home/research
- https://rsshub.app/eastmoney/search/策略研究
- https://rsshub.app/eastmoney/search/宏观研究
- https://rsshub.app/eastmoney/search/半导体
- https://rsshub.app/eastmoney/search/大模型
- https://rsshub.app/eastmoney/search/新能源
- https://rsshub.app/eastmoney/search/消费复苏
- https://rsshub.app/eastmoney/search/红利
- https://feeds.bloomberg.com/markets/news.rss
- https://sc.macromicro.me/feed

【Step 2 - 过滤】
只保留明确涉及以下市场的内容：
A股 / 中国宏观经济 / 人民币 / 沪深300 / 北向资金

排除：纯美股个股、欧洲市场、加密货币广告类内容、纯港股个股（不含A+H两地上市股票）

【Step 3 - 参考 YouTube @oldpowerful 频道】
用 Fetch 工具抓取 https://www.youtube.com/@oldpowerful/videos 页面，
获取过去7天内发布的视频标题和链接，逐一访问视频页面提取描述文字或字幕摘要。
将该频道的核心结论/研报观点纳入本周分析，标注"（来源：@oldpowerful）"。
若过去7天无新视频，注明"本周暂无新视频发布"。

【Step 4 - 逐条处理每篇研报/文章】
对每篇研报按以下格式输出：

【研报名称】来自：{机构} | {时间}
核心观点：（2-3句话）
涉及标的（仅A股可买）：
  - A股龙头个股：{股票名称(A股代码，如688981.SH)}
  - 相关ETF（A股上市）：{ETF名称(代码)}
投资建议：操作方向 | 参考仓位 | 时间维度 | 风险提示

重要规则：所有标的只输出A股（沪深京）可买的代码，不列纯港股（.HK）代码。
若某研报涉及的标的仅有港股而无A股对应，注明"该标的暂无A股对应"，跳过不列。

【Step 5 - 汇总周报】
在所有研报处理完后，生成本周汇总：

## A股投研周报 {本周起止日期，如2026-04-28 至 2026-05-04}

### 一、本周宏观与市场环境
（过去一周影响A股的宏观要点，3-5条，每条注明来源研报名称和机构）

### 二、本周重点研报摘要
（按行业分组，每篇按Step 4格式输出）

### 三、@oldpowerful 频道本周观点
（本周该频道视频核心结论，2-3条；若无新视频则注明）

### 四、本周综合判断
**强制规则：以下每一条判断必须在括号内注明所依据的具体研报名称和出具机构，不得给出无来源的泛泛结论。格式：（依据：{研报名称}，{机构}）**

- 市场情绪：乐观 / 中性 / 谨慎（依据：{研报名称}，{机构}）
- 重点关注行业：{行业1}（依据：{研报名称}，{机构}）；{行业2}（依据：{研报名称}，{机构}）；{行业3}（依据：{研报名称}，{机构}）
- 本周值得关注的标的（仅A股可买）：
  - 龙头个股：{股票名称(A股代码)} — 逻辑：{一句话}（依据：{研报名称}，{机构}）
  - 相关ETF：{ETF名称(代码)} — 逻辑：{一句话}（依据：{研报名称}，{机构}）

若本周无足够研报支撑某行业判断，直接注明"本周暂无相关研报覆盖"，不得自行补充未经研报支持的判断。

### 五、本周相关标的参考清单（仅A股）
（汇总本周研报涉及的所有A股标的，分为"龙头个股"和"ETF"两栏，每个标的后注明来源研报机构）

【Step 6 - 推送】
通过 Telegram Bot 推送到「每周投研」频道
```

---

## 九、A股可买ETF参考库（供投资建议引用）

> 以下ETF均在沪深交易所上市，可直接用A股账户买入。
> 513180（恒生科技ETF）和513060（港股通ETF）底层资产为港股，但ETF本身在A股上市，可用人民币直接买入，纳入参考库。

```
宽基指数:
  510300 - 沪深300ETF（华泰柏瑞）
  510500 - 中证500ETF
  588000 - 科创50ETF
  159915 - 创业板ETF
  159755 - 中证A50ETF

行业ETF:
  512480 - 半导体ETF
  515230 - 新能源ETF
  159992 - 创新药ETF
  512660 - 军工ETF
  512800 - 银行ETF
  515080 - 中证红利ETF
  513180 - 恒生科技ETF（A股上市，底层港股）
  513060 - 港股通ETF（A股上市，底层港股）

主题ETF:
  516160 - 央企红利ETF
  516950 - 中证人工智能ETF
  515220 - 煤炭ETF
```

---

## 十、YouTube @oldpowerful 频道集成说明

频道地址：https://www.youtube.com/@oldpowerful

**抓取方式：**
每周日执行时，用 Fetch 工具访问该频道的视频列表页面，
提取过去7天内发布的视频标题和 URL，逐一抓取视频描述/字幕，
提取研报结论和标的观点，整合到本周周报第三节。

**集成原则：**
- 只纳入发布于过去7天内的视频内容
- 若无法抓取字幕，仅使用视频标题和描述中的信息
- 与RSS研报观点出现分歧时，两方均列出，不做强制合并
- 标注来源："（来源：YouTube @oldpowerful）"
- 若该频道提及港股标的，转化为对应A股代码后再输出；无A股对应则注明跳过

**RSS 备选：**
若 YouTube 频道有RSS，可用：
https://rsshub.app/youtube/channel/UCqpH7ehuFGRQrj6YTTWI9s
（需先通过频道页面获取 channelId）
