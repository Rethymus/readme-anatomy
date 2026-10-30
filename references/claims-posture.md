# Claims & posture — the semantic contract layer (L2)

Read when: always, before finalizing any claim, badge, or admonition (routed
from SKILL.md Step 1).

A README is a contract offered to strangers. This file defines how strongly
each sentence is allowed to assert, and which visual device carries which
semantic load.

## The three claim tiers

Every factual statement belongs to exactly one tier. Audit claim by claim;
when in doubt, downgrade.

| Tier | Definition | Allowed wording | Forbidden wording |
|---|---|---|---|
| **verified** | An evidence path exists *now*, shipped with the claim | "renders in 41±3 ms (bench: `scripts/bench.py`, last run in README of v2.3.0)" | — |
| **development-archive** | True in the repo, but not shipped, not measured, or not released with the snapshot | "`bench-mode` (development archive: unreleased, see `#214`)" — code font + explicit note | The same fact stated as present-tense product behavior |
| **marketing** | Persuasion without a verifiable referent | — | "blazingly fast", "battle-tested", "used by thousands", "enterprise-grade"; at sentence level, selling through an undisclosed "not X, but Y" contrast — comparisons belong only in the 30-second before/after table (`references/anatomy.md`) |

Rules:

- A claim's tier is a property of **the evidence, not the sentence**. Rewording
  does not upgrade a tier; shipping evidence does.
- Development-archive claims never appear in the header, the 30-second path,
  or the contrast table. The top of the document is verified-only territory.
- Numbers beat adjectives, ranges beat points, and a number with a reproducible
  path beats both ("41±3 ms, `scripts/bench.py`" not "fast").
- Negative claims sit under the same tier governance as positive ones. The
  credibility of "not X" is a property of how specific the boundary is and how
  checkable its counter-example is; a blanket denial ("not a toy, a real tool")
  has no referent and is marketing whatever its tone. Capability-limitation
  statements (partial support / client-side only / unsupported) use a
  controlled vocabulary and carry the upstream evidence path (issue, doc page,
  forum thread) under the same Where discipline as any number.

## How to place a claim

Work the four steps in order; the first match wins.

1. An evidence path exists that ships with the claim — **verified**.
2. The fact holds inside the repo but is unreleased, unmeasured, or not part
   of the shipped snapshot — **development-archive**.
3. The sentence carries a number but no path — stop and ask the author for
   the source. Placing the claim for them would be inventing evidence.
4. Nothing above applies — **marketing**; delete the sentence.

Signals, strong versus weak. Strong: a runnable path, a dated run, a number
with a range. Weak: a superlative with no named referent, an audience-size
word, a comparison with no stated baseline. Weak signals do not merely cast
doubt — they place the sentence, and the only place they reach is the
marketing tier.

When the author insists on keeping a sentence that this procedure placed at
marketing: state the three-tier system in one sentence, offer the honest
alternative (replace the adjective with a verified number), and if the
overrule stands, record it in the evals ledger like any other downgrade
overrule — the Author sign-off section below owns that path.

## Worked example: the MIT narrowing

Before (tier violation — asserts more than the license proves):

> glasswing is 100% open source under MIT.

The repo's code carries MIT; vendored assets and the `docs/` tree carry other
licenses. The sentence is falsifiable by a reader with five minutes and a
`LICENSE` listing. After (tier-correct):

> The code in `src/` is MIT-licensed; vendored assets retain their upstream
> licenses (see `NOTICE`).

This is the entire discipline in one diff: the claim shrinks until the reader
cannot falsify it. That is strength, not timidity — unfalsifiable READMEs
teach readers to discount every sentence.

## Admonition semantics

One device, one job. Mixing them is how docs start lying:

| Device | Carries exactly | Example |
|---|---|---|
| `[!IMPORTANT]` | Boundaries; necessary/sufficient conditions | "Green gates are necessary, not sufficient, for release." |
| `[!WARNING]` | Never-do; channel exclusivity (anti-impersonation) | "We will never DM you asking for keys. Release channels are exactly: GitHub Releases, npm `glasswing`." |
| `[!NOTE]` | Translation drift policy; source of truth | "English `README.md` is the source of truth; the Chinese translation may lag." |

