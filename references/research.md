# Research — the anchor ledger

Read when: a rule's rationale is challenged, an anchor must be re-verified,
or the decay watchlist is due (routed from SKILL.md Step 1).

Rules in this skill cite anchors; this ledger is where they live. Anchors are
acknowledgements, not dependencies: every rule stands on its own rationale,
and when a source dies the entry gets a replacement note, never a rule change.

URLs verified reachable: **2026-10-27** (first sweep, morning) and
**2026-10-27** (second sweep, evening — ecosystem re-scan + literature).

## Standards & prior art

| Anchor | What it grounds | URL |
|---|---|---|
| agentskills.io specification | Progressive disclosure (3 levels), frontmatter fields (`name` ≤64, `description` ≤1024, optional `license`/`compatibility` ≤500/`metadata`/`allowed-tools`), SKILL.md ≤ 500 lines / < 5000 tokens, references one level deep; official `skills-ref validate` checker | https://agentskills.io/specification |
| AGENTS.md standard | The agent-facing surface layer: README for humans, AGENTS.md for agents; 60k+ projects; nearest-file-wins monorepo nesting | https://agents.md |
| llms.txt proposal | Site-level markdown index for LLM consumption (`llms-full.txt` variant); format proposal, adoption emerging — verify currency before relying | https://llmstxt.org |
| RichardLitt/standard-readme (6.4k★) | Canonical section order; spec-style README norms | https://github.com/RichardLitt/standard-readme |
| matiassingers/awesome-readme (21.6k★) | Curated corpus behind the badge/structure rules of thumb | https://github.com/matiassingers/awesome-readme |
| anthropics/skills (184k★) | Official skill repo — no README-class skill in its directory (framework-level whitespace re-confirmed 2026-10-28) | https://github.com/anthropics/skills |
| obra/superpowers (306k★, 15 skills) | Largest community skill framework — methodology skills (TDD, debugging, plans); **no README-craft skill** (framework-level whitespace re-confirmed 2026-10-28) | https://github.com/obra/superpowers |
| addyosmani/agent-skills (111k★) | Production engineering skills (code-review/security/test/perf personas) + evals fixtures; **no README-craft skill** (framework-level whitespace re-confirmed) | https://github.com/addyosmani/agent-skills |
| Embedded README skills (red ocean, 2026-10-28) | 8152 project-local skills via code search (`filename:SKILL.md readme in:path`); sampled types: style-clone (remix-run/write-readme), multi-stage supervisor (getkyo/kyo /readme), structure template (langgraph4j/make_readme) — **zero claim-tiering / machine-gate / bilingual-discipline occurrences in the sample**; this skill's differentiation is scoped to exactly that gap | code search, ledger 4.3 |
| eli64s/readme-ai (~3k★) | Counter-example: template+LLM generation of "credible appearance" without claim management | https://github.com/eli64s/readme-ai |
| tommy0103/better-readme-skill (30★) | Nearest prior skill: cognitive-funnel audit/rewrite. Stops at structure; no claim tiers, no gates, no bilingual drift policy | https://github.com/tommy0103/better-readme-skill |
| noffle, *Art of README* | Cognitive-funnel grounding for section order. **Original repo is offline (404 as of 2026-10-27)**; an archived copy is vendored inside better-readme-skill — cite that path, not a dead link | via https://github.com/tommy0103/better-readme-skill |

## Literature

First sweep (proposal anchors):

| Paper | Grounds | Link |
|---|---|---|
| Prana et al., *Categorizing the Content of GitHub README Files*, APSEC 2018 | README content taxonomy — the structure layer's classification basis | https://arxiv.org/abs/1811.02081 |
| *An Empirical Study On Correlation between Readme Content and Project Popularity*, 2022 | README content correlates with project popularity — the "why bother" evidence | https://arxiv.org/abs/2209.01400 |
| Liu et al., *Lost in the Middle: How Language Models Use Long Contexts*, 2023 | Long-context middle-position degradation — grounds *trimming* context and keeping instructions near the edges. **It does not establish any specific file count**: the "≤ 3 references" budget below is this skill's heuristic, not a measured threshold | https://arxiv.org/abs/2307.03172 |

