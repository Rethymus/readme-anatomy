#!/usr/bin/env python3
"""table_doctor.py -- escape-aware GFM pipe-table integrity checker (stdlib only).

Background: independent review of v0.10.1 (commit af1f745) found ledger
table cells carrying BARE unescaped pipes ('python | tail', '||') that GFM
split at render time, silently dropping the Status column; the fix escaped
them as \\|, and the fix-time verification scan used naive split('|') --
which counts escaped pipes too and would have misreported the now-correct
rows.  Two defects, one lesson surface.  This tool re-derives it as a gate:

  * cell splitting is escape-aware: `\\|` is a literal pipe, not a separator;
  * every table's delimiter row and every data row must have the same number
    of cells as its header row -- a mismatch is a FAIL carrying the line
    number and both counts;
  * boundary rules: fenced code blocks (``` or ~~~), indented code blocks
    (4+ columns of spaces OR tabs -- a tab advances to the next multiple
    of 4), and interrupting HTML blocks (CommonMark types 1-6, e.g. <div>)
    are never part of a table; the delimiter row itself is never counted as
    a data row; a pipe-bearing line with no delimiter row beneath it is
    prose, not a table.

Usage:
    python scripts/table_doctor.py <file>          # check one markdown file
    python scripts/table_doctor.py <file> --json   # machine-readable report
    python scripts/table_doctor.py --selftest      # dual-anchor fixtures

Exit codes: 0 = all tables intact (or no tables), 1 = at least one mismatch,
2 = usage error.  Read-only: the file is never modified.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path

# ---------------------------------------------------------------- parsing ----

_DELIM_CELL = re.compile(r":?-+:?$")
_FENCE_TOKEN = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
_LIST_MARKER = re.compile(r"^ {0,3}(?:[-*+] |\d{1,9}[.)] )")
_HR = re.compile(r"^ {0,3}(?:-{3,}|\*{3,}|_{3,})\s*$")


def split_cells(line: str) -> list[str]:
    """Split a table row into raw cell strings, escape-aware.

    A pipe preceded by an unescaped backslash (`\\|`) is a literal pipe and
    stays inside its cell -- escaped cells must not be miscounted (the
    af1f745 fix-time scan counted them; the render-time defect had been
    the bare pipes).
    """
    cells: list[str] = []
    cur: list[str] = []
    escaped = False
    for ch in line:
        if escaped:
            cur.append(ch)
            escaped = False
        elif ch == "\\":
            cur.append(ch)
            escaped = True
        elif ch == "|":
            cells.append("".join(cur))
            cur = []
        else:
            cur.append(ch)
    cells.append("".join(cur))
    if len(cells) > 2 and cells[0].strip() == "":
        cells = cells[1:]
        if cells and cells[-1].strip() == "":
            cells = cells[:-1]
    elif len(cells) > 1 and cells[-1].strip() == "" and cells[0].strip() != "":
        cells = cells[:-1]
    return cells


def cell_count(line: str) -> int:
    """Number of cells in a table row, after trimming the outer empties."""
    return len(split_cells(line))


def is_delimiter_row(line: str) -> bool:
    """True for a GFM table delimiter row like `|---|:---:|` (>=1 pipe)."""
    if "|" not in line:
        return False
    cells = split_cells(line)
    if not cells:
        return False
    stripped = [c.strip() for c in cells]
    return all(_DELIM_CELL.fullmatch(c) for c in stripped)


_HTML_BLOCK_TAGS = (
    "address|article|aside|base|basefont|blockquote|body|caption|center|col|"
    "colgroup|dd|details|dialog|dir|div|dl|dt|fieldset|figcaption|figure|"
    "footer|form|frame|frameset|h[1-6]|head|header|hr|html|iframe|legend|li|"
    "link|main|menu|menuitem|nav|noframes|ol|optgroup|option|p|param|section|"
    "source|summary|table|tbody|td|tfoot|th|thead|title|tr|track|ul"
)
# CommonMark HTML blocks that can interrupt a paragraph (types 1-6): type 1
# (script/pre/style/textarea), type 5 (exactly `<![CDATA[`, case-sensitive --
# a loose `<![` would over-match declarations like <![foo]>), declarations
# `<!DOCTYPE` (matched by `![A-Za-z]`), type 6 (the block-tag list), plus
# comments and processing instructions.  Type 7 (any other complete tag,
# e.g. <br>) can NOT interrupt a paragraph, so it must stay a table row.
_HTML_BLOCK = re.compile(
    r"^ {0,3}<(?:/?(?:" + _HTML_BLOCK_TAGS + r"|script|pre|style|textarea)"
    r"(?:\s|>|/>|$)|!--|\?|!\[CDATA\[|![A-Za-z])",
    re.IGNORECASE,
)


def indent_columns(line: str) -> int:
    """Leading whitespace of `line` in columns (GFM: a tab advances to the
    next multiple of 4), so a tab-indented line is an indented code block,
    exactly like a 4-space-indented one."""
    col = 0
    for ch in line:
        if ch == " ":
            col += 1
        elif ch == "\t":
            col += 4 - (col % 4)
        else:
            return col
    return col


def fence_open(line: str):
    """Return (fence_char, width) if `line` opens a GFM code fence, else None.

    GFM: a backtick fence's info string may not contain a backtick, so
    a line like three-backticks + "a`b" is NOT a fence -- treating it as
    one would mask every real table that follows it.
    """
    m = _FENCE_TOKEN.match(line)
    if not m:
        return None
    token = m.group(1)
    if token[0] == "`" and "`" in m.group(2):
        return None
    return token[0], len(token)


def fence_mask(lines: list[str]) -> list[bool]:
    """Per-line mask: True = this line is inside (or is) a code fence."""
    mask = [False] * len(lines)
    ch: str | None = None
    width = 0
    for i, line in enumerate(lines):
        if ch is None:
            op = fence_open(line)
            if op:
                ch, width = op
                mask[i] = True
        else:
            mask[i] = True
            s = line.rstrip()
            lead = len(s) - len(s.lstrip(" "))
            body = s.lstrip(" ")
            if (
                body.startswith(ch)
                and set(body) == {ch}
                and len(body) >= width
                and lead <= 3
            ):
                ch, width = None, 0
    return mask


def _starts_block(line: str) -> bool:
    """GFM: a table is broken at a blank line or another block-level start."""
    if not line.strip():
        return True
    if fence_open(line):
        return True
    if _LIST_MARKER.match(line):
        return True
    if _HR.match(line):
        return True
    if re.match(r"^ {0,3}(#|>)", line):
        return True
    if _HTML_BLOCK.match(line):
        return True
    return False


def iter_tables(
    lines: list[str],
) -> list[dict]:
    """Yield tables as dicts of header/delimiter/data rows with line numbers."""
    mask = fence_mask(lines)
    tables: list[dict] = []
    i = 0
    n = len(lines)
    while i < n - 1:
        line = lines[i]
        if mask[i] or _starts_block(line) or "|" not in line:
            i += 1
            continue
        # A line indented 4+ columns is an indented code block in GFM and can
        # never START a table (a table's first row may be indented 0-3).
        # Tabs count toward the columns, like spaces.
        if indent_columns(line) >= 4:
            i += 1
            continue
        nxt = lines[i + 1]
        # The delimiter row obeys the same 0-3 indent rule: a 4+/tab-indented
        # `|---|---|` is an indented code block, so the candidate pair is a
        # paragraph, not a table (review round 3, finding 1 -- the tool
        # reported phantom defects on it).
        if mask[i + 1] or indent_columns(nxt) >= 4 or not is_delimiter_row(nxt):
            i += 1
            continue
        header_lineno = i + 1  # 1-based
        delim_lineno = i + 2
        header_cells = cell_count(line)
        delim_cells = cell_count(nxt)
        rows: list[dict] = []
        j = i + 2
        while j < n:
            body = lines[j]
            if mask[j] or _starts_block(body):
                break
            # A 4+/tab-indented continuation line is an indented code block
            # (markdown_it parses "table with zero data rows + code_block"),
            # so it ends the body and is never a defect of the table above
            # it (review round 3, finding 3).
            if indent_columns(body) >= 4:
                break
            rows.append({"lineno": j + 1, "cells": cell_count(body), "raw": body})
            j += 1
        tables.append(
            {
                "header_lineno": header_lineno,
                "delimiter_lineno": delim_lineno,
                "header_cells": header_cells,
                "delimiter_cells": delim_cells,
                "rows": rows,
            }
        )
        i = j
    return tables


# ---------------------------------------------------------------- checking ----

def check_text(text: str) -> dict:
    """Check every GFM table in `text`; return a report dict (never mutates)."""
    lines = text.splitlines()
    tables = iter_tables(lines)
    defects: list[dict] = []
    for t in tables:
        expected = t["header_cells"]
        if t["delimiter_cells"] != expected:
            defects.append(
                {
                    "lineno": t["delimiter_lineno"],
                    "kind": "delimiter",
                    "got": t["delimiter_cells"],
                    "expected": expected,
                }
            )
        for r in t["rows"]:
            if r["cells"] != expected:
                defects.append(
                    {
                        "lineno": r["lineno"],
                        "kind": "data",
                        "got": r["cells"],
                        "expected": expected,
                    }
                )
    return {
        "tables": len(tables),
        "data_rows": sum(len(t["rows"]) for t in tables),
        "defects": defects,
        "passed": not defects,
    }


def check_file(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    report = check_text(text)
    report["file"] = str(path)
    return report


def render(report: dict) -> list[str]:
    out = [f"table_doctor: {report['file']}"]
    out.append(
        f"  tables={report['tables']} data_rows={report['data_rows']} "
        f"defects={len(report['defects'])}"
    )
    for d in report["defects"]:
        kind = "delimiter row" if d["kind"] == "delimiter" else "data row"
        out.append(
            f"  FAIL line {d['lineno']}: {kind} has {d['got']} cell(s), "
            f"header has {d['expected']}"
        )
    verdict = "PASS" if report["passed"] else "FAIL"
    out.append(f"  {verdict} {report['file']}")
    return out


# ---------------------------------------------------------------- selftest ----
# Dual anchors per defect class: a fixture that MUST fire and one that MUST
# NOT (false-positive guard).  Fixtures run through the same check_text()
# code path as production.


def naive_cell_count(line: str) -> int:
    """The defect being guarded: a naive split('|') linter's cell count
    (same outer-empty trim, no escape awareness)."""
    parts = line.split("|")
    if len(parts) > 1 and not parts[-1].strip():
        parts = parts[:-1]
    if len(parts) > 1 and not parts[0].strip():
        parts = parts[1:]
    return len(parts)


def selftest() -> int:
    escaped_row = "| x \\| y | 2 |"
    cases: list[dict] = []

    # 1. must-not-fire: healthy table
    cases.append(
        {
            "label": "must-not-fire: healthy 3-col table, 2 data rows",
            "text": "| A | B | C |\n|---|---|---|\n| 1 | 2 | 3 |\n| 4 | 5 | 6 |\n",
            "expect": "pass",
            "expect_tables": 1,
        }
    )

    # 2. must-not-fire: escaped pipe stays one cell (the v0.10.1 regression);
    #    the anchor only guards something if naive splitting WOULD misreport,
    #    so that is asserted here too (fail-closed on a toothless anchor).
    cases.append(
        {
            "label": "must-not-fire: escaped \\| inside a cell (naive split would fire)",
            "text": "| A | B |\n|---|---|\n" + escaped_row + "\n",
            "expect": "pass",
            "expect_tables": 1,
            "naive_probe": (escaped_row, 2, 3),
        }
    )

    # 3. must-fire: data row one column too many
    cases.append(
        {
            "label": "must-fire: data row has one extra column",
            "text": "| A | B |\n|---|---|\n| 1 | 2 | 3 |\n",
            "expect": "fail",
            "expect_defects": [(3, "data", 3, 2)],
        }
    )

    # 4. must-fire: data row one column short
    cases.append(
        {
            "label": "must-fire: data row has one column short",
            "text": "| A | B |\n|---|---|\n| 1 |\n",
            "expect": "fail",
            "expect_defects": [(3, "data", 1, 2)],
        }
    )

    # 5. must-fire: delimiter row count disagrees with header
    cases.append(
        {
            "label": "must-fire: delimiter row column count mismatch",
            "text": "| A | B | C |\n|---|---|\n| 1 | 2 | 3 |\n",
            "expect": "fail",
            "expect_defects": [(2, "delimiter", 2, 3)],
        }
    )

    # 6. must-not-fire: a deliberately broken table inside a code fence
    cases.append(
        {
            "label": "must-not-fire: broken table inside a fenced code block",
            "text": "```md\n| A | B |\n|---|---|\n| 1 | 2 | 3 |\n```\n",
            "expect": "pass",
            "expect_tables": 0,
        }
    )

    # 7. must-not-fire: pipe-bearing prose with no delimiter row is not a table
    cases.append(
        {
            "label": "must-not-fire: pipe-bearing line with no delimiter row",
            "text": "just | some | prose\nand more prose\n",
            "expect": "pass",
            "expect_tables": 0,
        }
    )

    # 8. must-not-fire: blank line ends the table; later pipe lines are new
    #    (non-table) blocks, never data rows of the earlier table
    cases.append(
        {
            "label": "must-not-fire: blank line ends the table body",
            "text": "| A | B |\n|---|---|\n\n| 1 | 2 | 3 |\n",
            "expect": "pass",
            "expect_tables": 1,
        }
    )

    # 9. must-not-fire: a 4-space-indented code block renders as code in
    #    GFM -- its interior is never a table, even when deliberately broken
    cases.append(
        {
            "label": "must-not-fire: pipe lines inside an indented code block",
            "text": "    | A | B |\n    |---|---|\n    | 1 | 2 | 3 |\n",
            "expect": "pass",
            "expect_tables": 0,
        }
    )

    # 10. must-not-fire: the start-indent guard must not swallow real tables
    #     -- a healthy 0-indent table next to an indented lookalike finds
    #     exactly one table and passes
    cases.append(
        {
            "label": "must-not-fire: indented lookalike beside a real table",
            "text": ("| A | B |\n|---|---|\n| 1 | 2 |\n\n"
                     "    | X | Y |\n    |---|---|\n    | 1 | 2 | 3 |\n"),
            "expect": "pass",
            "expect_tables": 1,
        }
    )

    # 11. must-not-fire: a backtick fence's info string may not contain a
    #     backtick (GFM) -- ```a`b is not a fence, so it must not mask the
    #     real table after it (the pre-fix tool found 0 tables here)
    cases.append(
        {
            "label": "must-not-fire: backtick in fence info is no fence (no masking)",
            "text": "```a`b\nsome text\n\n| A | B |\n|---|---|\n| 1 | 2 |\n",
            "expect": "pass",
            "expect_tables": 1,
        }
    )

    # 12. must-not-fire: a CommonMark type-6 HTML block (<div>) can interrupt
    #     a paragraph, so it ends the table instead of joining it as a 1-cell
    #     data row (pre-fix probe false-FAILED line 4: 1 cell vs header 2)
    cases.append(
        {
            "label": "must-not-fire: HTML block adjacent to the table ends it",
            "text": "| A | B |\n|---|---|\n| 1 | 2 |\n<div>\n",
            "expect": "pass",
            "expect_tables": 1,
            "expect_data_rows": 1,
        }
    )

    # 13. must-not-fire: a tab advances to the next multiple of 4 columns, so
    #     a tab-indented pipe block is an indented code block, never a table
    #     (pre-fix probe false-FAILED line 3: 3 cells vs header 2)
    cases.append(
        {
            "label": "must-not-fire: pipe lines inside a tab-indented code block",
            "text": "\t| A | B |\n\t|---|---|\n\t| 1 | 2 | 3 |\n",
            "expect": "pass",
            "expect_tables": 0,
        }
    )

    # 14. must-not-fire: an indented delimiter row is an indented code block,
    #     so the candidate pair is a paragraph -- no phantom defects on the
    #     unindented line after it (review round 3, finding 1: the tool
    #     false-FAILED line 3 here)
    cases.append(
        {
            "label": "must-not-fire: indented delimiter row is no table",
            "text": "| A | B |\n    |---|---|\n| 1 | 2 | 3 |\n",
            "expect": "pass",
            "expect_tables": 0,
        }
    )

    # 15. must-not-fire: a 4-space indented body line is an indented code
    #     block that ends the table -- zero data rows, not a defect
    #     (review round 3, finding 3: the tool false-FAILED line 3 here)
    cases.append(
        {
            "label": "must-not-fire: indented body line ends the table",
            "text": "| A | B |\n|---|---|\n    | 1 | 2 | 3 |\n",
            "expect": "pass",
            "expect_tables": 1,
            "expect_data_rows": 0,
        }
    )

    # 16. must-not-fire: CDATA (CommonMark HTML block type 5) interrupts the
    #     paragraph and ends the table -- not a 1-cell data row (review
    #     round 3, finding 2: the tool false-FAILED line 4 here)
    cases.append(
        {
            "label": "must-not-fire: CDATA block ends the table",
            "text": "| A | B |\n|---|---|\n| 1 | 2 |\n<![CDATA[x]]>\n",
            "expect": "pass",
            "expect_tables": 1,
            "expect_data_rows": 1,
        }
    )

    # 17. must-fire anchor for the tab-block guard: a real broken table
    #     after a tab-indented code block must still fire -- the guard must
    #     never swallow a genuine defect (finding 4's dual-anchor demand)
    cases.append(
        {
            "label": "must-fire: real broken table after a tab code block",
            "text": ("\t| A | B |\n\t|---|---|\n\n"
                     "| A | B |\n|---|---|\n| 1 | 2 | 3 |\n"),
            "expect": "fail",
            "expect_defects": [(6, "data", 3, 2)],
        }
    )

    # 18. must-fire anchor for the HTML-block guard: a real broken table
    #     after an interrupting <div> must still fire
    cases.append(
        {
            "label": "must-fire: real broken table after an HTML block",
            "text": ("| A | B |\n|---|---|\n| 1 | 2 |\n<div>\n\n"
                     "| A | B |\n|---|---|\n| 1 | 2 | 3 |\n"),
            "expect": "fail",
            "expect_defects": [(8, "data", 3, 2)],
        }
    )

    total = 0
    failed = 0
    for case in cases:
        total += 1
        ok = True
        notes: list[str] = []
        report = check_text(case["text"])
        want_fail = case["expect"] == "fail"
        if report["passed"] == want_fail:
            ok = False
            notes.append(f"expected {case['expect']}, got report {report['passed']}")
        if "expect_tables" in case and report["tables"] != case["expect_tables"]:
            ok = False
            notes.append(f"tables={report['tables']} want {case['expect_tables']}")
        if "expect_data_rows" in case and \
                report["data_rows"] != case["expect_data_rows"]:
            ok = False
            notes.append(
                f"data_rows={report['data_rows']} want {case['expect_data_rows']}")
        if want_fail:
            got = [(d["lineno"], d["kind"], d["got"], d["expected"])
                   for d in report["defects"]]
            if got != case["expect_defects"]:
                ok = False
                notes.append(f"defects={got} want {case['expect_defects']}")
        if "naive_probe" in case:
            raw, aware_want, naive_want = case["naive_probe"]
            aware = cell_count(raw)
            naive = naive_cell_count(raw)
            if (aware, naive) != (aware_want, naive_want):
                ok = False
                notes.append(
                    f"anchor toothless: aware={aware} naive={naive} "
                    f"want aware={aware_want} naive={naive_want}"
                )
        status = "PASS" if ok else "FAIL"
        if not ok:
            failed += 1
        print(f"  [{status}] table selftest: {case['label']}"
              + (f" ({'; '.join(notes)})" if notes else ""))

    print(f"table_doctor selftest: {total - failed}/{total} green")
    return 1 if failed else 0


# -------------------------------------------------------------------- main ----

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Escape-aware GFM pipe-table integrity checker.")
    ap.add_argument("file", nargs="?", help="markdown file to check")
    ap.add_argument("--selftest", action="store_true",
                    help="run the dual-anchor fixture suite")
    ap.add_argument("--json", action="store_true",
                    help="emit the report as JSON (with --file only)")
    args = ap.parse_args(argv)

    if args.selftest:
        if args.file:
            ap.error("--selftest takes no file argument")
        return selftest()
    if not args.file:
        ap.error("provide a markdown file, or --selftest")
    path = Path(args.file)
    if not path.is_file():
        print(f"table_doctor: no such file: {path}", file=sys.stderr)
        return 2
    report = check_file(path)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print("\n".join(render(report)))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
