# Evals ledger

Every dogfood run lands here: rubric scores, decisions, known limitations.
Started at 3 rounds (M2), following the one-concern-per-repo house tradition
of recorded rubric evaluation.

Rubric (0–3 each): **Structure** (anatomy compliance) · **Claims** (tier
discipline, no marketing) · **Gates** (doctor output) · **Reader-30s** (does
the top of the document answer Q2). Blind comparison protocol: score the
"with-skill" and "no-skill direct write" versions without knowing which is
which.

| Date | Target | Round | Structure | Claims | Gates | Reader-30s | Notes / known limitations | Decision |
|---|---|---|---|---|---|---|---|---|
| 2026-10-27 | this repo (M0+M1 scaffold) | 0 (bootstrap) | — | — | selftest 22/22 | — | gates all green on the repo's own README; real desensitized rewrite pair landed during M0 reconciliation; gate 3 gained a fixture-backed precision fix (case-only variants are one form; separators are identity) from dogfooding the real pair | scaffold accepted |
| 2026-10-28 | this repo (research iteration, v0.2) | 0.5 | — | — | selftest 27/27 | — | evening sweep: ecosystem re-verified (superpowers/addyosmani — whitespace holds); 2026 literature cluster anchored; doctor v0.2 (ref-links, setext, --json, anchor suggestions); agent-surfaces.md added; bilingual self-dogfood (README.zh-CN.md, gate 5 both ways); CI workflow | accepted |
| 2026-10-28 | agent-comparability README (mature, house-style) | 1 | 3 | 3 | before: gate 3 FAIL + 3 badge WARN → after ALL GREEN (selftest 28/28) | 3 | mode=audit-only: even a mature README hid two mechanical classes. (a) gate 3 flagged inline-code identifiers — false-positive class #2, fixed with a fixture-backed inline-code exemption (prose display name + code identifiers legitimately coexist); (b) 3 shields badges lacked flat-square — fixed in both languages. Gates 1/2/5/6 confirmed clean; no prose changes | fixes on branch `readme-anatomy/dogfood-1` (1c94269) |
| 2026-10-28 | this repo (M3 publish + scaffold) | 1.5 | — | — | CI green on main and tag v0.2.0; selftest 29/29 | — | public repo live; one-liner GET-verified (HTTP 200, 1740 bytes, tag-pinned raw INSTALL.md — no HEAD, no redirector, no circular pointer); readme_scaffold.py ships gates-clean skeletons (anchors from the doctor's own slug function); dogfood also yielded gate 5 --zh normalization (fixture-backed) | published: github.com/Rethymus/readme-anatomy |
| 2026-10-28 | external sweep (3 popular READMEs, audit-only) | 2 | — | — | 2× ALL GREEN + 1 badge-wall FAIL | — | Best-README-Template (281 ln, 7 badge-ish lines) and readme-md-generator (141 ln) ALL GREEN — no false positives observed; The-Complete-FAANG-Preparation (1966 ln, 21 badge-ish lines) caught by gate 4 badge wall. Zero text reproduced — counts and outcomes only. Calibration: gate 4 counts units on pure-badge lines (header badge-walls — the anatomy's concern) | sweep recorded, no upstream contact |
| 2026-10-28 | this repo (v0.3.0 release) | 2.5 | — | — | selftest 32/32; CI on main + tag | — | --fix mechanical repairs shipped (badge flat-square, prose-name drift; inline code spared — bracket-corruption bug caught by its own smoke test and fixed pre-release); decay-watch.yml automates watchlist items 5–6 (weekly live GET probes); CI badge added to both headers; one-liner re-pinned to v0.3.0 | published |
| 2026-10-28 | this repo (v0.3.1 — watchlist full automation) | 2.7 | — | — | selftest 32/32 + validate 11/11; CI on main + tag | — | scripts/validate_skill.py (agentskills.io frontmatter + ≤500-line body, 11 dual-anchor fixtures; parser's dead non-scalar branch caught by its own fixture and moved into the parser) wired into readme-gates CI — watchlist item 3's mechanical half automated; ecosystem-watch.yml monthly flagship-framework scan — item 2 automated. Watchlist now: 3 of 8 items on CI schedules, remainder procedural by design | published |
| 2026-10-28 | this repo (v0.7.0 -- READU-style claims probe) | 3.5 | — | — | doctor 42/42 + claims 16/16 + mcp 10/10; CI on main + tag | — | scripts/claims_probe.py verifies the evidence table's Where column against the repo: path existence, cross-file anchors (doctor's own slugger, percent-decoded), line-number ranges, commands on PATH; --run executes commands (10s timeout, exit codes) and compares a recorded output contract (`cmd -> `expected text``) against real stdout -- offline that stays WARN, since an unverified output claim is not a pass. Only known commands and .py-with-args are ever executed; unknown command words WARN instead of guessing. It certifies anchorability, not truth. Deliberately NOT gate 8: the doctor's gates apply to any README, the evidence table is this method's contract. Audit catches this round: (a) MCP selftest asserted 'own README is green', which fails every release window -- replaced with a structural assertion plus the scaffold output as the stable green anchor; (b) research overclaims corrected -- Liu 2023 grounds trimming context, NOT the <=3-reference number, and the 2026 numeric specifics (226%, 83.9%) are marked unconfirmed after a re-verification attempt returned arXiv HTTP 429; (c) an earlier ledger insertion had silently no-op'd on a stale anchor -- this row is asserted present after writing | published |
| 2026-10-28 | this repo (v0.7.1 -- evidence tables carry output contracts) | 3.7 | — | — | claims --run on both tables: 13 ref(s), 0 FAIL, 0 WARN; CI on main + tag | — | the dogfood the v0.7.0 capability was built for: every numeric claim in both evidence tables moved from the prose Notes column (human-read, rots silently) into the Where column as `cmd -> `expected output`` -- CI now executes each command and matches real stdout, so a fixture count that changes without this row turning red is impossible. Found while migrating: the zh table had already drifted (said six gates / 27 fixtures, missing the MCP and claims rows) -- bilingual content drift caught by hand during the upgrade, exactly the failure mode references/bilingual.md documents; both tables now carry identical row sets. Process note: this row was initially lost to a failed-chain release -- the release script raised StopIteration because it hand-typed the canonical origin-project name with one letter drifted (third occurrence of exactly this incident class), and the bash chain continued on newlines so v0.7.1 shipped without the row; scripts now locate anchors programmatically and fail closed | published |
| (planned) | glasspring README (upstream PR if welcomed) | 2 | | | | | dogfood on the origin project | |
| (planned) | one external open-source repo | 3 | | | | | external validity check | |

## Provenance — assets/before.md & assets/after.md

- Source: `Rethymus/glasspring` (canonical spelling; local baseline clone at
  `F:\ZCodeData\glassspring-remediation` — the double-s in that local
  directory name is a naming artifact; the path itself is real).
- `before.md` = `git show c2be2f7~1:README.zh-CN.md` (107 lines; pre-rework
  snapshot, state of 2026-10-27 20:53).
- `after.md` = `git show c2be2f7:README.zh-CN.md` (384 lines; `c2be2f7` is the
  rework commit on remote `main` — "centered header, badges, admonitions,
  TOC + FAQ, raw-URL install one-liner", PR #4, 2026-10-27 22:39).
- Desensitization: programmatic regex, glasspring name family → `glasswing`,
  author `Rethymus` → `example`; residue scan: zero hits.
- Rights: the source repo is this method's origin project (the author's own);
  no third-party text was introduced.
- Gate runs on both real trees (offline, `--name glasspring`): ALL GREEN for
  both. The gates measure mechanical integrity — the rework's gains are L1/L2
  craft (anatomy, claims posture, one-liner), which is the live demonstration
  of "gates are necessary, not sufficient".

## Spelling-scan exceptions (documented, not drift)

- `docs/PROPOSAL.md` — historical proposal text; carries a dated erratum note.
- `HANDOFF.md` — original handoff text, paths/spelling corrected in place;
  the literal local directory name `glassspring-remediation` is a real path.
- `evals/ledger.md` — this file, when citing the errata themselves.
- `scripts/readme_doctor.py`, `scripts/spelling_norm.py` — docstrings and
  selftest fixtures use `lumina-cli` / `LuminaCLI` as the separator-drift
  specimen: the detector's test name (glasswing is one word and cannot
  demonstrate separator variants), not project prose; this ledger cites the
  specimen itself when recording the exception.

Standing rules (inherited from the house engineering discipline):

- Every rule carries an anchor or is re-derivable from a script — citations
  are acknowledgements, not dependencies.
- PR red line: never loosen a gate threshold to make a document pass.
- Rights review precedes merge: third-party material needs a source and
  license note in `references/research.md` first.
