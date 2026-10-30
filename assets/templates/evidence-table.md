# Evidence table template (claims-posture.md L2)

Lives in the Evidence section. Every tier-verified claim gets one row; the
table carries a date; development-archive claims do **not** appear here. The
Status column uses the closed five-value vocabulary (`run-passed` /
`run-failed` / `blocked` / `not-run` / `source-only`) — a row earns a
`run-*` status only when its Where check actually ran.

```markdown
## Evidence

_Generated 2026-10-27 against v<version>. Re-run `scripts/verify-evidence.sh` after any release._

| Claim | Where | Status | Notes |
|---|---|---|---|
| <checkable statement with number/range> | `<repo path or command>` | `run-passed` | conditions: platform, sample size, run date |
| <second claim> | `<path>` | `run-passed` | <scope limit> |

External corroboration (never a substitute for the local "Where" column; the
Independence grade is recorded, never implied):

| Source | What it supports | Independence | Link |
|---|---|---|---|
| <paper/benchmark> | <which claim, at what distance> | <author-reported / independently reproduced / reader-rerunnable> + <date recorded> | <url> |
```

Rules:

- "Where" is a path or command in this repo — a URL alone is a citation, and a
  citation is not a measurement.
- "Status" says whether the Where check actually ran: `run-passed` /
  `run-failed` only after execution; anything not yet executed is `not-run` or
  `source-only`, and such a row cannot back a verified-tier claim.
- Numbers come with conditions (platform, sample, date) or they don't come.
- Corroboration rows state their Independence grade and the date it was
  recorded.
- A claim that cannot fill its "Where" cell moves out of this table and into
  the development-archive wording in the body (code font + note).
