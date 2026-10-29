<!-- 简体中文翻译 · 源文件为英文 README.md（source of truth）。
     漂移策略见文首 [!NOTE]；本文件由双语门禁（gate 5）校验。 -->

# readme-anatomy

*把 README 写作变成一门测量学科的项目 skill——结构、主张分级、机器门禁。*

> [!NOTE]
> 英文 `README.md` 是 source of truth。本翻译可能滞后；冲突时以英文版为准。最后同步：2026-10-29。

agent 能否证明一份 README 说的是真话，而不只是把它写得看起来可信？

[![readme gates](https://github.com/Rethymus/readme-anatomy/actions/workflows/readme-gates.yml/badge.svg?style=flat-square)](https://github.com/Rethymus/readme-anatomy/actions/workflows/readme-gates.yml)

30 秒：[安装](#3-安装) · [对照](#2-30-秒对照) · [能力](#4-能力) · [证据](#7-证据)

[English](README.md) | **简体中文**

**目录**

1. [为什么要有这个项目](#1-为什么要有这个项目)
2. [30 秒对照](#2-30-秒对照)
3. [安装](#3-安装)
4. [能力](#4-能力)
5. [工作原理](#5-工作原理)
6. [边界（这个 skill 不做什么）](#6-边界这个-skill-不做什么)
7. [证据](#7-证据)
8. [常见问题](#8-常见问题)
9. [参与贡献](#9-参与贡献)
10. [许可证](#10-许可证)

## 1. 为什么要有这个项目

LLM 辅助的 README 生成解决了空白页问题，却制造了真实性问题：文档*看起来*
很可信——徽章墙、自信的形容词、整齐的小节——但其中的主张从未被按"如何
验证"分类过。readme-anatomy 押相反的一注：README 是一份契约，每句话都要
归入一个层级（已验证 / 开发档案 / 禁止的营销话术），当结构或引用腐烂时，
机器门禁会让文档直接 FAIL。它以
[Agent Skill](https://agentskills.io/specification) 的形态存在，是为了让
任何 agent 都能*执行*这套方法，而不只是欣赏它。

## 2. 30 秒对照

| 提示词式 README 生成 | readme-anatomy |
|---|---|
| 产出可信的外观 | 强制主张分级；营销措辞直接删除 |
| 按模板拼结构 | 按解剖学 + 项目类型侧重排结构 |
| "看起来不错"就是标准 | `readme_doctor.py` 七项门禁必须退出码 0 |
| 双语靠事后补 | 第一天就声明 source of truth + 漂移策略 |

## 3. 安装

**给你的 agent 的一句话：**

```text
Install readme-anatomy for me: https://raw.githubusercontent.com/Rethymus/readme-anatomy/v0.11.0/INSTALL.md
```

优先用一句话。从检出版使用：

```bash
git clone https://github.com/Rethymus/readme-anatomy.git && cd readme-anatomy
python scripts/readme_doctor.py --selftest   # 预期：全绿
```

然后让 agent 读取 `SKILL.md`（见你的客户端 skill 加载文档），或把
`readme-anatomy/` 目录复制进你的 skills 目录。完整说明见
[INSTALL.md](INSTALL.md)。

## 4. 能力

- 通过四问路由（项目类型、读者的 30 秒、主张强度、双语策略）重写或审计
  README。
- 把每条主张归入三个层级，并给出各层级的措辞范式。
- 用七项离线机器门禁校验 README（仅标准库 Python）；解析引用式链接与
  setext 标题；可选 `--live` 用 GET 探活；`--json` 输出机读报告供 CI 与
  agent 循环使用；坏锚点附带最近 slug 建议；双语证据表做行集与锚集比对、跨表面一致性检查（安装
  一句话的仓库归属与 pin 对照 git remote 与最新 tag、SKILL.md 与包
  版本对照 tag）。`--fix` 原地修复机械缺陷类——含按当前标题再生过期目录
  （幂等：一致的目录字节不变）。`--dry-run` 以 unified diff 预览同一修复集而不落盘。
- 每个任务先路由到五种模式之一（新建 / 重写 / 小改 / 只审计 / 翻译），
  小改动不承担全流程成本。
- 让仓库的 agent 表面层（AGENTS.md、llms.txt）与 README 保持一致，
  而不是互相复制。
- 整条工具链以 MCP stdio 服务暴露（`scripts/mcp_server.py`——四工具、
  JSON-RPC 2.0、零 SDK 依赖），偏好原生工具调用的宿主无需绕行 shell。
- 以 READU 方式核查证据表（`scripts/claims_probe.py`）：每格“在哪”的
  路径存在、锚点可达、行号在界、命令在 PATH；`--run` 实际执行、查退出码，
  并把记录的输出口径（`命令 -> `期望文本``）与真实 stdout 比对。它认证的是
  锚点可达，不是主张为真。
- 附真实重写前后对照对（脱敏）与头部、证据表、FAQ 的即用模板。
- 发布自动化同样保持第一方：`v*` tag 推送即由 runner 自带的 `gh` CLI 发布
  GitHub Release（`--generate-notes`；`.github/workflows/release.yml`）——
  第三方 action 永远拿不到 `contents: write` 令牌（setup 指令武器化立场见
  `references/agent-surfaces.md`）。

## 5. 工作原理

这个 skill 编码了三层：**解剖学**（结构：头部要素、章节次序、目录）、
**语义契约**（主张分级、admonition 语义学、双语漂移策略、agent 可抓取的
安装一句话）、**门禁**（`scripts/readme_doctor.py`）。agent 回答四个问题，
最多读三份参考文件（长上下文纪律，见 `references/research.md`），重写，
然后跑到门禁全绿为止。规则引用锚点；锚点从不承载规则。

## 6. 边界（这个 skill 不做什么）

> [!IMPORTANT]
> 门禁全绿是必要条件，不是充分条件。doctor 认证的是"可检查性"，不是
> 真实性；主张层级由 agent 提议、由作者签字确认。

- 不生成营销文案式的"可信外观"——那是本 skill 要对抗的反模式。
- 不做全自动翻译——只管约定与漂移策略。
- 不复制第三方模板内容——锚点只引用，永不搬运。

## 7. 证据

| 主张 | 在哪 | 备注 |
|---|---|---|
| 七门禁自测全绿 | `python scripts/readme_doctor.py --selftest` -> `48/48 green` | 数量即主张：增删 fixture 不同步更新此行，CI 变红 |
| MCP 表面全绿 | `python scripts/mcp_server.py --selftest` -> `11/11 green` | 子进程握手、工具往返、协议守卫 |
| 规范校验全绿 | `python scripts/validate_skill.py --selftest` -> `11/11 green` | agentskills.io frontmatter + 行数预算 |
| 证据探针全绿 | `python scripts/claims_probe.py --selftest` -> `20/20 green` | 双锚点 fixture |
| 脚手架产物过门禁 | `python scripts/readme_scaffold.py --selftest` -> `passes the gates by construction` | 双语两文件 |
| 真实重写前后对（脱敏） | `assets/before.md`、`assets/after.md` | 起源项目重构前快照 vs 重写版；出处见 `evals/ledger.md` |
| 规则带出处锚点 | `references/research.md` | URL 已于 2026-10-27 验证；2026 数字细节已于 2026-10-28 经 arXiv 摘要（一手）确认；衰变观察哨列出最先腐烂之处 |
| agent 表面层纪律 | `references/agent-surfaces.md` | AGENTS.md 标准 + 2026 文献（方向性） |
| 双语自食其果 | `README.md` + `README.zh-CN.md`，gate 5 | 本仓库消费自己的双语门禁 |
| CI 强制执行 | `.github/workflows/readme-gates.yml` | 每次 push 跑全部自测 + 双语门禁 + claims `--run` |
| 方法有先行文献 | `references/research.md`（文献表） | Prana 2018；热度实证 2022；Liu 2023（支撑裁剪上下文，不支撑 ≤3 数字）；2026 文献簇 |

## 8. 常见问题

- *为什么是 skill 而不是 linter？* linter 能让坏锚点 FAIL，却无法判定
  "game-changing"必须改成分级的数字或删除。本 skill 把判断（agent +
  references）与强制（门禁）配对。
- *和 readme-ai 有什么不同？* readme-ai 生成可信外观的文档；readme-anatomy
  强迫主张变得可检查。完整的先行者地图见 `references/research.md`。
- *它会取代 AGENTS.md 吗？* 不会——两者是不同表面层。README 给人读；
  `AGENTS.md` 给在仓库里干活的 agent 读。本 skill 让二者保持一致
  （一个事实，一个家），而不是合并。见 `references/agent-surfaces.md`。
- *它会原地重写我的 README 吗？* agent 提议，你批准。主张分级在作者签字
  前都只是提议表。

## 9. 参与贡献

欢迎 issue 与 PR。最有价值的两类贡献：新的自测 fixture（能被你塞进假阳性
的门禁就是 bug），以及 `evals/ledger.md` 里的 dogfood 记录。

## 10. 许可证

MIT——见 [LICENSE](LICENSE)。
