<!-- Desensitized few-shot pair, "after" half: the rework that added the
     centered header, badges, admonitions, numbered TOC + FAQ, and the
     agent-fetchable install one-liner (384 lines). Provenance:
     evals/ledger.md. -->

<div align="center">

# 🎨 glasswing

**给你的 Coding Agent 装上一双「设计眼睛」——每对颜色实测对比度、31 条反 slop 扫描、六趟渲染探针，0 命中才准交付**

*A measurement-first design gate for AI coding agents.*

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE)
[![Dependencies](https://img.shields.io/badge/Dependencies-0_stdlib_only-2ea44f.svg?style=flat-square)](#-安全性)
[![Validated](https://img.shields.io/badge/Validated-34_runs-blueviolet.svg?style=flat-square)](#-验证语料)
[![For](https://img.shields.io/badge/For-AI_Coding_Agents-8957e5.svg?style=flat-square)](#-安装与快速上手)

**简体中文** | [English](README.md)

*为什么 AI 做的界面总是长着同一张脸——是模型不会设计，还是从来没人告诉过它什么是对的？*

**30 秒路径**：[安装](#-安装与快速上手) → [五秒对照](#-五秒看懂) → [它能做什么](#-它能做什么) → [验证证据](#-验证语料)

</div>

> [!IMPORTANT]
> **glasswing 是设计知识层，不是设计答案。** 它给任何能读 `.agents/skills/` 的 AI 编码代理提供四件事：路由、推导、实测、拦截。它**不是 UI 组件库**，不替代人类设计师的判断，也不承诺产出的页面「好看」。它承诺的是**可验证**：每一对颜色真的被测过对比度（WCAG + APCA 双意见）、31 条反 slop 规则 0 命中、六趟渲染探针全部通过。门禁是必要条件，不是充分条件。

> [!NOTE]
> [README.md](README.md) 是本文件的英文翻译，两版保持语义一致；skill 的 references 与工具输出以中文为准。两版如有漂移，**以中文版为源**。

---

## 目录

1. [为什么需要](#-为什么需要)
2. [五秒看懂](#-五秒看懂)
3. [安装与快速上手](#-安装与快速上手)
4. [它能做什么](#-它能做什么)
5. [内置工具](#-内置工具)
6. [它是怎么工作的](#-它是怎么工作的)
7. [设计理念](#-设计理念)
8. [装完之后怎么管理](#-装完之后怎么管理)
9. [它不做什么](#-它不做什么)
10. [验证语料](#-验证语料)
11. [安全性](#-安全性)
12. [为什么值得一个 Star](#-为什么值得一个-star)
13. [FAQ](#-faq)
14. [参与贡献](#-参与贡献)
15. [License](#-license)

---

## 🤷 为什么需要

AI Coding Agent 已经能帮你写出能跑的前端代码——但你让它"做个好看的页面"，它交回来的永远是同一张脸：

- 🎨 "帮我做个落地页" → **奶油底 + 赤陶色 + 紫色渐变 Hero**，和上一个 AI 做的页面一模一样
- 🌓 "加个暗色模式" → **直接反相**：纯白字糊在纯黑底上，看三分钟眼睛疼
- 📊 "做个后台 dashboard" → 表格数字用比例字体对不齐列，数据刷新时整页动画乱跳
- 💰 "支付页也要好看" → **金额半透明**，用户看不清自己要付多少钱就关掉了
- 📱 "小程序也要" → 照搬网页玻璃配方，**微信 webview 渲染成空白**
- ♿ "注意一下无障碍" → 引用了 WCAG 条款，但**没有一对颜色真的被测过**
- 🈶 "中文排版优化一下" → 行高 1.5 挤成一团，中西文混排没有空隙
- ✨ "再加点微交互" → **每张卡片都 scroll fade-up**，弹簧到处乱弹

这些不是 Agent 的能力问题——是**没人教过它什么是对的**。它不知道 0.72 是玻璃 tint 的可读性下限，不知道暗色模式不是反相，不知道破坏性按钮永远不该用主色。

**glasswing 把这件事变成一句话。**把下面这句发给你的 Agent——在任何项目里都能直接用，Agent 会自己抓取安装指引，不依赖任何本地路径：

```
帮我安装 glasswing：https://raw.githubusercontent.com/Example/glasswing/main/INSTALL.md
```

装好后，你说"做个落地页"，Agent 自己走四问路由、推导令牌、实测对比度、截图验证——不需要你喊"注意质量"。

### ✅ 在你用之前，你可能想知道

| | |
|---|---|
| 📏 **实测非声称** | 每对颜色跑 WCAG 对比度（玻璃按最坏合成实测）+ APCA Lc 双意见；数字全有来源台账 |
| 🚫 **反 slop 内建** | 31 条检测规则：奶油+赤陶、紫渐变、中点元数据、统一圆角+同款阴影、AI 套话词、有机 blob……0 hard 才能交付 |
| 🔬 **六趟渲染探针** | `probe_render.py`：动画守门 / t=0 冻结 / reduced-motion 契约 / axe 无障碍 / **点击指纹**（死契约与隐形态检测）/ **经济性信号**（均质间距/单侧强调）——静态扫描看不见的，渲染时全看见 |
| 🧪 **34 轮实测验证** | 14 领域包 + 12 风格包（5 包 GP 端到端转正）+ shadcn 桥接 + 真实小程序 dogfood + 冷启动隔离测试 |
| 🆚 **对照实验** | 有无 skill 四组对照 **+6/+5/+6/+4**（基线非稻草人） |
| 🤖 **兼容所有 Agent** | 任何能读 `.agents/skills/` 的 coding agent——Claude Code、ZCode、Codex CLI……装一次全项目可用 |
| 🩺 **自带体检** | `doctor.py` 一条命令：全部脚本自测 + slop 扫描 + 输出契约检查 |
| ⚖️ **法律红线内建** | 不捆绑 SF 字体、不自绘 SF Symbols、不拿"Liquid Glass"做品牌——借鉴阶梯写进宪法 |

---

## ⚡ 五秒看懂

同一份 brief，做两次。[examples/before.html](examples/before.html) 是**故意的** AI 默认款——紫色渐变 hero、三张同形卡、emoji 图标、未测量的低对比灰字（扫描器实测命中 10 warn + 1 info）。[examples/after.html](examples/after.html) 是同一 brief 的全流程交付——对比度 11/11 实测通过、扫描 0 命中、双视口目验。浏览器直开，差距自己看：

| 默认 AI 款 | glasswing 款 |
|---|---|
| ![before](docs-img/shot-pulse-before-desktop-1440x900.png) | ![after](docs-img/shot-pulse-after-desktop-1440x900.png) |

---

## 📦 安装与快速上手

把这句话发给你的 AI Agent（Claude Code、ZCode、Codex 等）：

```
帮我安装 glasswing：https://raw.githubusercontent.com/Example/glasswing/main/INSTALL.md
```

就这一步。URL 指向安装指引，Agent 抓取后自己完成剩下的事——**你不需要先克隆本仓库，也不需要知道任何路径**。

**前提只有三条：**

- 一个能读 skill 目录的 AI 编码 Agent（Claude Code、ZCode、Codex CLI……）
- 允许 Agent 执行命令（复制文件、运行安装器与自测）
- Python 3（纯 stdlib，零 pip 依赖）；Node 仅安装器需要

**升级也是同一句话**——再次发送即可，安装器以 `--replace` 覆盖旧目录并自动保留一份备份。

<details>
<summary>它会做什么？（点击展开）</summary>

1. **抓取安装指引** — 按上面的 URL 读取 INSTALL.md（含安装器用法与各宿主的目录约定）
2. **确认安装位置** — 问你要装到哪个项目、哪个宿主：Claude Code 装到 `.claude/skills/`，Codex / 通用 Agent Skills 装到 `.agents/skills/`，也可用户级全局安装
3. **运行安装器** — `install.mjs` 完整复制 skill 目录（SKILL.md、14 领域包、12 风格包、成熟库栈指引、shadcn 桥接、15 个自测工具），复制前后做字节级完整性校验，`--dry-run` 可先预览
4. **运行自测** — `doctor.py` 全绿后告诉你怎么用：对 Agent 说"帮我做个落地页"即可触发

装完之后，`doctor.py --target <目录>` 一条命令随时复查所有工具状态；想逐项核对体验，过一遍 [USER-CHECKLIST.md](USER-CHECKLIST.md)。
</details>

<details>
<summary>Agent 已经在克隆好的仓库里？（本地回退说法）</summary>

如果你的 Agent 已在本仓库的工作目录中，也可以说：

```
帮我安装 glasswing：读取当前仓库根目录的 INSTALL.md 并按步骤完成安装
```

两种说法等价；URL 版不依赖本地路径，任何场景都适用。
</details>

### 手动安装（不经过 Agent）

```bash
git clone https://github.com/Example/glasswing
node glasswing/skills/glasswing/scripts/install.mjs --target /path/to/your/project --host claude
```

`--host` 可选 `claude`（装到 `.claude/skills/`）或 `codex`（装到 `.agents/skills/`），省略则通用安装；`--dry-run` 预览，`--replace` 覆盖升级（自动留备份）。

---

## 🎯 它能做什么

**14 个领域包**，每个都是实测过的 DNA 卡——不是风格描述，是可执行的工程约束：

| 领域包 | 亮点规则 | GP 验证 |
|------|---------|--------|
| 🛒 电商零售 | 价格信任区不透明 / Baymard 费用前置 / 促销克制 | ✅ 14/14 |
| 💰 金融支付 | 金额 tabular-nums / 红色仅逾期 / 危机安全入口 | ✅ 14/14 |
| 💻 开发者工具 | mono 数据 / 玻璃永不压代码 / 复制按钮每块 | ✅ 14/14 |
| 📚 教育 | COPPA 强监管 / 儿童触控 ≥56px / 动效 1/5 | ✅ 14/14 |
| 📺 媒体内容 | 播放面暗色默认 / 正文永不半透明 / F-pattern | ✅ 14/14 |
| 👥 社交社区 | 禁强制实名 / 投票可见排序 / 永不出卖排名 | ✅ 14/14 |
| 🎮 游戏娱乐 | 60fps 预算 / HUD 四角 / 稀有度五阶 | ✅ 14/14 |
| ✈️ 旅行本地 | ETA 置信区间 / 费用不晚披露 / Peak-End | ✅ 14/14 |
| 🏥 健康健身 | 永不庆祝 normal / 危机入口常驻 / 制药 ISI | ✅ 14/14 |
| 🏛️ 政务公共 | 玻璃原则性不匹配 / 动效 0/5 / 法定无障碍 | ✅ 14/14 |
| 🏭 工业B2B | 图纸版本红线 / 零 hover 依赖 / 3m 可读 | ✅ 14/14 |
| 🔬 学术科研 | 图表即内容 / DOI 可点 / 引用不可协商 | ✅ 14/14 |
| 🏢 企业/演示 | 真实摄影 / sticky scroll-telling / 不伪造 | ✅ 14/14 |
| 📋 效率B2B | WIP 可见 / 多视图同数据 / HR 尊严约束 | ✅ 14/14 |

**12 个风格包**（用户点名即切换，★ = GP 端到端转正）：

| 风格包 | 一句话 | 适配 |
|---|---|---|
| ★ Linear 仪器盘 | 键盘优先，mono 数据，零玻璃 | devtools / B2B 深色 |
| Notion 纸感 | 灰阶层级，块编辑语法 | 文档 / 知识库 |
| 瑞士国际 | 不对称网格，红作标点 | 作品集 / 编辑 |
| 粗野主义 | 2-3px 黑边，零圆角零阴影 | 独立刊物 / 活动页 |
| 杂志编辑 | 衬线正文，hairline 节奏 | 深度内容 |
| 暗色学院 | 羊皮纸+oxblood，双线分隔 | 复古学术 |
| 有机自然 | 陶土/植物，叶形角 | 手作 / 生活方式 |
| ★ 暖软 SaaS | chunky 触觉按钮，2px+ 边框 | 习惯养成 / onboarding |
| ★ 暗色电影 | void 分层，信号色 ≤3，唯一 glow | AI / infra 营销 |
| ★ 静奢柔和 | 胶片颗粒，衬线反差，sage 双轨 | 律所 / 精品酒店 |
| ★ 柔性结构 | 巨型 grotesk，漫射影 | 设计工具 / 建筑事务所 |
| ★ 空灵玻璃 | OLED 深空，假玻璃三件套 | AI 数据平台 |

十二包同内容对照画廊见 [assets/style-gallery.html](skills/glasswing/assets/style-gallery.html)（浏览器直开）。每个风格包的玻璃判定、圆角纪律、动效预算都经跨包一致性审计。另有 **shadcn/ui 桥接**（Base UI 原语层，2026-07 起默认）与**成熟库优先栈**（shadcn + Lucide + Motion + dnd-kit + Zustand……11 库各行带库域法 + 依赖去重三查——严禁在已有依赖可表达时自行实现）。

---

## 🔧 内置工具

| 工具 | 一句话 | 亮点 |
|---|---|---|
| 🩺 `doctor.py` | 一键体检：全部脚本自测 + slop 扫描 + 输出契约 | 统一入口，一条命令全检 |
| 📊 `check_contrast.py` | WCAG 对比度 + APCA Lc 双意见 | `--pairs` 批处理 / `--tone-for` 闭式解 |
| 🌈 `palette_from_oklch.py` | 品牌色 → OKLCH 色阶重推导 | `--scaffold` 从 DNA 卡发射起跑文件 |
| 📸 `preview_shot.py` | 真 390px 视口截图 + 交互证据 | `--click` / `--probe` / `--scroll-to` / `--label` |
| 🚫 `slop_scan.py` | 31 条反 slop 规则程序化扫描 | 双锚点自测防空转 |
| 🌗 `token_emit.py` | DTCG 令牌 → CSS/Swift/Kotlin/wxss | `--wxss` 小程序 rpx 自动换算 |
| ✅ `verify_output.py` | 机械契约检查 + `--html` 验收报告 | PASS/FAIL/UNKNOWN 三态 |
| 🔧 `spring_convert.py` | SwiftUI 弹簧 ↔ CSS `linear()` 互转 | Apple 官方参数值锚定 |
| 🔬 `probe_render.py` | 六趟渲染探针（A-F + 空渲染守卫） | 点击指纹抓死契约 / axe a11y / reduce 契约 / 经济性信号 |
| 🎴 `deal_direction.py` | 方向发牌器（9+2 选 1 承诺） | `--prompt` 派生种子可复现 |
| 🚀 `run_init.py` | 一键脚手架：骨架 + tokens 占位 + notes 模板 | 骨架故意不绿（诚实起点） |
| 📝 `notes_draft.py` | design-notes 起稿：实测 §4 + 首扫 §6 + 锚点 §8 自动预填 | 判断节留待填槽，终稿仍须补全 |
| 🔍 `visual_diff.py` | 像素级截图 diff（纯 stdlib 解码 PNG） | 修复前后 `--min-diff` 必须有差（无差=没修）/ drift `--max-diff` |
| 🔌 `mcp_server.py` | 门禁 MCP 化：10 工具注册进 Claude Desktop/ZCode/Cursor | stdio JSON-RPC，结构化 JSON 返回，免 shell 引号 |
| 📸 `samples_gate.py` | 全样本回归一条命令（13+5 入口双宽度） | 豁免感知 / 网络依赖诚实 SKIP |
| 🖥️ `install.mjs` | 安装器 + 文件图完整性校验 | 排除 __pycache__ |

---

## 📐 它是怎么工作的

```
你说："做一个咖啡电商的落地页"
        │
        ▼
四问路由：什么类型？什么领域？什么平台？什么栈？
（读 ≤3 个 reference 文件——上下文经济学，长上下文降低遵循度）
        │
        ▼
令牌先行：从你的品牌色重推导 OKLCH 色阶（不抄任何现成值）
        │
        ▼
按配方构建：玻璃分级配方 / 弹簧语义预设 / CJK 排版规则 / 领域红线
        │
        ▼
实测验证：对比度批处理 + 反 slop 扫描 + 六趟渲染探针（含点击指纹）+ 真视口截图 + 输出契约
        │
        ▼
交付：tokens.css + preview.html + design-notes.md + 截图
```

Agent 读了 SKILL.md 之后自己知道该调什么工具、读哪些 reference。**不需要记命令。**

---

## 🧠 设计理念

**glasswing 是一个设计知识层（design knowledge layer），不是又一个 UI 模板。**

它比任何具体实现高一层——负责**路由、推导、验证、拒绝**，不负责底层设计本身。设计由 Agent 按 reference 规则完成，没有包装层。

你给一个新 Agent 装环境的时候，总要花时间教它什么是对的——对比度怎么测？玻璃什么时候用？破坏性按钮什么颜色？每次都要重新踩一遍。glasswing 做的事情很简单：**当下最可靠的设计规则，我们替你验证好、锚点化、写进 reference。规则过时了我们更新，你不用操心。**

### 参考文件结构

```
references/
├── tokens.md          → 令牌体系（OKLCH 色阶 / 暗色重推导阶梯）
├── type.md            → 排版（比例缩放 / CJK 规则 / RTL / Microcopy / 图片纪律）
├── layout-baselines.md → 落地页量化基线（构图/色彩/字型/动效/图像——99 SOTD 实测）
├── motion.md          → 弹簧物理（语义预设 / 可中断 / 手势同轴）
├── glass.md           → 玻璃配方（三级降级 / 决策树 / HIG 官方锚定）
├── domains/           → 14 个领域包（每个含玻璃判定/运动预算/红线）
├── recommended-stack.md → 成熟库优先栈（11 库域法 + 去重三查 + 路线判据）
├── style-packs/       → 12 个风格 DNA 卡（重推导值/规则/实测对比度）
├── platforms/         → 平台适配（shadcn 桥接 / TV / 桌面 / 移动）
└── types/             → 产品类型（中后台语法 / 原生习语 / 游戏 HUD）
```

---

## 💬 装完之后怎么管理

直接对 Agent 说大白话就行，不用记命令：

| 你说 | Agent 会做 |
|---|---|
| "帮我做个落地页 / 后台 / 小程序页面" | 触发 glasswing：路由 → 推导 → 构建 → 门禁 → 交付 |
| "检查一下这个页面的设计质量" | 跑扫描器 + 六趟渲染探针 + 对比度批处理，出报告 |
| "用 Linear 的风格做" | 读 linear-instrument 风格包，替换基调 |
| "glasswing 更新了吗？" | 重跑 `doctor.py --selftest`，全绿即就位 |
| "新起一个页面工程" | `run_init.py <目录>` 一条命令搭骨架（tokens/notes/截图目录+下一步指引） |
| "卸载 glasswing" | 列出将删除的目录清单（.agents/skills/glasswing/ + 各项目内 gp-* 样本），确认后删除，不碰其他文件 |

---

## 🚫 它不做什么

> [!WARNING]
> **glasswing 永远不会做的事：**
> - **不生成设计答案** — 它测量与拦截；设计本身仍来自你的 brief 和模型
> - **不认证「好看」** — 全部门禁 PASS 只代表可验证的底线达标，不代表会获奖（见 [FAQ](#-faq)）
> - **不联网、不上传** — 所有脚本 stdlib-only 纯本地运行，截图与报告不出本机
> - **不内嵌 Apple 专有资产** — SF 字体、SF Symbols、"Liquid Glass" 品牌词，一样都不在里面，也永远不会有

---

## 📊 验证语料

| 证据 | 在哪 |
|---|---|
| 34 轮验证导航（逐轮 RUBRIC + 已知限制；索引 30 轮，run31-34 为 dogfood/隔离/压力/多页扩展） | `evals/RESULTS-INDEX.md` |
| 有无 skill 对照实验（+6/+5/+6/+4） | `evals/results/run6-9/` |
| 真实小程序 dogfood（v2 vs v3 演进量化） | `evals/results/run30/` |
| 冷启动隔离测试（安装副本独立运行） | `evals/results/run31/` |
| 安全产品 dogfood（审计档案语法） | `evals/results/run32/` |
| 跨包冲突压力测试（FM-6 实战验证） | `evals/results/run33/` |
| 全量稳定性矩阵（30/30 零漂移） | `evals/results/n6-audit.md` |
| 外部独立佐证：StyleSeed BENCH-V1 实测裸规则不一致（Codex +1.6 / Claude Code −3.7），强制渲染→评分→修订门禁才 +5.3——与 glasswing「测量而非说教」架构同结论 | [bitjaru/styleseed](https://github.com/bitjaru/styleseed) |
| 12 包风格画廊（同内容对照，浏览器直开） | [assets/style-gallery.html](skills/glasswing/assets/style-gallery.html) |
| 多页站点三律实测（MASTER 分层/方差/token 一致） | `examples/gp-multipage-site/` |
| Agent 友好文档索引（给 Agent 读的仓库地图） | `llms.txt` |
| 全部来源台账 | `docs/SOURCES.md` |

> 注：标注为代码字体的证据文件位于开发档案，尚未随公开快照发布。


### 项目状态

| | |
|---|---|
| 验证 | 34 轮 RUBRIC 实测；全量稳定性矩阵 30/30 零漂移 |
| 工具 | 16 个，其中 15 个自带 `--selftest` |
| 运行时 | Python stdlib（零依赖）+ Node（仅安装器） |
| 文档语言 | 中文为主，[英文版](README.md)可用 |
| License | MIT |

---

## 🔒 安全性

glasswing 在设计上重视安全：

| 措施 | 说明 |
|------|------|
| 🔒 **纯本地运行** | 所有脚本 stdlib-only（零外部依赖），数据不出本机 |
| 🛡️ **默认安全** | `install.mjs` 只复制文件，不修改系统配置；不含可执行二进制 |
| 👀 **完全开源** | 代码透明，随时可审查。全部工具 stdlib Python |
| 🔍 **自测覆盖** | 每个工具带 `--selftest`（含命中锚点 + 防误报锚点）；双锚点架构防规则空转 |
| 🧩 **模块化** | 不信任某个组件？删掉对应的脚本文件即可，不影响其他 |

### 脚本安全审计

核心脚本经三面安全测试：JSON 注入（stdlib json.load 安全解析不 eval）、HTML XSS（`html.escape()` 统一转义，0 命中）、Python 代码注入（$value 按字符串处理不 eval）。**零安全漏洞**。

---

## ⭐ 为什么值得一个 Star

- **可验证**：每条规则要么有出处锚点、要么脚本能重推导——引用是致谢，不是依赖
- **实测文化**：34 轮 RUBRIC + 有无 skill 对照实验（+6/+5/+6/+4）+ 冷启动隔离测试，全部在盘可查
- **一个人也能维护**：16 个工具、15 个自带自测、全 stdlib、doctor 一条命令全检——规则过时了我们更新，你不用操心

---

## ❓ FAQ

**Q：装了 glasswing，Agent 做的页面就一定「好看」吗？**

不。glasswing 守的是**可验证的底线**，不是审美上限：对比度被实测、slop 被拦住、渲染被探针看过。好看与否仍取决于你的 brief 和模型本身的发挥——但它保证不会交付「看起来能跑」的糊弄货。

**Q：让 Agent 引用 WCAG / HIG 文档不就行了，为什么要这个？**

引用 ≠ 实测。模型会流利地引用 WCAG 1.4.3，然后交回一对从没算过对比度的灰字。glasswing 把「引用条款」变成「跑数字出报告」：每条规则要么带出处锚点、要么脚本能重推导，引用是致谢，不是依赖。

**Q：全部门禁 PASS，就等于设计正确吗？**

PASS 是**必要条件**，不是充分条件。门禁能拦住不合格的交付，拦不住平庸——0 slop 的页面也可以很无聊。反过来，FAIL 一定是真问题：不是真缺陷就是该修的漂移；双锚点自测（命中锚点 + 防误报锚点）防的就是规则空转和误报。

**Q：会拖慢 Agent 吗？和现有的 shadcn / 组件库冲突吗？**

不冲突——glasswing 本身**不是组件库**，成熟库优先栈反而严禁在已有依赖可表达时自行实现。所有工具 stdlib-only、纯本地运行，不引入任何运行时依赖；Agent 按需调工具，不改变你的构建链。

---

## 🌱 参与贡献

- **规则争议 / 误报漏报**：开 issue 并附上 `doctor.py` 的输出，定位到具体规则编号最好
- **PR 红线**：**不许为了让扫描通过而放宽规则阈值**；新增规则必须带双锚点自测（命中锚点 + 防误报锚点）
- **翻译**：[README.md](README.md) 的改进欢迎提 PR，中文版为源

---

> [!WARNING]
> **防冒名声明**：glasswing 唯一的发行渠道是本 GitHub 仓库——npm / PyPI / 网盘上任何叫 glasswing 的同名包都不是本项目。本项目没有官方代币、积分、付费群或收费版本，代码以 MIT 开源；任何以 glasswing 名义收费、募资或代运营的行为都与本项目无关，请直接举报。

## 📄 License

[MIT](LICENSE) — 设计规则与工具代码随便用；Apple 的字体、符号、商标一样都不在里面，也永远不会有。规则出处与致谢台账见 `docs/SOURCES.md`。
