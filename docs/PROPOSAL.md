# 把 README 写法固化成 Agent Skill —— 编排分析与立项提案

> 状态：提案（未立项）
> 日期：2026-10-27
> 来源：对 glasspring README 重写全过程的复盘 + 竞品/文献调研（全部链接已验证）

> **勘误（2026-10-27 交接执行时补记）**：项目 canonical 名为 **`glasspring`**（glass⊕spring 共享中缀 s；GitHub 仓库 `Rethymus/glasspring`）。本文写作 `glassspring` 系拼写漂移——恰是交接硬纪律 1 要防的事故。README 重写提交 = 远程 main 尖端 `c2be2f7`（2026-10-27 22:39，PR #4），before 样本 = `c2be2f7~1:README.zh-CN.md`；该前后对已脱敏（glasspring→glasswing、Rethymus→Example）存入 `assets/before.md`、`assets/after.md`。详见 `evals/ledger.md`。

---

## 0. TL;DR 决策表

| 问题 | 结论 | 一句话理由 |
|---|---|---|
| 需要新项目吗 | **需要**，独立仓库 | 领域、受众、版本节奏、CI 门禁都与 glassspring 不同；塞进去会破坏它自己的"上下文经济学" |
| 叫什么 | **`readme-anatomy`**（skill 名）；品牌语 *Measurement-first README craft* | 命名空间几乎空白（GitHub 全站仅 3 个同名模糊命中），关键词可被 agent/人类检索到 |
| 核心定位 | 与生成器（readme-ai）和漏斗审计（better-readme-skill）互补的**第三层：结构 + 主张纪律 + 机器门禁** | 没有任何人做"README 主张的可验证性"这件事 |
| MVP 周期 | M0–M3，约一周（单人、含 dogfood） | 见 §6 路线图 |
| 最小差异化 | `readme_doctor.py` 六项机器门禁 + before/after few-shot 对照 | 规则不靠 agent 自觉，靠 FAIL 拦截 |

---

## 1. 方法论解构：这次重写到底用了什么可迁移的知识

把 glasspring 的 README 重写过程复盘，可迁移知识分三层。**这三层就是 skill 的骨架。**

### L1 结构骨架层（anatomy）

- **居中头部五要素**：标题 → 一句话定位（英文 descriptor，如 *A measurement-first design gate for AI coding agents*）→ 钩子问句（引人思考的开放式问题）→ 徽章（≤4 枚、flat-square、每枚链到有意义目标）→ 语言切换行（当前语言加粗、另一语言为链接）
- **30 秒路径**：头部下方的锚点速览（安装 → 对照 → 能力 → 证据）
- **编号目录（TOC）**：10–15 节，锚点必须程序化校验
- **章节次序**：为什么需要 → 五秒对照 → 安装 → 能力 → 原理 → 边界（不做什么）→ 证据 → FAQ → 贡献 → License
- **FAQ 与"它不做什么"独立成节**：防杠声明的正文化

### L2 语义契约层（claims & conventions）

- **Admonition 语义学**：`[!IMPORTANT]` = 边界与"必要/充分条件"声明；`[!WARNING]` = 永不做什么 + 渠道排他（防冒名）；`[!NOTE]` = 翻译漂移策略（哪个版本是 source of truth）
- **主张分级**：三档——已验证主张（有证据路径）/ 开发档案主张（未随快照发布，降级为代码字体+注记）/ 营销话术（禁用）。glasspring 重写时"MIT 全开源 → 代码以 MIT 开源"的收窄就是这一层的实操
- **安装一句话 = 可抓取 raw URL**：`帮我安装 X：<raw url>`——不依赖本地路径，任何项目里直接粘贴可用；本地路径说法降级为回退选项
- **双语约定**：`README.md` + `README.zh-CN.md`（或反向），切换行双向可达，交叉引用零残留
- **证据表**：每条主张配"在哪"一列，外部佐证单独一行

### L3 验证门禁层（gates）

1. 内链锚点校验（GitHub slug 规则模拟，含 emoji 前缀产生的首连字符）
2. 链接活性（GET 而非 HEAD——raw.githubusercontent 拒绝 HEAD 会假阳性 404）
3. 项目名拼写一致性（本 session 实证：同一文档混入两种拼法，靠肉眼不可发现，必须程序规范化）
4. 徽章数量与样式上限
5. 语言切换行双向可达 + 交叉引用无残留
6. Admonition 用法审计（IMPORTANT/WARNING/NOTE 各司其职，不混用）

---

## 2. 竞品与先行者地图（2026-10-27 全部验证）

