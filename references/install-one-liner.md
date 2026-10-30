# The agent-fetchable install one-liner (L2)

Read when: writing the install section of anything installable (routed from
SKILL.md Step 1).

The install section's first line is written for two readers at once: a human
who pastes it into a chat, and an agent that must act on it without any local
context. Both need the same property: the line carries everything, depends on
nothing.

## The pattern

```markdown
**One-liner for your agent:**

```text
Install glasswing for me: https://raw.githubusercontent.com/example/glasswing/v2.3.0/install.md
```
```

Rules:

- The URL is a **raw** content URL (`raw.githubusercontent.com/...`), not an
  HTML page. Agents fetch content, not chrome.
- It must be **GET-fetchable**. Raw endpoints reject `HEAD` requests — a liveness
  checker that sends HEAD reports false 404s. Gate 2's `--live` mode uses GET
  for exactly this reason; replicate that if you check by hand
  (`curl -L <url>` — never `curl -I`).
- The line names the project in its canonical spelling (gate 3) and states the
  intent ("Install X for me") so the sentence survives being pasted with no
  surrounding context.
- Local paths are the **fallback**, clearly second: "Prefer the one-liner; if
  you already have the repo: `make install`." A one-liner that only works on
  the author's machine is not a one-liner.

## Constructing the URL

| Project host | Raw pattern |
|---|---|
| GitHub file | `https://raw.githubusercontent.com/<owner>/<repo>/<ref>/<path>` |
| GitHub release asset | `https://github.com/<owner>/<repo>/releases/download/<tag>/<asset>` (asset URL, not the release page) |
| GitLab file | `https://gitlab.com/<owner>/<repo>/-/raw/<ref>/<path>` |

- Pin a **tag**, not `main` — the one-liner is quoted in issues and blogs and
  must not change meaning after the next commit.
- The target document should be self-contained install instructions (what the
  skill era's "install.md" is): dependencies, one command, a verification step.
  Pointing the one-liner at `README.md` itself is circular and therefore
  forbidden.

## Security posture — an install line is executable trust

A 2026 study ("Setup Complete, Now You Are Compromised: Weaponizing Setup
Instructions Against AI Coding Agents", anchor in `research.md`) shows setup
instructions — READMEs included — are an active supply-chain attack surface
against coding agents, and registry redirection inside them is rarely caught.
The one-liner inherits that risk, so:

- Pin a **tag**, never a branch: already a rule above, now a security rule
  too — the quoted sentence must not change meaning after the next commit.
- The URL host must be the project's **canonical** host. Keep the README's
  `[!WARNING]` channel-exclusivity note current so readers can detect impostor
  instructions claiming to be this project.
- For binaries, prefer release assets with published checksums, and have the
  one-liner's target document verify the checksum before running anything.
- Never chain a third-party redirector or URL shortener into the one-liner —
  both break provenance, and both are how redirection attacks hide.

## Self-test before publishing

1. `curl -L <url>` returns 200 with the file's bytes (not HEAD — see above).
2. Paste the sentence into a fresh agent session with no repo context; the
   agent reaches a working install without asking a clarifying question.
3. Gate 2 on the README passes with `--live`.

Step 2 is the acceptance test; steps 1 and 3 are its mechanical preconditions.
