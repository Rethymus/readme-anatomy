# Installing readme-anatomy

readme-anatomy is an [Agent Skill](https://agentskills.io/specification): a
directory whose `SKILL.md` teaches your coding agent a measurement-first
README method — anatomy, tiered claims, bilingual drift policy — with six
machine gates in `scripts/`.

## Prerequisites

- Python 3.10+ (stdlib only — the gates run offline by default)
- Any agent host that loads skill directories; a plain terminal is enough to
  run the gates

## Install from a clone

```bash
git clone https://github.com/Rethymus/readme-anatomy.git
cd readme-anatomy
python scripts/readme_doctor.py --selftest   # expect: selftest 42/42 green
```

## Install into an agent host

Copy (or symlink) the whole `readme-anatomy/` directory into your host's
skills directory:

- project scope: `.agents/skills/readme-anatomy/` (Codex & friends) or
  `.claude/skills/readme-anatomy/` (Claude Code)
- user scope: `~/.agents/skills/readme-anatomy/`

Then verify the copy in place:

```bash
python <skills-dir>/readme-anatomy/scripts/readme_doctor.py --selftest
# expect: selftest 42/42 green
```

File-copy success does **not** prove your host discovers the skill — run one
real task ("audit this README") and check that the four-question routing from
`SKILL.md` shows up in the transcript. That is the acceptance test; the
selftest is its mechanical precondition.

## Generate a starting README (optional)

```bash
python scripts/readme_scaffold.py --name your-project --type cli-tool --lang both --out-dir path/to/project
```

The generated skeleton passes the gates by construction; every
`<placeholder>` in it is a claim awaiting its tier.

## Use as an MCP server (optional)

Agent hosts that speak MCP can call the toolchain natively instead of via
the shell -- no SDK dependency, newline-delimited JSON-RPC 2.0 on stdio:

```json
{ "mcpServers": { "readme-anatomy": {
    "command": "python",
    "args": ["<skills-dir>/readme-anatomy/scripts/mcp_server.py"] } } }
```

Exposes four tools: `readme_doctor` (seven gates, optional in-place fix),
`readme_scaffold` (gates-clean skeleton), `validate_skill` (spec
validation), `claims_probe` (evidence-table verification). Verify after configuring:

```bash
python <skills-dir>/readme-anatomy/scripts/mcp_server.py --selftest
# expect: selftest 10/10 green
```

## Uninstall

Delete the copied `readme-anatomy/` directory. Nothing else is written
outside it.
