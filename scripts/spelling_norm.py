#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
spelling_norm.py -- rewrite every surface variant of the project name to the
canonical form. Gate 3 of readme_doctor.py detects; this fixes.

Why this exists: mixed spellings ("Lumina CLI" / "lumina-cli" / "LuminaCLI")
survive eyeball review indefinitely -- the eye reads words, not strings.
Construct the comparison, don't eyeball it (same principle as the gates).

Usage
  python scripts/spelling_norm.py README.md --name lumina-cli [--allow "Lumina CLI"] [--write]

Dry-run by default: prints a unified diff. --write applies in place.
Stdlib only.
"""
from __future__ import annotations

import argparse
import difflib
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from readme_doctor import _name_pattern  # share the variant detector


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", help="markdown file to normalize")
    ap.add_argument("--name", required=True, help="canonical project name")
    ap.add_argument("--allow", action="append", default=[],
                    help="surface form to leave untouched (repeatable)")
    ap.add_argument("--write", action="store_true", help="apply changes in place")
    args = ap.parse_args(argv)

    path = Path(args.file)
    text = path.read_text(encoding="utf-8")
    keep = set(args.allow) | {args.name}
    pat = _name_pattern(args.name)
    changes = 0

    def repl(m: re.Match) -> str:
        nonlocal changes
        if m.group(0) in keep:
            return m.group(0)
        changes += 1
        return args.name

    new_text = pat.sub(repl, text)

    if changes == 0:
        print(f"spelling_norm: already canonical ({args.name!r}); nothing to do")
        return 0

    diff = difflib.unified_diff(
        text.splitlines(keepends=True), new_text.splitlines(keepends=True),
        fromfile=str(path) + " (before)", tofile=str(path) + " (after)")
    sys.stdout.writelines(diff)
    print(f"spelling_norm: {changes} occurrence(s) -> {args.name!r}"
          + ("  [written]" if args.write else "  [dry-run; pass --write to apply]"))
    if args.write:
        path.write_text(new_text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
