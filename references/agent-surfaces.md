# Agent surfaces — README, AGENTS.md, and llms.txt (L2)

Read when: the repo also carries AGENTS.md or llms.txt, or the user asks what
agents read (routed from SKILL.md Step 1).

A repository now speaks to two audiences through different files. Confusing
them is how both documents rot: the README grows agent plumbing nobody reads,
and the agent file grows prose nobody's agent obeys.

## The three surfaces

| Surface | Audience | Carries | Canonical spec |
|---|---|---|---|
| `README.md` | Humans skimming for 30 seconds | Positioning, install, evidence, boundaries | this skill's anatomy |
| `AGENTS.md` | Coding agents working *in* the repo | Build/test commands, conventions, agent-specific context | https://agents.md (adopted by Codex, Cursor, Gemini CLI, Copilot's agent, Jules, Aider, Devin and others; 60k+ projects; nearest-file-wins, nest per package in monorepos) |
| `llms.txt` | Agents fetching a *site's* docs | A curated markdown index of doc links for LLM consumption | https://llmstxt.org (format proposal; `llms-full.txt` variant; adoption still emerging — verify before relying) |

## Rules

1. **One fact, one home.** Each fact lives in exactly one surface; the others
   link. The README's install one-liner is the single install entry — if the
   repo also has `AGENTS.md`, that file points agents at the same command
   instead of restating it. Duplicated instructions drift apart silently.
2. **The README stays human-shaped.** Don't fold agent instructions into the
   README "so everything is in one place" — that is how READMEs bloat. If the
   project needs agent behavior docs, add `AGENTS.md` and reference it from
   the README's Contributing section ("for AI agents: see `AGENTS.md`").
3. **Agent instruction files bloat measurably.** A 2026 study reports that
   agent-facing instruction files (CLAUDE.md et al.) grow substantially over
   their lifetime ("catastrophic remembering"; +226% growth within the
   lifecycle, confirmed 2026-10-28 against the paper's abstract — see the
   ledger note in `research.md`), and that encoding
   *rationale* instead of accumulating rules curbs the growth. When you touch
   an AGENTS.md, delete as often as you add, and say why a rule exists in one
   clause.
4. **Install lines are executable trust.** A 2026 security study weaponizes
   setup instructions (READMEs, Makefiles, requirements) against coding
   agents — registry redirection is rarely caught. Therefore: pin tags, never
   `main`; use the project's own canonical raw URL; prefer checksummed release
   assets for binaries; and keep the `[!WARNING]` channel-exclusivity note in
   the README so users can detect impostor instructions.
5. **Monorepos: nearest file wins.** Agents read the closest `AGENTS.md` in
   the directory tree; subpackage overrides are legitimate, root duplication
   is not. A README at the root that contradicts a package's AGENTS.md is a
   drift bug — gate 3's spelling discipline applies to all surfaces.
6. **Confusable surfaces disambiguate by path, not by wording.** When a repo
   carries several near-named surfaces (`README.md` / `README.zh-CN.md` /
   `INSTALL.md` / `AGENTS.md` / `llms.txt`), a rule about "the install doc"
   or "the agent file" is ambiguous until it names the real file path.
   Surface-affecting changes are matched by path, and rules that govern one
   surface name it — "`AGENTS.md` (repo root)" — instead of a synonym the
   next reader must guess at. Rule 1 keeps the paths from multiplying; this
   rule keeps the names from blurring.
7. **Review strength follows the change object.** Not every edit earns the
   same scrutiny; decide by what changed, not by how small the diff looks:

   | Changed object | Review strength | What must hold |
   |---|---|---|
   | The install one-liner | strict | gate 7 re-run; pin vs latest tag and origin vs git remote checked line by line; both language files agree |
   | README body prose | regular | all seven gates on the touched file and its translation pair |
   | A rule in `references/*.md` | justified | say why the rule changes; sync the SKILL.md Step 1 routing row and any `research.md` anchor the rule cited |

## What this skill gates (and doesn't)

Gate 5 covers bilingual cross-references; gate 7 covers cross-surface
consistency (the one-liner's origin and pin against the git remote and the
latest tag, SKILL.md and package versions against the tag). These surfaces
add no gate of their own: when writing or auditing any surface, run the same
gates on it — it is markdown with links and a project name, and every rule
here applies verbatim.
