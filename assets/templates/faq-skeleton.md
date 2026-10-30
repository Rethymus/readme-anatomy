# FAQ skeleton (anatomy.md L1, section 8)

FAQ is a standalone section, and every entry is a real question — including
the hostile one. If no one has asked anything yet, seed it from the
boundaries section: every boundary generates a "why not X?" question.

```markdown
## FAQ

- *<The hostile question — "Why not <obvious alternative>?"*
  <One-paragraph honest answer; if the alternative is better for some use
  case, say so and link out.>

- *<The misread — the thing users assume it does but it doesn't>*
  <Point at the boundaries section; repeat the boundary in one sentence.>

- *<The operational question — install/upgrade/compatibility>*
  <Answer with a command or a version table, not prose.>

- *<The trust question — "how do I know claim X is true?">*
  <Link the evidence table row, and let countable public evidence answer:
  a number the reader can click through to — a release page, a merged-PR
  listing, a benchmark log. A slogan is a non-answer.>
```

Anti-patterns (each of these means the entry is decoration):

- Invented questions no reader would ask ("Is this tool amazing?").
- Answers that restate the question ("Is it fast? It's very fast").
- More than eight entries — a longer FAQ is a boundaries section that didn't
  get written.