- `[!TIP]` and `[!CAUTION]` are legal GitHub types but this method reserves
  the three above; other uses default to plain prose.
- Admonitions mark *policy*, never emphasis. If a sentence needs a box to be
  noticed, the sentence is weak or the section is too long.
- Gate 6 enforces the mechanical half (canonical set, casing); the semantic
  half is this file's job. Both are required — that is what "necessary, not
  sufficient" means in practice.

## The evidence table

Every tier-verified claim gets a row; the table lives in the Evidence section
(template: `templates/evidence-table.md`):

| Claim | Where | Status | Notes |
|---|---|---|---|
| Renders 30k-row table in 41±3 ms | `scripts/bench.py`, run logged in `docs/bench-2026-10.md` | `run-passed` | Chrome 139, M2, median of 50 |
| No runtime dependencies | `package.json` `dependencies: {}` | `run-passed` | verified at v2.3.0 |

- "Where" is a path or a command, never a URL alone — a URL is a citation,
  and **a citation is not a measurement**.
- External corroboration (papers, third-party benchmarks) goes in a separate
  row and never substitutes for a local path.
- The table is dated. Undated evidence tables rot silently.
- Absence claims are claims too. "No runtime dependencies", "works offline",
  "every link resolves" assert that a counterexample does not exist, so the
  Where cell must hold the check that would surface one (a manifest field, a
  dependency listing, a link sweep) plus the date that check was run. No
  negative row is written before its check has actually been executed — the
  "No runtime dependencies" row above earns its place by pointing at the
  manifest, not at confidence.

### The Status column — a closed vocabulary

Anchor resolvability is not claim truth. The table therefore carries a Status
column drawn from a closed five-value vocabulary, so "the check actually ran"
and "this names a sensible verification step" can never blur into each other:

| Status | Earned when |
|---|---|
| `run-passed` | the check the Where cell names was executed — here or in CI — and returned the recorded result |
| `run-failed` | the check ran and disagreed with the claim; the row is pending repair or removal |
| `blocked` | the check cannot run in this environment; the blocker is named |
| `not-run` | the check is proposed but has not been executed yet |
| `source-only` | the Where cell names where proof would live, but nothing has verified it |

Rules: a row earns a `run-*` status only when its Where check actually ran and
produced a result; anything short of that is `not-run` or `source-only`. A
`source-only` or `not-run` row cannot back a verified-tier claim — until its
check runs, the claim it supports belongs in development-archive wording or on
the task list. The claims probe reports such rows as WARN-class advisory
findings for exactly this reason: an anchor that resolves is a location, not a
verdict.

### Independence grading for external corroboration

Corroboration rows (papers, third-party benchmarks) carry an Independence
column with three graded values, and every row states its grade and the date
it was recorded:

- **author-reported** — the claim's own author measured it;
- **independently reproduced** — a third party re-ran it and published the
  result;
- **reader-rerunnable** — the reader can rerun it in place: the command and
  the data ship with the claim.

The grade is recorded, never implied — a reader deciding how far to trust a
row should not have to guess who ran it.

### Scale numbers on badges — the evidence shape

A number printed on a badge is a claim like any other. Its Where is the data
file that generates it plus the mechanism that regenerates it (a scheduled job
or a change-triggered script) — never the badge image, and never a hand-typed
or screenshotted figure. Gate 4 enforces the mechanical half for shields
dynamic/json badges aimed back at the badge's own repo: the encoded target
must resolve to an on-disk file holding valid JSON. A badge number with no
regenerating data file behind it is marketing-tier material in a verified
costume — wire it up or word it down.

## Author sign-off

The agent proposes the tier table (old wording → tier → new wording); the
author disposes. If the author overrules a downgrade, record it — the evals
ledger (`evals/ledger.md` in this skill's repo) keeps those decisions so they
are decisions, not drift.