Second sweep (2026-10-27 evening; retrieved via arXiv API, cs.SE, sorted by
submission date — a cluster is forming around READMEs as consistency-checked,
agent-facing artifacts):

| Paper | Grounds | Link |
|---|---|---|
| READU: *Inconsistency-Driven Just-in-Time Detection and Repair of README Bugs* (Baek, Krampf, Pradel, 2026) | Academic twin of the claims probe: README defects detected against repo-internal/external sources, then auto-repaired — the probe implements the *detection* half for evidence anchors (structure + anchorability); claim-vs-code semantic consistency remains out of scope. Abstract figures (verified 2026-10-28): 6,000 recent commits across 6 popular repos (incl. Linux, Spring Boot) yielded 244 true positives at 75% precision, 217 auto-repaired; 66 README bugs reported (44 confirmed, 26 fixed); <$0.01 and <1 min per commit | https://arxiv.org/abs/2607.15780 |
| *Why Does CLAUDE.md Keep Growing? Catastrophic Remembering in Agentic Coding* (Chakrabarti, 2026) | Agent instruction files grow over their lifetime; rationale-encoding curbs bloat — grounds agent-surfaces.md rules 1–3 and the README-stays-human-shaped rule. Abstract figures (verified 2026-10-28): 1,867 repos / 247,694 instruction lifecycles; +226% growth within the lifecycle (more than triple), +4.9 net instructions/commit, deletion log-hazard −0.032/commit; prompt comments remove 99.3% of redundant instruction accrual (+211.3% → +1.4%); WildIFEval real-instruction following up to +23.1% | https://arxiv.org/abs/2608.11095 |
| *Setup Complete, Now You Are Compromised: Weaponizing Setup Instructions Against AI Coding Agents* (Bagmar, Saraf, 2026) | Setup instructions are a supply-chain attack surface — grounds the executable-trust rules in `install-one-liner.md`, `agent-surfaces.md` rule 4, and claims_probe's opt-in `--run`. Abstract (verified 2026-10-28): 12 scenarios, 5 attack classes — the abstract carries no success-rate figures | https://arxiv.org/abs/2607.15143 |
| *A Multi-Surface Consistency Audit of Software Citation Metadata* (Shan, 2026) | Multi-surface projects frequently carry core-field conflicts — grounds gate 7 and "one fact, one home". Abstract figures (verified 2026-10-28): 117 open-source research-software projects (87 HPC/quantum + 30 JOSS/pyOpenSci baseline), up to 7 surfaces each; of the 62 projects exposing ≥2 comparable surfaces, 52 (83.9%) have at least one core-field conflict; 28 of 32 CITATION.cff files with a preferred citation point to a record inconsistent with the software's own metadata; verdict precision 98.5% on a 338-row stratified human sample | https://arxiv.org/abs/2608.17159 |
| *Maintenance Signals in AI-Assisted GitHub Repositories* (Tsuchida et al., 2026) | AI-assisted repos ship longer READMEs with more headers/code blocks — supports the section cap and anti-bloat posture | arXiv API title search, same session |
| *Falsifiable Release Gates for Self-Improving Systems* (Soni, 2026) | Safety claims degrade to "a promise in a README" — grounds claim tiering as an anti-promise device | arXiv API title search, same session |

