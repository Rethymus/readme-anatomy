# CI Status — PAUSED (2026-11-16)

**GitHub Actions is disabled for this account** (billing lock reported by
GitHub: "该任务未启动，因为你的账户因账单问题已被锁定"). Per the maintainer's
decision, all GitHub Actions tasks for this project are paused until further
notice. This file is the single source of truth for that state.

## What is affected

All four workflows in `.github/workflows/`:

| Workflow | Cadence | Effect of the pause |
|---|---|---|
| readme-gates.yml | every push | no remote gate runs; verify locally instead |
| release.yml | tag push `v*` | no automatic GitHub Release creation; releases must be created manually (`gh release create <tag> --generate-notes`) or deferred |
| decay-watch.yml | weekly (Mon 04:17 UTC) | scheduled probes suspended; watchlist items 5/6 (badge URL shapes, raw-URL GET semantics) and 8 (ledger link rot, via ledger_probe) are unmonitored remotely |
| ecosystem-watch.yml | monthly (3rd 05:23 UTC) | scheduled probes suspended; watchlist item 2 (ecosystem whitespace) is unmonitored remotely |

Note: pushes to `main` and tag pushes still work as git operations; nothing
will run on the remote for them, so a push produces no CI signal at all.

## What still works (local gates are unaffected)

The whole toolchain is stdlib Python and runs offline. The remote CI was a
**mirror** of local gates, not an additional check — with one exception
(recorded below). Local acceptance for any change:

```bash
python scripts/readme_doctor.py --selftest      # 48/48
python scripts/claims_probe.py --selftest       # 20/20
python scripts/mcp_server.py --selftest         # 12/12
python scripts/validate_skill.py --selftest     # 13/13
python scripts/table_doctor.py --selftest       # 18/18
python scripts/table_doctor.py evals/ledger.md  # ledger table integrity
python scripts/ledger_probe.py references/research.md  # anchor liveness
python scripts/claims_probe.py README.md --run          # output contracts
python scripts/claims_probe.py README.zh-CN.md --run
python scripts/readme_doctor.py README.md --name readme-anatomy --zh README.zh-CN.md
```

The exception: **gate 7 (surfaces) resolves the latest tag from the local
clone**, so local runs fully cover it too. Nothing in the paused workflows
checks something the local suite cannot.

## Reactivation checklist (when the billing issue is resolved)

1. Remove the `[PAUSED ...]` header marker from each of the four workflow
   files (this commit's markers say where to cut).
2. Verify the runs come back: push a trivial commit or
   `gh workflow run decay-watch --ref main` and confirm a `schedule`/`dispatch`
   run completes success.
3. Re-verify the first scheduled fires: decay-watch Mon 04:17 UTC,
   ecosystem-watch monthly 3rd 05:23 UTC (they were never proven under real
   scheduling before the pause — see evals/ledger.md round 6.1).
4. Restore the README claims: re-add the readme-gates badge to both language
   headers, flip the "Remote CI — blocked" evidence row back to `run-passed`
   (keep EN/zh row parity — gate 5 checks it), and drop the PAUSED
   parenthetical from the release-automation bullet in both languages.
5. Delete this file (or flip it to an ACTIVE status note) in the same commit.

## Discipline during the pause

- The double gate still applies, locally: **review approval + local gate
  suite green** before any release.
- Watchlist items 2/5/6/8 lose their automation during the pause. Run the
  local equivalents by hand for any release:
  `ledger_probe` (item 8), `table_doctor` (ledger integrity), and one manual
  `gh api` spot-check of the flagship frameworks (item 2).
- Do not describe the project as "CI-verified" in any README/claim while
  paused — say "local gates verified".
