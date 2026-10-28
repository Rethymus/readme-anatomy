# Agent surfaces — README, AGENTS.md, and llms.txt (L2)

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
   their lifetime ("catastrophic remembering"; the exact rate is
   **unconfirmed** — see the ledger note in `research.md`), and that encoding
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

## What this skill gates (and doesn't)

Gate 5 covers bilingual cross-references; these surfaces add no new gate in
v0.2 — cross-surface consistency (version strings, install commands repeated
across README/AGENTS.md) is a planned M4 check. For now, when writing or
auditing any surface, run the same gates on it: it is markdown with links and
a project name, and every rule here applies verbatim.
