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
| (planned) | agent-comparability README | 1 | | | | | dogfood, full rubric + blind pair | |
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
