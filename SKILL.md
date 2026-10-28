---
name: readme-anatomy
description: Rewrite and audit project READMEs with a measurement-first method — centered header anatomy, tiered claims, bilingual drift policy, agent-fetchable install one-liners, and machine-checkable gates. Use whenever the user asks to write, rework, audit, or translate a README (帮我写 README、重写 README、审计 README、中英双语 README), says the README "looks AI-generated", "is sloppy", or "makes claims I can't verify", or needs badges, admonitions, a table of contents, or an install command. Covers new-write, full-rewrite, small-edit, audit-only, and translate task modes.
license: MIT
compatibility: scripts/ need Python 3.10+ (stdlib only); gates run offline by default
metadata:
  version: "0.10"
  method-origin: "distilled from the glasspring README rework (2026-10-27)"
---

# readme-anatomy — measurement-first README craft

Treat a README the way an engineer treats code: structure first, every claim
classified by how it can be verified, and a machine gate that fails loudly.
This skill does not produce "credible-looking" prose. It produces claims a
reader can check and a document `readme_doctor.py` can validate.

The method has three layers. Every task touches all three:

| Layer | Name | Governed by |
|---|---|---|
| L1 | Structure — header anatomy, section order, TOC | `references/anatomy.md` |
| L2 | Semantic contract — claim tiers, admonitions, bilingual, install line | `references/claims-posture.md`, `references/bilingual.md`, `references/install-one-liner.md` |
| L3 | Verification — seven machine gates | `scripts/readme_doctor.py` |

## Step 0 — Answer the Four Questions before writing anything

A blank agent does not lack language ability; it lacks a decision tree. These
four questions are that tree. Write the answers down — they become the final
report (Step 7).

1. **Project type** — library, CLI tool, spec, dataset, or a skill itself?
   This sets section emphasis (see the per-type table in `references/anatomy.md`).
2. **The reader's 30 seconds** — a stranger skims for one of three things:
   *what it does*, *how to install it*, *why believe it*. Which one does this
   project live or die on? That answer owns the top of the document.
3. **Claim strength** — every factual statement lands in exactly one of three
   tiers: **verified** (evidence path exists), **development-archive** (true in
   the repo but not shipped/measured — downgrade the wording), or **marketing**
   (forbidden). Audit the existing README claim by claim. See
   `references/claims-posture.md`.
4. **Language** — monolingual or bilingual? If bilingual, which file is the
   source of truth? (Unanswered, this question silently rots into drift. See
   `references/bilingual.md`.)

## Step 0a — Pick the narrowest task mode

Full ceremony on a one-line edit is how skills breed busywork. Pick the
narrowest mode that covers the request, and say which mode you picked:

| Mode | Trigger | Scope |
|---|---|---|
| **new** | No README, or a from-scratch rewrite was asked | Full Steps 1–7; generate the shape with `python scripts/readme_scaffold.py --name X --type T --lang both`, then fill every placeholder |
| **rewrite** | Existing README, user wants the method applied | Full Steps 1–7, claim-by-claim audit |
| **small-edit** | A section, badge, link, or wording fix | Touch only the affected section; re-run gates on the whole file; skip the Four Questions except the one the edit touches (usually Q3) |
| **audit-only** | "Check/audit my README" — no rewrites requested | No edits. Deliver the gate output + tier table as findings |
| **translate** | "Translate my README" / bilingual setup | Steps 4 + 6 only; read `references/bilingual.md` |

## Step 1 — Read references on demand (budget: ≤ 3 per task)

Long-context models lose information in the middle of bloated context
(Liu et al. 2023, arXiv:2307.03172 — ledger in `references/research.md`).
Read only what the Four Questions route you to:

| Read this | When |
|---|---|
| `references/anatomy.md` | Always, before restructuring or drafting sections |
| `references/claims-posture.md` | Always, before finalizing any claim, badge, or admonition |
| `references/bilingual.md` | Only when Q4 = bilingual |
| `references/install-one-liner.md` | When writing the install section of anything installable |
| `references/agent-surfaces.md` | When the repo also carries AGENTS.md or llms.txt, or the user asks what agents read |
| `references/research.md` | When a rule's rationale is challenged, an anchor must be re-verified, or the decay watchlist is due |

## Step 2 — Restructure (L1)

Apply the anatomy: centered header (title → one-line descriptor → hook
question → ≤4 badges → language switch line), a 30-second anchor path under
the header, a numbered TOC of 10–15 sections, and the canonical section order
(*why needed → contrast → install → capabilities → how it works → boundaries →
evidence → FAQ → contributing → license*). "What it does not do" and FAQ are
standalone sections, not afterthoughts. Details and per-type emphasis:
`references/anatomy.md`.

## Step 3 — Apply claims discipline (L2)

Classify every statement into the three tiers and rewrite to match the tier:
verified claims get an evidence path, development-archive claims get downgraded
wording in code font with a note, marketing phrasing gets deleted. Use
admonitions by their semantics (`[!IMPORTANT]` = boundaries and
necessary/sufficient declarations, `[!WARNING]` = never-do + channel
exclusivity, `[!NOTE]` = translation drift policy). Build the evidence table.
Full wording patterns and worked examples: `references/claims-posture.md`.

