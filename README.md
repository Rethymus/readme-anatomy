# readme-anatomy

*A skill that turns README writing into a measurement discipline — structure, tiered claims, and machine gates.*

Can an agent prove a README tells the truth, instead of merely making it look convincing?

[![readme gates](https://github.com/Rethymus/readme-anatomy/actions/workflows/readme-gates.yml/badge.svg?style=flat-square)](https://github.com/Rethymus/readme-anatomy/actions/workflows/readme-gates.yml)

30 seconds: [Install](#3-install) · [Contrast](#2-30-second-contrast) · [Capabilities](#4-capabilities) · [Evidence](#7-evidence)

**English** | [简体中文](README.zh-CN.md)

**Contents**

1. [Why this exists](#1-why-this-exists)
2. [30-second contrast](#2-30-second-contrast)
3. [Install](#3-install)
4. [Capabilities](#4-capabilities)
5. [How it works](#5-how-it-works)
6. [Boundaries — what this skill does not do](#6-boundaries--what-this-skill-does-not-do)
7. [Evidence](#7-evidence)
8. [FAQ](#8-faq)
9. [Contributing](#9-contributing)
10. [License](#10-license)

## 1. Why this exists

LLM-assisted README generation solved blank-page problem and created a
truthfulness problem: documents that *look* credible — badge walls, confident
adjectives, tidy sections — while their claims were never classified by how
they can be verified. readme-anatomy is the opposite bet: a README is a
contract, every sentence gets a tier (verified / development-archive /
marketing-forbidden), and a machine gate fails the document when structure or
references rot. It exists as an [Agent Skill](https://agentskills.io/specification)
so any agent can run the method, not just admire it.

## 2. 30-second contrast

| Prompt-style README generation | readme-anatomy |
|---|---|
| Produces credible appearance | Forces claim tiers; marketing phrasing is deleted |
| Structure by template | Structure by anatomy + per-project-type emphasis |
| "Looks good" is the bar | `readme_doctor.py` seven gates must exit 0 |
| Bilingual by afterthought | Source-of-truth declaration + drift policy on day one |

## 3. Install

**One-liner for your agent:**

```text
Install readme-anatomy for me: https://raw.githubusercontent.com/Rethymus/readme-anatomy/v0.5.0/INSTALL.md
```

Prefer the one-liner. From a checkout:

```bash
git clone https://github.com/Rethymus/readme-anatomy.git && cd readme-anatomy
python scripts/readme_doctor.py --selftest   # expect: all green
```

Then point your agent at `SKILL.md` (see your client's skill-loading docs), or
copy the `readme-anatomy/` directory into your skills directory. Full details:
[INSTALL.md](INSTALL.md).

## 4. Capabilities

- Rewrites or audits a README through a four-question routing (project type,
  reader's 30 seconds, claim strength, bilingual policy).
- Classifies every claim into three tiers with wording patterns for each.
- Validates a README with seven offline machine gates (stdlib-only Python);
  reference-style links and setext headings parsed; optional `--live` link
  liveness using GET; `--json` report for CI and agent loops; broken anchors
  come back with nearest-slug suggestions; cross-surface consistency checked
  (one-liner origin and pin vs the git remote and latest tag, SKILL.md and
  package versions vs the tag). `--fix` repairs the mechanical classes in
  place -- including regenerating a stale table of contents from the current
  headings (idempotent: a matching TOC is left byte-identical).
- Routes every task through five modes (new / rewrite / small-edit /
  audit-only / translate) so small edits don't inherit full-ceremony cost.
- Keeps the repo's agent surfaces (AGENTS.md, llms.txt) consistent with the
  README instead of duplicating it.
- Scaffolds a gates-clean README skeleton from the four answers
  (`scripts/readme_scaffold.py` — output passes the doctor by construction),
  and carries a real before/after pair plus copy-paste templates.

## 5. How it works

The skill encodes three layers: **anatomy** (structure: header elements,
section order, TOC), **semantic contract** (claim tiers, admonition semantics,
bilingual drift policy, agent-fetchable install one-liner), and **gates**
(`scripts/readme_doctor.py`). The agent answers the four questions, reads at
most three reference files (long-context discipline, see
`references/research.md`), rewrites, then runs the gates until they pass.
Rules cite anchors; anchors never carry the rules.

## 6. Boundaries — what this skill does not do

> [!IMPORTANT]
> Green gates are a necessary condition, not a sufficient one. The doctor
> certifies checkability, not truth; claim tiers are proposed by the agent and
> signed off by the author.

- No marketing-copy generation — producing "credible appearance" is the
  anti-pattern this skill exists to counter.
- No fully automatic translation — conventions and drift policy only.
- No copying of third-party template content — anchors cite, they never import.

## 7. Evidence

| Claim | Where | Notes |
|---|---|---|
| Seven gates with dual-anchor selftest | `scripts/readme_doctor.py`, `--selftest` | each gate ships a must-fire and a must-not-fire fixture |
| Real rewrite pair, desensitized | `assets/before.md`, `assets/after.md` | origin project's pre-rework snapshot vs the rework (header/TOC/FAQ/one-liner); provenance in `evals/ledger.md` |
| Rules carry source anchors | `references/research.md` | all URLs verified 2026-10-27; decay watchlist ranks what rots first |
| Agent-surface discipline | `references/agent-surfaces.md` | grounded in the AGENTS.md standard and 2026 literature (instruction-file bloat; weaponized setup instructions) |
| Bilingual self-dogfood | `README.md` + `README.zh-CN.md`, gate 5 | this repo consumes its own bilingual gates |
| CI enforcement | `.github/workflows/readme-gates.yml` | selftest + gates on both language files on every push |
| Method grounded in prior art | `references/research.md` (literature tables) | Prana 2018; README-popularity study 2022; Liu 2023; 2026 cluster (READU, instruction bloat, setup-instruction attacks) |

## 8. FAQ

- *Why a skill and not a linter?* A linter can fail a broken anchor; it cannot
  decide that "blazingly fast" must become a tiered number or be deleted. The
  skill pairs judgment (agent + references) with enforcement (gates).
- *How is this different from readme-ai?* readme-ai generates
  credible-looking documents; readme-anatomy forces claims to be checkable.
  See `references/research.md` for the full prior-art map.
- *Does this replace AGENTS.md?* No — they are different surfaces. The README
  is for humans; `AGENTS.md` is for agents working in the repo. This skill
  keeps them consistent (one fact, one home) instead of merging them. See
  `references/agent-surfaces.md`.
- *Does it rewrite my README in place?* The agent proposes; you approve. Claim
  tiers are a proposal table until the author signs off.

## 9. Contributing

Issues and PRs welcome. The two highest-value contributions: new selftest
fixtures (a gate you can sneak a false positive past is a bug), and dogfood
reports in `evals/ledger.md`.

## 10. License

MIT — see [LICENSE](LICENSE).
