# Bilingual convention & drift policy (L2)

Read when: only when Q4 = bilingual (the translation question; routed from
SKILL.md Step 1).

Unmanaged bilingualism is deferred divergence. This file fixes the file
conventions, the switch-line format, and what to do when one language falls
behind the other.

## File convention

- `README.md` — source of truth (English by default; if the project's primary
  audience is Chinese, the pairing below inverts — but one of the two files
  must be *declared* the source, in writing, in both files).
- `README.zh-CN.md` — translation. Never a fork: no translated-only sections,
  no original-only sections. If content divergence is desired, it becomes a
  different document with a different name.

## Switch line

Top of each file, under the header (element 5 in `anatomy.md`):

```
**English** | [简体中文](README.zh-CN.md)      ← in README.md
[English](README.md) | **简体中文**             ← in README.zh-CN.md
```

Rules:

- Current language bold, other language a plain link, **no `#fragment`** —
  the switch line swaps documents, not sections. Gate 5 checks bidirectional
  reachability and flags fragment-bearing switch links.
- Exactly one switch line per file. A second cross-language link deeper in the
  body is where drift begins.

## Drift policy — three tiers of lag, three responses

Declare the policy in a `[!NOTE]` at the top of the translation file. The
default:

> `[!NOTE]` English `README.md` is the source of truth. This translation may
> lag; when in conflict, the English file wins. Last synced: 2026-10-27.

| Lag | Detection | Required response |
|---|---|---|
| **Link drift** (translation links to anchors that moved) | Gate 5 + gate 1 on both files | Fix immediately — mechanical, no judgment involved |
| **Content drift** (translation missing new sections) | Diff section counts — automated as gate 5's heading-sequence parity when the doctor runs with `--zh`; the Last-synced date remains the human check for what a heading sequence cannot see | Either sync now, or move the missing section into a "pending translation" list in the `[!NOTE]`. Never let the translation silently claim parity |
| **Terminology drift** (same term, two translations) | Glossary check | One row in a mini-glossary table at the bottom of the translation; the row wins over any single usage |

## Cross-reference residue

Links pointing into the *other* language file (`README.zh-CN.md#某节`) are
residue when: the target file doesn't exist, or the link is deeper than the
switch line. Gate 5 fails both. The fix is always the same: point at the
anchor in the *current* file; the reader uses the switch line to cross.

## Translation is not this skill's job

This file governs conventions and drift. The translation act itself — tone,
idiom, naturalness — is the agent's general capability. Do not build
translation workflows here.
