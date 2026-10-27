# Claims & posture — the semantic contract layer (L2)

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
| **marketing** | Persuasion without a verifiable referent | — | "blazingly fast", "battle-tested", "used by thousands", "enterprise-grade" |

Rules:

- A claim's tier is a property of **the evidence, not the sentence**. Rewording
  does not upgrade a tier; shipping evidence does.
- Development-archive claims never appear in the header, the 30-second path,
  or the contrast table. The top of the document is verified-only territory.
- Numbers beat adjectives, ranges beat points, and a number with a reproducible
  path beats both ("41±3 ms, `scripts/bench.py`" not "fast").

## Worked example: the MIT narrowing

Before (tier violation — asserts more than the license proves):

> lumina is 100% open source under MIT.

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
| `[!WARNING]` | Never-do; channel exclusivity (anti-impersonation) | "We will never DM you asking for keys. Release channels are exactly: GitHub Releases, npm `lumina`." |
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

| Claim | Where | Notes |
|---|---|---|
| Renders 30k-row table in 41±3 ms | `scripts/bench.py`, run logged in `docs/bench-2026-10.md` | Chrome 139, M2, median of 50 |
| No runtime dependencies | `package.json` `dependencies: {}` | verified at v2.3.0 |

- "Where" is a path or a command, never a URL alone — a URL is a citation,
  and **a citation is not a measurement**.
- External corroboration (papers, third-party benchmarks) goes in a separate
  row and never substitutes for a local path.
- The table is dated. Undated evidence tables rot silently.

## Author sign-off

The agent proposes the tier table (old wording → tier → new wording); the
author disposes. If the author overrules a downgrade, record it — the evals
ledger (`evals/ledger.md` in this skill's repo) keeps those decisions so they
are decisions, not drift.