| 项目 | 形态 | 星 | 与本 skill 的关系 |
|---|---|---|---|
| [eli64s/readme-ai](https://github.com/eli64s/readme-ai) | 独立 CLI（LLM+模板生成通用段落） | ~3k | **反向教材**：生成"看起来可信"的 README，不管理主张真实性 |
| [tommy0103/better-readme-skill](https://github.com/tommy0103/better-readme-skill) | agent skill（Art of README 认知漏斗审计/重写/翻译） | 30 | **最接近的先行者**；止步于漏斗检查，无主张分级、无门禁、无双语漂移策略 |
| [RichardLitt/standard-readme](https://github.com/RichardLitt/standard-readme) | README 规范 + linter | 6.4k | 结构层参考锚点（章节次序规范的先例） |
| [matiassingers/awesome-readme](https://github.com/matiassingers/awesome-readme) | 案例策展 | 21.6k | few-shot 素材库（好 README 的实证样本） |
| [anthropics/skills](https://github.com/anthropics/skills) | 官方 skills 仓库（19 个 skill） | 184k | **无 README 类 skill——空白确认**；skill-creator 是作者方法论来源 |
| [agentskills.io](https://agentskills.io/specification) | 开放规范 | — | 渐进披露三级、frontmatter 约束、≤500 行、引用一层深 |

注：noffle《Art of README》原文仓库已下线（404），better-readme-skill 内存有档案副本——引它时走这条注记，不要给死链。

### 文献锚点（arXiv 已验证）

- **Categorizing the Content of GitHub README Files**（Prana 等，APSEC 2018）：README 内容七大类目——结构层的分类学基础
- **An Empirical Study On Correlation between Readme Content and Project Popularity**（2022）：README 内容与项目热度正相关——"为什么值得做"的实证依据
- **Lost in the Middle: How Language Models Use Long Contexts**（Liu 等，2023，arXiv:2307.03172）：长上下文中间位置信息利用率坍塌——SKILL.md 限行、references 按需读、≤3 文件预算的理论依据

---

## 3. 需不需要新开项目？——需要，理由如下

1. **领域不同**：glasspring 是前端设计知识层（路由/令牌/对比度/渲染探针）；README 工艺是文档与主张管理。混装会让两个 skill 的 description 触发边界互相污染。
2. **glasspring 自己的宪法反对**：它的 SKILL.md 规定单任务读 ≤3 个 reference（上下文经济学）。往里面塞一个无关领域，违反它自己的设计纪律。
3. **受众不同**：README skill 服务所有仓库作者（不限前端）；glasspring 服务前端交付。
4. **CI 门禁不同**：设计 skill 的门禁是对比度/渲染探针；README skill 的门禁是锚点/链接/拼写/admonition——两套流水线，一套仓库装不下。
5. **你的仓库风格本来就是 one-concern-per-repo**（agent-comparability、glasspring、Aionis……），新项目符合既有模式。
6. **可组合而非依赖**：readme-anatomy 可以反过来给 glasspring 写 README（dogfood），但二者零依赖。

**与 glasspring 的关系声明**（写进新 README 的 Note）：哲学同源（测量而非说教、规则带锚点、门禁拦截），工程上平行。

---

## 4. 仓库与 skill 结构

```
readme-anatomy/                 # skill 名 = 目录名（规范强制）
├── SKILL.md                    # ≤500 行：四问路由 + 流程 + 门禁调用点
├── references/                 # 按需读，单文件聚焦
│   ├── anatomy.md              # L1：章节次序、头部五要素、30 秒路径、TOC 规则
│   ├── claims-posture.md       # L2：主张三档分级话术、admonition 语义学
│   ├── bilingual.md            # L2：双语约定、漂移策略、切换行规范
│   ├── install-one-liner.md    # L2：raw URL 安装语句模式 + 本地回退
│   └── research.md             # 文献/规范锚点台账（引用是锚点，不是依赖）
├── assets/
│   ├── before.md / after.md    # 同一仓库重写前后对照（最强 few-shot）
│   └── templates/              # 头部模板、证据表模板、FAQ 骨架
└── scripts/
    ├── readme_doctor.py        # 六项门禁 + --selftest（双锚点：命中 + 防误报）
    └── spelling_norm.py        # 项目名拼写规范化（构造字符串比对，不靠肉眼）
```

frontmatter（遵循 [agentskills.io](https://agentskills.io/specification)）：

```yaml
---
name: readme-anatomy
description: Rewrite and audit project READMEs with a measurement-first
  method — centered header anatomy, tiered claims, bilingual drift policy,
  agent-fetchable install one-liners, and machine-checkable gates. Use
  whenever the user asks to write, rework, translate, or audit a README,
  or says the README "looks AI-generated", "is sloppy", or needs badges,
  admonitions, a table of contents, or an install command.
---
```

（description 按 skill-creator 指南写得"pushy"——列出触发短语，防止 under-trigger。）

---

## 5. 如何让一片空白的 agent 理解这套思路

这是核心问题。答案不是"写清楚点"，而是六个机制叠加：

1. **把 tacit 判断显式化为路由问题**。空白 agent 不缺语言能力，缺的是决策树。入口就是四问（仿 glasspring 的四问路由）：
   - 这是什么类型的项目？（库 / 工具 / 规范 / 数据集 / skill 本身）
   - 读者是谁，30 秒内要得到什么？（能干什么 / 怎么装 / 信不信）
   - 主张强度是什么档？（每条陈述逐条归档到三档之一）
   - 单语还是双语？哪个是 source of truth？
2. **渐进披露控制上下文预算**：SKILL.md 只放流程与路由（<5000 tokens）；细节全部下沉 references 按需读；依据写进 research.md（Lost in the Middle）。
3. **few-shot 对照是最强教学**：assets/before.md 与 after.md 用同一仓库的真实重写（glassspring 本次改稿可作首个样本，脱敏后），让 agent "看见"差距而不是阅读形容词。
4. **每条规则带出处锚点**："徽章 ≤4"→ 热门仓库实证；"章节次序"→ Standard Readme + Prana 类目学；"≤3 reference"→ Lost in the Middle。规则因锚点而可信，锚点过时单独更新。
5. **机器门禁让 agent 自我校验**：doctor 脚本 FAIL 即改——不要求 agent "记住规范"，要求它"跑门禁"。这是与所有提示词式方案的实质区别。
6. **判断句而非形容词**：所有指导写成可执行判断（"门禁是必要条件不是充分条件""引用 ≠ 实测""安装语句不依赖本地路径"），禁止"要优雅、要清晰"式空话。

---

## 6. 具体措施：里程碑路线图

| 里程碑 | 内容 | 验收 |
|---|---|---|
| **M0**（0.5 天） | 建仓；从本提案生成 SKILL.md + anatomy.md + claims-posture.md；制作首对 before/after（glasspring 改稿脱敏版） | skills-ref validate 通过；SKILL.md ≤500 行 |
| **M1**（1 天） | `readme_doctor.py` 六项门禁 + `--selftest` 双锚点（每项门禁带命中样本与防误报样本） | selftest 全绿；对一个已知烂 README 全项 FAIL |
| **M2**（2–3 天） | 真实 dogfood：agent-comparability、glassspring、一个外部开源仓库各重写一遍；建 `evals/` 台账（仿 glasspring 的 34 轮 RUBRIC 传统，从 3 轮起步） | 每轮留 RUBRIC 评分 + 已知限制；对照"无 skill 直写"版本盲评 |
| **M3**（1 天） | 本 skill 的 README 用这套方法自己写（递归自证）+ raw URL 安装一句话 + 发布 | 门禁对自身 README 全绿；安装一句话实测可抓取 |
| **M4**（可选） | 对照实验扩展、翻译流（中↔英 drift 校验）、MCP 化门禁 | — |

**工程纪律**（从 glassspring 继承）：
- 每条规则要么带锚点、要么脚本可重推导——引用是致谢，不是依赖
- PR 红线：不许为了让门禁通过而放宽规则阈值
- 权利审查前置：references 引用外部材料注明来源与许可（吸取 glassspring 第三方材料权利审查未结的教训），避免重蹈覆辙

---

## 7. 命名分析

| 候选 | GitHub 模糊命中 | 评价 |
|---|---|---|
| **`readme-anatomy`** ✅ | 3 | 结构层直觉命名；与 references/anatomy.md 呼应；几乎无碰撞；保留 readme 关键词利于触发与检索 |
| `readme-conformance` | 13 | 强调门禁面；但 conformance 与你 agent-comparability 的品牌词重叠，易被视为衍生 |
| `readmesmith` | 3 | 工匠感；但 -smith 后缀在工具圈已泛滥 |
| `readme-contract` | 163 | 碰撞太多，弃 |
| `porchlight`（仅作仓库名/品牌名候选） | 0（与 readme 组合；单独 66 个无关域同名） | 诗意（README 是仓库为路人留的灯），符合 glassspring 式命名审美；但 skill 名仍建议带 readme 关键词 |

**推荐**：skill 名 `readme-anatomy`，仓库同名，tagline：**"Measurement-first README craft — structure, claims discipline, and machine gates."**

---

## 8. 风险与边界（写进 skill 的"不做什么"）

- 不生成营销文案式的"可信外观"（那是 readme-ai 的领地，也是反模式）
- 不替作者裁决主张口径——分级建议给出，最终署名责任在人
- 不搬运外部 README 模板的受版权内容；锚点引用注明出处
- 不做多语言全自动翻译（只管约定与漂移校验；翻译本体是 agent 的通用能力）

---

## 附：本提案的信息来源

开源：[anthropics/skills](https://github.com/anthropics/skills)（184k★，无 README skill）、[agentskills.io 规范](https://agentskills.io/specification)、[eli64s/readme-ai](https://github.com/eli64s/readme-ai)（~3k★）、[tommy0103/better-readme-skill](https://github.com/tommy0103/better-readme-skill)（★30）、[RichardLitt/standard-readme](https://github.com/RichardLitt/standard-readme)（6.4k★）、[matiassingers/awesome-readme](https://github.com/matiassingers/awesome-readme)（21.6k★）
文献：Prana 等《Categorizing the Content of GitHub README Files》(2018)；《An Empirical Study On Correlation between Readme Content and Project Popularity》(2022)；Liu 等《Lost in the Middle: How Language Models Use Long Contexts》(2023, arXiv:2307.03172)
本地方法论来源：glassspring README 重写 session（2026-10-27）、ZCode skill-creator 撰写指南、glasspring 的 SKILL.md 工程纪律