## Step 4 — Bilingual policy (only if Q4 = bilingual)

Declare the source of truth in the translation's `[!NOTE]` (see
`references/bilingual.md`), wire the bidirectional
switch line (current language bold, the other a link), and leave zero stale
cross-language references. Drift handling tiers: `references/bilingual.md`.

## Step 5 — Install one-liner (L2)

If the project is installable, the install section leads with one sentence a
human can paste to any agent and an agent can fetch directly:

```
Install <name> for me: <raw.githubusercontent.com URL>
```

The URL must be GET-fetchable (raw endpoints reject HEAD — see the gate). Local
clone paths are a fallback, never the headline. If the repo also carries
`AGENTS.md` or `llms.txt`, keep the three surfaces consistent — the README
links to them, never copies them (`references/agent-surfaces.md`). The one-liner
is executable trust: pin a tag, name the canonical host, and never let it point
anywhere but the project's own raw content. Construction and self-test:
`references/install-one-liner.md`.

## Step 6 — Run the gates (L3)

```
python scripts/readme_doctor.py <README.md> --name <canonical-name> [--zh README.zh-CN.md] [--live]
```

Hosts that speak MCP may instead wire `scripts/mcp_server.py` (stdio) and
call the `readme_doctor` tool -- same gates, same report, no shell round-trip.

After the evidence table is drafted, run the claims probe (READU-style): it
verifies every Where cell -- path existence, cross-file anchors, line-number
ranges, commands on PATH; `--run` executes commands and checks exit codes
(a trust decision). Write an output contract when the claim quotes a result:
`` `python scripts/x.py --selftest` -> `42/42 green` `` -- with `--run` the
text must appear in the output; offline it stays WARN, because an unverified
output claim is not a pass. The probe certifies that anchors *resolve*; it
does not certify the claim is true. Deliberately a separate tool, not gate 8:
the doctor's gates apply to any README, the evidence table is this method's
contract.

```
python scripts/claims_probe.py <README.md> [--run]
```

Stdlib-only, offline by default (`--live` adds real link liveness via GET).
Seven gates:

1. **anchors** — internal links resolve under GitHub slug rules (including the
   leading hyphen an emoji prefix produces, and `-1` suffixes on duplicates)
2. **links** — relative targets exist on disk; http(s) links are well-formed
   offline, alive under `--live` (GET, not HEAD)
3. **spelling** — exactly one surface form of the project name
4. **badges** — ≤ 4 badges, every badge links somewhere meaningful, shields.io
   badges use `flat-square`
5. **bilingual** — switch line bidirectional, zero stale cross-language refs,
   evidence tables in parity across languages (row counts + anchor sets)
6. **admonitions** — canonical `[!TYPE]` set, correct casing, no overuse
7. **surfaces** — cross-surface consistency: the one-liner's repo must match
   the git remote (impostor detection), its pin must not be stale, it must
   not point at the README itself, and SKILL.md/package versions must match
   the latest tag

Fix every FAIL and rerun until exit code 0 (`--fix` repairs the mechanical classes in place: TOC regeneration from current headings, badge flat-square style, drifted prose name surfaces; `--dry-run` previews the same set as a diff without writing). Every WARN needs a stated reason
to keep — write that reason into the report, do not silently ignore it.

## Step 7 — Report to the author

Deliver: (a) the Four Answers, (b) a claim-tier table (old wording → tier →
new wording), (c) the gate output. The skill proposes tiers; **the author
signs off on final claim wording**. Never publish a tier upgrade without the
evidence path to back it.

## Judgment sentences — the non-negotiables

- Gates passing is a **necessary condition, not a sufficient one**. A green
  doctor run does not certify truth; it certifies checkability.
- A citation is not a measurement. "Benchmarked in paper X" is tier
  development-archive until the benchmark runs against *this* project.
- The install one-liner must not depend on local paths. If it only works on
  the author's machine, it is not an install line.
- Marketing filler is a bug, not a style. Delete "blazingly fast", "used by
  thousands" unless a tier-verified number replaces them.
- Anchors cite, they do not depend. If an external source dies, this skill's
  rules still stand (see `references/research.md` for the ledger).
- The README is for humans; `AGENTS.md` is for agents. Merging them bloats
  both — agent instruction files measurably balloon over a project's life
  (see `references/agent-surfaces.md`).
- Admonitions are for boundaries and policies, not emphasis. Three or more of
  the same type in one document means prose failed, not that the reader needs
  a louder box.

## What this skill does not do

- No generation of marketing-style "credible appearance" — that is the
  readme-ai anti-pattern this skill exists to counter.
- No adjudicating the author's claim wording — tiers are proposed, humans
  dispose.
- No copying copyrighted template content — rules carry source anchors; they
  never lift third-party prose.
- No fully automatic translation — this skill governs bilingual *conventions
  and drift*; translation itself is the agent's general capability.