Ledger note — **verification status of the 2026 entries**: titles came from
arXiv API queries on 2026-10-27 and the numeric specifics in the summaries
("~226% growth", "83.9% of projects") came from abstract-level summaries, not
from reading the papers; a re-verification attempt that evening returned
HTTP 429 from the arXiv API. **Re-verified 2026-10-28**: a literature
reviewer pass checked all four entries that carry numeric specifics against
the papers' own arXiv abstracts (first-hand), and the table above now records
stable `arxiv.org/abs/` links with the checked figures — 226% (CLAUDE.md
growth) and 83.9% (multi-surface conflicts) are confirmed at abstract level.
The remaining two 2026 rows (Tsuchida, Soni) carry no figures; their links
are still API-search placeholders. Full-text reading remains open, so
abstract-level is the stated strength of every number here — and the
weaponization abstract gives scenario/attack counts only, no success rates.
The rules these entries inform still do not depend on the exact figures.

## Agent-infrastructure precedents (round 5.5 research pass)

Three repositories that run agent-facing infrastructure, cited as
pattern-level precedent for this round's method landings. Rights note for
every row: what is borrowed is the idea and the pattern — never expression,
code, or prose; each landing is this repo's own wording, and a landing whose
diff reproduces source text is rejected on sight. Licenses verified
2026-10-30 against each repo's GitHub metadata and (for the non-standard
license) its LICENSE file; URLs probed alive the same day.

| Anchor | Pattern this repo borrows | License (SPDX) | URL |
|---|---|---|---|
| paperclipai/paperclip | Separating "the source exists" from "the check actually ran" as distinct statuses in a closed evidence vocabulary; rule files that self-describe their trigger conditions while the root file only routes; matching changes on confusable surfaces by file path rather than by wording; bidirectional documentation-drift audit (shipped-but-undocumented, documented-as-planned) with a fix-facts-not-style patch discipline | MIT | https://github.com/paperclipai/paperclip |
| vectorize-io/hindsight | Generated artifacts re-checked by CI with a check mode that fails stale output and prints the regeneration command — structural conventions enforced by executables, not proofreading | MIT | https://github.com/vectorize-io/hindsight |
| mksglu/context-mode | The minimal evidence unit for a benchmark claim (data file plus size plus rerun command); a controlled status vocabulary over capability matrices with upstream evidence attached to each negative cell; problem → counter-example → corrected example → one-sentence rule as the anti-pattern entry shape. Source-available under a non-OSI license: ideas only are taken — no code, no text, no redistribution | Elastic-2.0 | https://github.com/mksglu/context-mode |

## Decay watchlist — what rots first, and how to notice

If this skill stops working in a year, it will most likely be one of these,
in this order. Each entry names its cheap detection probe. Items 2, 5, 6 and
8 run automatically (`.github/workflows/ecosystem-watch.yml` monthly — flagship
framework scans for README-class skills; `decay-watch.yml` weekly — live GET
probes of this repo's own bilingual pair plus a link-liveness sweep of this
ledger (`scripts/ledger_probe.py`: an HTTP >= 400 anchor red-lights,
unreachable network warns only); `validate_skill.py` in
`readme-gates.yml` on every push — spec frontmatter + body budget). The
remaining probes stay procedural on purpose: they need judgment, not
thresholds.

1. **GitHub slug & admonition rendering changes** (highest traffic, most
   silent). Our slugger approximates github-slugger; GitHub may change emoji
   handling or admonition syntax. Probe: `--selftest` catches internal
   regressions; each release, probe one real emoji-headed README against
   github.com rendering by hand.
2. **Ecosystem whitespace closes — scoped claim, three automated layers.**
   The 2026-10-28 first full code sweep **revised the claim**: embedded
   README skills are a red ocean (code search `filename:SKILL.md readme
   in:path` → total_count **8152**; sampled remix-run/write-readme
   [style-clone], getkyo/kyo [/readme supervisor], langgraph4j/make_readme
   [structure-template] — none carry claim tiers, machine gates, or
   bilingual discipline). The surviving whitespace is precisely scoped:
   **framework-level directories stay empty, and the claims-discipline +
   machine-gates route had zero occurrences in the sample.** Probe:
   **automated monthly** by `.github/workflows/ecosystem-watch.yml` —
   (a) flagship-framework + high-star skill-hub directory scan, a hit is a
   red light; (b) code-search baseline tracking against 8152 (a >50% surge
   red-lights "adoption accelerating"); (c) name/description resonance as
   WARN-only early warning.
