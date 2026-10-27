# Research — the anchor ledger

Rules in this skill cite anchors; this ledger is where they live. Anchors are
acknowledgements, not dependencies: every rule stands on its own rationale,
and when a source dies the entry gets a replacement note, never a rule change.
All URLs verified reachable on **2026-10-27**.

## Standards & prior art

| Anchor | What it grounds | URL |
|---|---|---|
| agentskills.io specification | Progressive disclosure (3 levels), frontmatter constraints, SKILL.md ≤ 500 lines, references one level deep | https://agentskills.io/specification |
| RichardLitt/standard-readme (6.4k★) | Canonical section order; spec-style README norms | https://github.com/RichardLitt/standard-readme |
| matiassingers/awesome-readme (21.6k★) | Curated corpus behind the badge/structure rules of thumb | https://github.com/matiassingers/awesome-readme |
| anthropics/skills (184k★) | Official skill repo — 19 skills, **none README-related** (whitespace confirmation); skill-creator methodology informs this skill's authoring loop | https://github.com/anthropics/skills |
| eli64s/readme-ai (~3k★) | Counter-example: template+LLM generation of "credible appearance" without claim management | https://github.com/eli64s/readme-ai |
| tommy0103/better-readme-skill (30★) | Nearest prior skill: cognitive-funnel audit/rewrite. Stops at structure; no claim tiers, no gates, no bilingual drift policy | https://github.com/tommy0103/better-readme-skill |
| noffle, *Art of README* | Cognitive-funnel grounding for section order. **Original repo is offline (404 as of 2026-10-27)**; an archived copy is vendored inside better-readme-skill — cite that path, not a dead link | via https://github.com/tommy0103/better-readme-skill |

## Literature

| Paper | Grounds | Link |
|---|---|---|
| Prana et al., *Categorizing the Content of GitHub README Files*, APSEC 2018 | README content taxonomy — the structure layer's classification basis | https://arxiv.org/abs/1811.02081 |
| *An Empirical Study On Correlation between Readme Content and Project Popularity*, 2022 | README content correlates with project popularity — the "why bother" evidence | https://arxiv.org/abs/2209.01400 |
| Liu et al., *Lost in the Middle: How Language Models Use Long Contexts*, 2023 | Long-context middle-position degradation — SKILL.md line budget, ≤ 3 references per task | https://arxiv.org/abs/2307.03172 |

## Rights & licensing discipline

- No third-party prose is copied into this skill. Anchors cite; they do not
  import. Any future quotation from an external work must carry its license
  note here **before** merging (the standing lesson from glasswing's
  unresolved third-party rights review).
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
