<!-- Desensitized few-shot pair, "before" half: the pre-rework snapshot
     (107 lines). The "after" half is assets/after.md. Provenance, source
     commits, and the desensitization mapping: evals/ledger.md. -->

# glasswing

[English](README.md) · [简体中文](README.zh-CN.md)

**Glasswing 是一个面向响应式网页界面的项目级 Agent Skill。**它引导编程 Agent 新建预览、整体改版、局部 UI 修改或只读审查。对于新预览或整体改版，它会按产品类型、领域或风格、平台和技术栈路由到相关参考，再指导设计方向、令牌、实现、视口检查和定向验证。默认材质与动效指导受 Apple 启发；用户 brief 和现有设计系统优先，玻璃效果可选。

仓库遵循开放的 [Agent Skills 格式](https://agentskills.io/specification)。该格式规定宿主激活 Skill 时会加载完整的 `SKILL.md`；之后 Glasswing 才要求 Agent 阅读不超过三份核心设计参考，具体任务指南和平台适配文件可能增加阅读量。这是路由要求，不代表已经测得 token 节省或效果提升；不同宿主的加载行为尚未全面验证。参考内容是静态文件；Glasswing 不会浏览真实产品并自动生成参考卡片。原生 App、游戏和小程序的代码交付不在已验证范围内。

## 什么时候用 Glasswing

- "帮我做一个响应式页面 / 后台 / 落地页"——新建预览。
- "把这个应用重新设计一遍"——整体改版，沿用现有令牌体系。
- "小修一处 UI"——在现有体系内改动。
- "看看这个页面的设计"——只读审查。

Glasswing 不交付原生 App、游戏或小程序的代码；其平台类参考文件仅可作为网页预览的参考。

> **公开源码预览 · 稳定版 BLOCKED。** 保留的第三方材料尚未完成来源与再分发权利审查。再次分发源码或安装副本前，请阅读[发布门槛](docs/RELEASE-GATES.md)和[第三方声明](THIRD_PARTY_NOTICES.md)。

## 咖啡售卖页示例

这是人工整理的示例，展示响应式页面和仅在本地生效的购物袋交互。示例 brief 指定了奶油色、浓咖啡色和陶土色；当前页面选择了分栏主视觉和三张商品卡。它不是全新 Agent 宿主会话的运行结果，也不能证明 Glasswing 会提升设计效果。[设计说明](examples/coffee-storefront/design-notes.md)记录了路由选择和检查结果。

<p align="center"><img src="examples/coffee-storefront/shots/coffee-storefront-desktop.png" alt="虚构的 Morrow Coffee 售卖页桌面全页截图。" width="100%"><br>1440px 桌面页面</p>

<p align="center"><img src="examples/coffee-storefront/interaction.gif" alt="本地交互：初始页面、加入 House Blend、打开购物袋、增加数量，再移除商品。" width="100%"><br>本地购物袋交互</p>

<details>
  <summary>移动端布局和打开的购物袋</summary>
  <p align="center"><img src="examples/coffee-storefront/shots/coffee-storefront-mobile.png" alt="虚构的 Morrow Coffee 售卖页移动端全页截图。" width="320"></p>
  <p align="center"><img src="examples/coffee-storefront/shots/coffee-storefront-bag-open.png" alt="已打开的购物袋，包含两件 House Blend、小计 36 美元和本地演示说明。" width="100%"></p>
</details>

仅针对这个示例：输出契约 **6/6 条款 PASS**、**7 组指定对比度 PASS**、Playwright 购物袋交互冒烟检查 **PASS**、样式扫描 **0 条发现**。渲染探测为 **UNKNOWN**（退出码 2）；axe 覆盖为 **NOT_RUN**。这些结果不能证明完全符合 WCAG、整体视觉质量或 Skill 的效果提升。

在仓库根目录启动页面：

~~~sh
python -m http.server 8000 --directory examples/coffee-storefront
~~~

访问 <http://127.0.0.1:8000/preview.html>。可查看[预览源码](examples/coffee-storefront/preview.html)、[设计令牌](examples/coffee-storefront/tokens.css)和[完整检查记录](examples/coffee-storefront/design-notes.md)。

## 安装和试用

请克隆仓库，并先安装到一次性项目。安装器使用 Node.js，辅助工具使用 Python。记录中的检查使用 Node.js 22.14 和 Python 3.12；这两者是已测试版本，不是声明的最低版本要求。

~~~sh
git clone https://github.com/Example/glasswing.git
cd glasswing
node skills/glasswing/scripts/install.mjs --target "PATH_TO_PROJECT" --host codex --dry-run
node skills/glasswing/scripts/install.mjs --target "PATH_TO_PROJECT" --host codex
~~~

请将 `PATH_TO_PROJECT` 替换为当前终端可用的路径。安装到 Claude Code 项目时使用 `--host claude`。安装器会将 Skill 和参考文件复制到 `.agents/skills/glasswing` 或 `.claude/skills/glasswing`；文件复制成功不能证明宿主会发现或遵循 Skill。备份、移除和当前宿主证据见[安装与宿主验证](INSTALL.md)。

安装后，在新的编程 Agent 会话中试试：

~~~text
使用 Glasswing 为虚构品牌 Morrow Coffee 制作响应式售卖页。配色使用暖奶油色（#f8f3eb）、浓咖啡色文字（#35221b）和陶土色按钮（#93432d）。包含主视觉、三张商品卡，以及可用键盘操作的本地购物袋；加购和移除商品时更新数量与小计，不做结账或支付。使用目标项目已有素材；若缺少商品图片，请用 CSS 或内联 SVG 绘制简单插图，不下载外部素材。交付 tokens.css、preview.html 和 design-notes.md。检查 390px 和 1440px 布局，将移动端和桌面 PNG 截图保存到 shots/，并报告无法执行的检查。
~~~

这是一条示例请求，不是已记录的宿主运行或基准评测结果。

## 任务模式和工具

| 任务 | Skill 会如何指导 |
|---|---|
| 新建预览 | 提出三个设计方向，创建语义化令牌、独立页面、设计说明和窄屏/桌面截图；新预览输出契约只适用于此模式。 |
| 整体改版 | 在现有应用和令牌系统内修改，并记录修改前后的证据。 |
| 局部 UI 修改 | 保留现有系统，并按改动范围做相称检查。 |
| 只读审查 | 检查并报告，不编辑项目文件。 |

仓库包含 `SKILL.md` 工作流、静态参考、辅助脚本和可选的 stdio MCP 服务器。参考内容用于指导，不是复制特定产品界面或素材的指令。MCP 需要手动配置，尚未验证生产宿主集成。浏览器探针需要 Chromium；可选 axe 检查会从 CDN 获取 axe-core 4.10.2。工具以调用者权限运行，不是沙箱；浏览器检查可能执行目标页面代码。详见[安全说明](SECURITY.md)。

## 当前证据与限制

证据快照日期：**2026-10-26**。仓库自检用于检查包和辅助工具，不评定 Agent 生成的设计。

~~~sh
python -m unittest discover -s tests -v
node skills/glasswing/scripts/install.mjs --selftest
python skills/glasswing/scripts/verify_output.py --selftest
python skills/glasswing/scripts/mcp_server.py --selftest
~~~

| 范围 | 已记录状态 |
|---|---|
| 安装器文件复制 | Windows、macOS、Linux CI 中 **PASS**；宿主发现和任务行为需要单独验证。 |
| Codex 宿主 | Skill 元数据可见性 **PASS**；读取安装后的文件和任务行为 **UNKNOWN**。 |
| Claude Code 宿主 | 全新会话发现和任务行为 **NOT_RUN**；其他宿主 **NOT_RUN**。 |
| 历史完整样本审计 | **FAIL / INCOMPLETE**：12 项 `PASS`、1 项真实对比度 `FAIL`、1 项预期负向对照、2 项 `SKIP`；历史输入未包含在本仓库中。 |
| 独立效果比较 | **NOT_RUN**。公开试点不是隐藏留出集；缺少两个任务输入，也没有分别衡量视觉差异度、token 成本或 Skill 使用覆盖。 |
| 隐私审查 | **PARTIAL**：仅完成启发式文本扫描；未运行专用密钥扫描，也未完整检查二进制文件和 Git 历史。 |
| 浏览器依赖完整性 | **OPEN**：axe-core 从 CDN 获取，尚无固定完整性校验值或离线覆盖策略。 |
| 来源与第三方权利 | **BLOCKED**，直至完成保留材料的来源和再分发义务审查。 |

详细证据和解除条件见[发布门槛](docs/RELEASE-GATES.md)、[评测说明](docs/EVALUATION.md)、[公开试点评测协议](evals/protocol.json)、[来源说明](PROVENANCE.md)和[第三方声明](THIRD_PARTY_NOTICES.md)。目前没有证据证明 Glasswing 提升整体设计质量、适用于所有 Agent 宿主或完全符合 WCAG。

## 许可证和项目结构

仓库包含 [MIT 许可证](LICENSE)，但该许可证不授予贡献者无权授权的第三方材料。请查看[第三方声明](THIRD_PARTY_NOTICES.md)；权利门槛解除前，稳定版仍为 **BLOCKED**。“受 Apple 启发”仅说明一种视觉起点，不代表与 Apple 存在关联。

- [可安装的 Skill](skills/glasswing/)：工作流、路由参考、脚本和模板。
- [咖啡售卖页](examples/coffee-storefront/)：人工整理的示例及其证据记录。
- [架构](docs/ARCHITECTURE.md)、[评测](docs/EVALUATION.md)和[发布门槛](docs/RELEASE-GATES.md)。
- [贡献指南](CONTRIBUTING.md)、[安全说明](SECURITY.md)、[来源说明](PROVENANCE.md)和[第三方声明](THIRD_PARTY_NOTICES.md)。