3. **agentskills.io spec evolution.** New required frontmatter fields or a
   stricter validator would fail our SKILL.md. Probe: **mechanical half
   automated on every push** — `scripts/validate_skill.py` in CI enforces the
   2026-10-27 constraint set (name/description/license/compatibility/metadata
   rules, ≤500-line body); re-read the spec itself each release for semantic
   changes, and keep `metadata.version` current.
4. **Model-context behavior shifts.** Newer models handle long context
   better, which can turn the ≤ 3-reference budget from measurement into
   folklore. Probe: re-check the Liu et al. basis and current model cards
   each model generation; adjust the budget by evidence, not vibe.
5. **shields.io / badge host parameter drift** (`style=flat-square`,
   endpoint shapes). Probe: fetch one badge URL from `assets/after.md` each
   release; review gate 4's `BADGE_HOSTS` list yearly.
6. **Raw-URL availability & HEAD/GET behavior.** GitHub could change
   `raw.githubusercontent.com` semantics, making the GET-not-HEAD rule wrong
   or unnecessary. Probe: a `--live` run against the one-liner URL in
   `assets/after.md` each release.
7. **llms.txt adoption uncertainty.** If the proposal stalls or forks, the
   surface table in `agent-surfaces.md` needs an update — the entry already
   carries a verify-before-relying note.
8. **Ledger rot itself.** Every anchor here is dated; a dead anchor gets a
   replacement note, never a silent deletion. Probe: **automated weekly** —
   `scripts/ledger_probe.py` GETs every link in this file
   (`decay-watch.yml`); a >= 400 response is a red light, unreachable
   network warns only. The verified-dates line at the top of this file
   stays the human check for the rot a link probe cannot see.

## Instruction-craft corpus

| Anchor | What it grounds | URL |
|---|---|---|
| elder-plinius/CL4R1T4S (third-party collection, cited as instruction-craft corpus) | Writing-craft patterns only, behind this repo's instruction-layer additions: evidence-bound assertions, mode-adjudication orderings, tiered decision procedures, non-applicability boundaries stated with the tool they govern, exclusion-form completion criteria, no-process-narration report discipline. **Rights note:** the corpus is a third-party collection of AI vendors' internal instruction documents; rights remain with the original vendors. This project extracts craft patterns (structure, instruction layering and precedence, scope/boundary statements, output contracts, tone discipline) — it never quotes, closely paraphrases, or republishes corpus text; sources are cited by file path only; extraction or evasion techniques are out of scope by standing rule. Probed via `scripts/ledger_probe.py` 2026-10-29 | https://github.com/elder-plinius/CL4R1T4S |

## Rights & licensing discipline

- No third-party prose is copied into this skill. Anchors cite; they do not
  import. Any future quotation from an external work must carry its license
  note here **before** merging (the standing lesson from glasspring's
  unresolved third-party rights review).
- The instruction-craft corpus above is pattern-level study material: rules
  land here only as this project's own wording, and a landing whose diff
  reproduces corpus text is rejected on sight.
- The `assets/before.md` / `assets/after.md` pair is this method's origin
  project's own rewrite pair, desensitized to `glasswing` (provenance and
  rights note in `evals/ledger.md`); no third-party text is reproduced.
- This skill's own content: MIT, see repository `LICENSE`.

## Maintenance

When re-verifying (or when a rule is challenged):

1. Check the URL; if dead, mark the entry `[dead YYYY-MM-DD]` and look for the
   canonical successor before removing.
2. If a replacement contradicts a rule, open the change against the *rule*
   with evidence — never edit the rule silently to match a moved page.
3. Update the verified date at the top only after re-checking every row.
