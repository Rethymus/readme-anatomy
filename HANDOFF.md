# 交接：readme-anatomy 项目启动（M0）

## 你是谁、在哪

你是 `readme-anatomy` 仓库的第一个开发 agent。目录刚建、完全空白（未 git init）。
使命：把一套经过实战验证的"measurement-first README 写法"固化成可安装的 Agent Skill。
唯一的立项依据是 `docs/PROPOSAL.md`——先完整读完它再动手，本文件只是执行摘要。

## 必读材料（按序，读完列出你的理解与疑问再开工）

1. **`docs/PROPOSAL.md`**（source of truth）：三层方法论（L1 结构骨架 / L2 语义契约 / L3 验证门禁）、仓库结构、M0–M4 路线图、命名依据、竞品与文献（链接已验证）
2. **`F:\ZCodeData\frontend\.agents\skills\glasspring\SKILL.md`**：工程纪律活样本——四问路由、单任务 ≤3 个 reference 的上下文预算、门禁文化、判断句措辞
3. **`F:\ZCodeData\frontend\.agents\skills\glassspring\scripts\doctor.py`** 的 `--selftest` 实现：双锚点模式（命中锚点 + 防误报锚点），M1 的 readme_doctor.py 要复刻这个模式
4. **方法论的实际产物**：https://github.com/Rethymus/glasspring 的 `README.md` 与 `README.zh-CN.md`（M3 递归自证的目标长相）；before 样本 = clone 后 `git show c2be2f7~1:README.zh-CN.md`（重写前的旧版）

## M0 任务清单（本次全部完成）

1. `git init`（默认分支 main）+ 建提案 §4 的目录骨架（SKILL.md / references×5 / assets / scripts）
2. **SKILL.md**：frontmatter 严格遵循 agentskills.io 规范——`name: readme-anatomy`（须与目录名一致）、description 按 skill-creator 指南写"pushy"触发词（列出用户会说的各种短语）；正文 = 四问路由 + 重写流程 + 门禁调用点 + "不做什么"；**≤500 行**
3. **references/anatomy.md** 与 **references/claims-posture.md**：把提案 §1 的 L1/L2 展开成可执行规则（每条规则 = 判断句 + 出处锚点）
4. **assets/before.md / after.md**：用 glasspring 重写前后样本脱敏改制（仓库名替换为虚构名），这是教空白 agent 的最强 few-shot
5. **验收**：frontmatter 校验通过（`skills-ref validate` 或等价自写校验）；SKILL.md 行数达标；全项目 `readme-anatomy` 拼写零漂移（见纪律 1）

做完 M0 停住等确认。M1（readme_doctor.py 六项门禁）不要抢跑。

## 硬纪律（前一个项目实战踩过的坑，逐条照做）

1. **拼写漂移**：生成文本里项目名会随机出现变体（glassspring 项目发生过 12 处、含死链 URL 的事故）。所有文件写完后必须用**程序构造字符串**（如 `'readme' + '-anatomy'`）做比对与规范化，禁止肉眼核对
2. **链接活性验证一律用 GET**：raw.githubusercontent.com 对 HEAD 请求返回 404 假阳性
3. **GitHub 锚点 slug 规则**：emoji 开头的标题锚点带首连字符（`#-为什么需要`）；标点（？！：，&/）删除；空格→连字符；`&` 两侧空格产生双连字符——TOC 锚点必须程序化校验，不许手写即信
4. **主张三档分级**：已验证主张（附证据路径）/ 开发档案主张（降级为代码字体 + 注记）/ 营销话术（禁用）。外部材料引用一律注明出处与许可——权利审查前置，这是 glassspring 发布流程的教训
5. **发布纪律**：不直推 main，一律 PR + CI 绿后合并；**不许为了让门禁通过而放宽规则阈值**（PR 红线）
6. 本阶段**不要**创建 GitHub 远程仓库——发布是 M3 的事，需用户授权

## 参考锚点（提案 §2 有完整链接表）

- anthropics/skills 的 `skill-creator`（官方 skill 撰写方法论：意图捕获→起草→2–3 个真实 prompt 试→迭代）
- agentskills.io/specification（frontmatter 约束、渐进披露三级、≤500 行、引用一层深）
- tommy0103/better-readme-skill（最近竞品，差异化定位见提案 §2 表格）
- arXiv:2307.03172《Lost in the Middle》（≤3 reference 预算的理论依据，写进 research.md）
