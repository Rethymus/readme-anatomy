# Anatomy — the structure layer (L1)

Read when: always, before restructuring or drafting sections (routed from
SKILL.md Step 1).

Every rule here carries an anchor (ledger in `research.md`). Anchors are
acknowledgements, not dependencies: if the source dies, the rule stands and the
ledger entry gets a replacement.

## Header — five elements, centered, in this order

| # | Element | Rule |
|---|---|---|
| 1 | **Title** | The project's canonical name, exactly as gate 3 (`spelling`) enforces it. |
| 2 | **One-line descriptor** | An English descriptor phrase in italics, ≤ 120 chars: *A measurement-first design gate for AI coding agents.* It names the category and the differentiator — no adjectives that a competitor couldn't also claim. |
| 3 | **Hook question** | One open question the reader recognizes as their own: *"Can an agent prove its UI work is done, instead of asserting it?"* If no honest hook question exists, the project may not yet know its reader — surface that to the author. |
| 4 | **Badges** | ≤ 4, `flat-square` style, and each badge must link to something meaningful (CI badge → workflow runs, license badge → license file). A badge linking `#` is decoration; gate 4 fails it. |
| 5 | **Language switch line** | `**English** | [简体中文](README.zh-CN.md)` — current language bold, the other a plain link, no fragment. Only present when bilingual (see `bilingual.md`). |

## The 30-second path

Directly under the header, one line of anchor links: the three or four jumps a
skimmer needs — install → contrast → capabilities → evidence. These must match
real section anchors; the TOC and gate 1 verify them. The path answers Q2
(what the reader's 30 seconds are for); it is ordered by that answer, not by
document position.

## Table of contents

- Numbered, 10–15 sections. Fewer means the document is probably missing the
  boundaries/FAQ/evidence sections; more means sections must merge.
- Anchor links only (gate 1 enforces GitHub slug behavior — emoji-prefixed
  headings produce a **leading hyphen**, e.g. `## 🚀 Install` → `#-install`;
  duplicate headings get `-1` suffixes).
- Depth: top-level sections only. A nested TOC is a symptom of nested thinking.

## Canonical section order

1. **Why this exists** — the problem stated in the reader's terms; ends on the
   hook question's answer-in-one-paragraph.
2. **30-second contrast** — before/after or with/without table. One screen.
3. **Install** — leads with the agent-fetchable one-liner
   (`install-one-liner.md`), then human steps.
4. **Capabilities** — what it does, each capability phrased as a checkable
   statement, not a feature adjective.
5. **How it works** — the mechanism in ≥ 1 diagram or worked example; this is
   the credibility section, so it carries evidence paths.
6. **Boundaries — what it does not do** — standalone section, `[!IMPORTANT]`
   opening. Anti-feature lists prevent the wrong adopter and preempt FAQ wars;
   write them by the negative-claim rules below.
7. **Evidence** — the evidence table (`templates/evidence-table.md`): every
   tier-verified claim with its "where" column.
8. **FAQ** — standalone; every entry is a real question someone asked or will
   ask, including the hostile one — whose answer carries click-through
   evidence (see Writing negative claims below).
9. **Contributing** — the smallest honest instruction, not a template wall.
10. **License** — one line plus link; wording must match the claims tier
    (see the MIT worked example in `claims-posture.md`).

Section order rationale: problem → proof-of-relevance → action → depth →
limits → trust — mirrors the cognitive funnel readers actually descend
(category anchor: Art of README, archived copy noted in `research.md`;
taxonomy anchor: Prana et al. 2018).

## Writing negative claims (sections 6 and 8)

Boundaries and FAQ are where a project makes verifiable negative statements;
four rules govern the craft:

- Every "does not do X" binds a "does Y instead" distinction. A bare negation
  reads as modesty; the contrast is the actual information. A boundary without
  its Y-half invites the reader to conclude "no capabilities at all" — the
  mirror-image failure of overclaiming.
- FAQ answers to hostile or skeptical questions carry countable, clickable
  public evidence — a number the reader can open (a merged-PR listing, a
  release page, a benchmark log), not a slogan. Slogans answer nothing and
  read as evasion.
- Project-status content uses a three-state marker (shipped / in progress /
  not started). "Coming soon" is not a state; it is a promise without a Where.
- Anti-pattern entries can take a four-part shape: the problem, a
  counter-example, the corrected example, then the rule in one sentence. The
  rule lands last because the pair before it is what makes it believed.

## Per-type section emphasis

| Q1 answer | Heaviest sections | Note |
|---|---|---|
| Library | Capabilities, How it works, a minimal code sample per capability | API stability statement belongs in Boundaries |
| CLI tool | 30-second contrast, Install, Capabilities | The one-liner is the product's front door |
| Spec / standard | Why this exists, Boundaries, Evidence | Conformance criteria ARE the capabilities |
| Dataset | Why, Evidence, License | Provenance outranks features; license tier must be exact |
| A skill itself | Why, Capabilities, Boundaries + what it does not do | Skills are read by agents; every claim must be machine-checkable |

## Rules of thumb, each with its anchor

- Badges ≤ 4, flat-square — observed ceiling among curated top READMEs
  (`awesome-readme`); above 4 the header becomes noise.
- 10–15 sections — Standard Readme's spec section count, ± evidence/boundaries
  which that spec underspecifies.
- Numbered TOC — readers cite sections back by number ("see §6"); numbers make
  issues and chats shorter.
- Boundaries before Evidence — a reader who hits limits after trust feels
  baited; a reader who hits limits before trust feels informed.
