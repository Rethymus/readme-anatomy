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
| 2026-10-27 | this repo (M0 scaffold) | 0 (bootstrap) | — | — | selftest pending | — | sample before/after pair is fictional composite; real desensitized glassspring pair lands in M2 | scaffold accepted |
| (planned) | agent-comparability README | 1 | | | | | dogfood, full rubric + blind pair | |
| (planned) | glassspring README | 2 | | | | | dogfood; replaces sample pair with desensitized real pair | |
| (planned) | one external open-source repo | 3 | | | | | external validity check; PR upstream if welcomed | |

Standing rules (inherited from the house engineering discipline):

- Every rule carries an anchor or is re-derivable from a script — citations
  are acknowledgements, not dependencies.
- PR red line: never loosen a gate threshold to make a document pass.
- Rights review precedes merge: third-party material needs a source and
  license note in `references/research.md` first.
