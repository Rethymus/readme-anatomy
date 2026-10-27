# Evidence table template (claims-posture.md L2)

Lives in the Evidence section. Every tier-verified claim gets one row; the
table carries a date; development-archive claims do **not** appear here.

```markdown
## Evidence

_Generated 2026-10-27 against v<version>. Re-run `scripts/verify-evidence.sh` after any release._

| Claim | Where | Notes |
|---|---|---|
| <checkable statement with number/range> | `<repo path or command>` | conditions: platform, sample size, run date |
| <second claim> | `<path>` | <scope limit> |

External corroboration (never a substitute for the local "Where" column):

| Source | What it supports | Link |
|---|---|---|
| <paper/benchmark> | <which claim, at what distance> | <url> |
```

Rules:

- "Where" is a path or command in this repo — a URL alone is a citation, and a
  citation is not a measurement.
- Numbers come with conditions (platform, sample, date) or they don't come.
- A claim that cannot fill its "Where" cell moves out of this table and into
  the development-archive wording in the body (code font + note).
