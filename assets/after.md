<!--
Few-shot sample (the "after" half). Same fictional project as before.md,
rewritten per this skill's method. Intentionly PASSES all offline gates:
run scripts/readme_doctor.py --name lumina-cli against it. Replaced by the
desensitized glassspring rewrite pair in M2.
-->

# lumina-cli

*A single-binary design-token converter that answers one question: what will my tokens actually render as?*

Can your design tokens survive the trip from Figma to production without a human checking every platform by hand?

[![CI](https://github.com/example/lumina/actions/workflows/ci.yml/badge.svg?style=flat-square)](https://github.com/example/lumina/actions/workflows/ci.yml)
[![License](https://img.shields.io/github/license/example/lumina?style=flat-square)](https://github.com/example/lumina/blob/main/LICENSE)
[![Release](https://img.shields.io/github/v/tag/example/lumina?style=flat-square)](https://github.com/example/lumina/releases)

30 seconds: [Install](#2-install) · [Contrast](#3-30-second-contrast) · [Capabilities](#4-capabilities) · [Evidence](#7-evidence)

**Contents**

1. [Why this exists](#1-why-this-exists)
2. [Install](#2-install)
3. [30-second contrast](#3-30-second-contrast)
4. [Capabilities](#4-capabilities)
5. [How it works](#5-how-it-works)
6. [Boundaries — what lumina-cli does not do](#6-boundaries--what-lumina-cli-does-not-do)
7. [Evidence](#7-evidence)
8. [FAQ](#8-faq)
9. [Contributing](#9-contributing)
10. [License](#10-license)

## 1. Why this exists

Design tokens rot in transit: a color defined once in Figma arrives as three
slightly different values on web, iOS, and Android, and nothing fails loudly —
a human just notices eventually. lumina-cli converts token sources into
platform outputs and reports every value that changed in transit, so "same
color everywhere" is a checkable exit status instead of a hope.

## 2. Install

**One-liner for your agent:**

```text
Install lumina-cli for me: https://raw.githubusercontent.com/example/lumina/v2.3.0/install.md
```

Prefer the one-liner. If you already have the repo checked out:

```bash
make install
lumina --version   # expect: lumina-cli 2.3.0
```

## 3. 30-second contrast

| Without lumina-cli | With lumina-cli |
|---|---|
| Hand-translate tokens per platform; drift found by users | One command per platform; drift printed as a diff table |
| "Same color everywhere" is a claim | Exit code 0 means no value changed in transit |

## 4. Capabilities

- Converts `tokens.json` (W3C design token draft format) to CSS variables,
  Swift, and Kotlin outputs.
- Reports every value that differs between input and output, as a table and a
  machine-readable exit code.
- Runs as a single static binary with no runtime dependencies.

## 5. How it works

lumina-cli parses the token source into an intermediate tree, applies
platform-specific quantization (for example, Android 5/6 bit color), then
diffs the round-tripped tree against the original. The diff *is* the product:
anything it prints is a value your users would have seen.

## 6. Boundaries — what lumina-cli does not do

> [!IMPORTANT]
> lumina-cli checks token *values* in transit. It does not validate design
> intent, enforce naming conventions, or sync back into Figma. Those are
> different tools' jobs.

- No watch mode yet (`watch-mode` is development archive: unreleased, see
  issue `#214`).
- No Windows binaries before v3.0 (CI gap, tracked in issue `#96`).

## 7. Evidence

| Claim | Where | Notes |
|---|---|---|
| 30k-token file converts in 41±3 ms | `scripts/bench.py`, run logged in `docs/bench-2026-10.md` | median of 50 runs, M2 MacBook |
| No runtime dependencies | `go.mod` has zero `require` entries | verified at v2.3.0 |
| W3C draft-format support | `internal/parser/w3c_test.go` | feature-frozen subset, see test for scope |

## 8. FAQ

- *Does it modify my token source?* Never — outputs are written to the
  `--out` directory; the source is read-only by design.
- *Why not Style Dictionary?* Style Dictionary is a build system with its own
  transform language; lumina-cli is a checker that reports transit drift. They
  compose; they do not compete.
- *Is it fast?* See the evidence table — 41±3 ms for 30k tokens, and the bench
  ships in the repo so you can produce your own number instead of trusting
  ours.

## 9. Contributing

Issues and PRs at `example/lumina`. Benchmarks and parser test cases are the
two highest-value contributions; read `docs/contributing.md` first.

## 10. License

The code in this repository is MIT-licensed; vendored parser fixtures retain
their upstream licenses (see `NOTICE`).
