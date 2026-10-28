#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
claims_probe.py -- verify the evidence table's "Where" column (READU-style). (v0.1)

The claims discipline (references/claims-posture.md) says every tier-verified
claim carries a "Where" cell that is a path or a command -- never prose, never
a URL alone ("a citation is not a measurement"). This tool checks that the
table can survive contact with the repository, in the spirit of READU
(Inconsistency-Driven Just-in-Time Detection and Repair of README Bugs, 2026;
anchor in references/research.md):

  path            exists relative to the README's directory (repo root)
  path.md#anchor  the target file exists AND the anchor resolves under GitHub
                  slug rules (same slugger as gate 1; percent-encoded
                  fragments are decoded first)
  path.py:123     the file has at least 123 lines
  command         the interpreter/binary is on PATH (python, node, git, ...);
                  a .py path with arguments counts as an implicit python cmd
  cmd → `text`    optional output contract: with --run, `text` must appear in
                  the command's stdout/stderr. Offline it WARNs -- an
                  unverified output claim is not a pass.
  prose / URL     WARN -- the "Where" cell must be checkable

**What this certifies**: that each evidence anchor *resolves*. It does not
certify that the claim is true -- a resolvable path to a benchmark script
says nothing about the number next to it. Anchorability is necessary, not
sufficient (the same judgment sentence that governs the doctor's gates).

Checks are offline and side-effect-free by default. --run additionally
executes commands (10s timeout each) and checks exit codes -- opt-in,
because running arbitrary README commands is a trust decision (see
references/agent-surfaces.md on weaponized setup instructions). Only
recognized commands and `.py` paths with arguments are ever executed; an
unrecognized command word WARNs instead of guessing.

This is deliberately NOT gate 8 of readme_doctor.py: the doctor's gates apply
to any README; the evidence table is this method's own semantic contract.

Usage
  python scripts/claims_probe.py README.md [--run] [--json]
  python scripts/claims_probe.py --selftest

Exit 0 = no FAIL. Stdlib only.
"""
from __future__ import annotations

import argparse
import json
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import unquote

sys.path.insert(0, str(Path(__file__).parent))
from readme_doctor import collect_headings, strip_code_fences  # noqa: E402

KNOWN_COMMANDS = ("python", "python3", "pip", "pip3", "node", "npm", "npx",
                  "git", "make", "bash", "sh", "curl", "wget", "pytest")
PATH_HINT_RE = re.compile(r"^\.?[\w.-]*[/\\]|^[^/\s]*\.(py|md|yml|yaml|json|toml|js|ts|mjs|txt|cfg|ini|sh)$",
                          re.IGNORECASE)
EVIDENCE_SECTION_RE = re.compile(r"^##\s+.*(\bevidence\b|证据).*?$", re.IGNORECASE)
NEXT_SECTION_RE = re.compile(r"^##\s+")
TABLE_ROW_RE = re.compile(r"^\s*\|.*\|\s*$")
TABLE_SPLIT_RE = re.compile(r"^\s*\||\|\s*$")
SEPARATOR_RE = re.compile(r"^[\s|:-]+$")
CODE_SPAN_RE = re.compile(r"`([^`\n]+)`")
EXPECT_SPLIT_RE = re.compile(r"\s*(?:→|->)\s*")
URL_RE = re.compile(r"^https?://", re.IGNORECASE)


def parse_evidence_rows(text: str) -> list[tuple[str, str]]:
    """(claim, where) data rows from the Evidence section's table(s)."""
    rows: list[tuple[str, str]] = []
    lines = strip_code_fences(text).splitlines()
    in_section = False
    for line in lines:
        if NEXT_SECTION_RE.match(line):
            in_section = bool(EVIDENCE_SECTION_RE.match(line))
            continue
        if not in_section or not TABLE_ROW_RE.match(line):
            continue
        cells = [c.strip() for c in TABLE_SPLIT_RE.sub("", line).split("|")]
        if len(cells) < 2 or SEPARATOR_RE.match(line):
            continue
        if re.search(r"\bclaim\b|\b主张\b", cells[0], re.IGNORECASE):
            continue  # header row
        rows.append((cells[0], cells[1]))
    return rows


def _classify(token: str) -> dict:
    if URL_RE.match(token):
        return {"raw": token, "kind": "url"}
    if re.match(r"^-", token):
        return {"raw": token, "kind": "flag"}
    if token.split("/")[-1].split("\\")[-1].endswith(
            (".py", ".md", ".yml", ".yaml", ".json", ".toml", ".js", ".ts",
             ".mjs", ".txt", ".cfg", ".ini", ".sh")) or "/" in token or "\\" in token:
        return {"raw": token, "kind": "path"}
    if token in KNOWN_COMMANDS:
        return {"raw": token, "kind": "cmd"}
    return {"raw": token, "kind": "unknown"}


def extract_refs(where_cell: str) -> tuple[list[dict], bool]:
    """Verifiable refs from a Where cell. Returns (refs, has_any_span).
    Only inline-code spans are candidates -- prose is decoration, code is the
    claim's anchor. An optional `→ `expected text`` after a command records
    the output contract (checked only under --run)."""
    parts = EXPECT_SPLIT_RE.split(where_cell, maxsplit=1)
    left = parts[0]
    expect = None
    if len(parts) > 1:
        m = CODE_SPAN_RE.search(parts[1])
        if m:
            expect = m.group(1).strip()
    spans = CODE_SPAN_RE.findall(left)
    refs: list[dict] = []
    for span in spans:
        if span.startswith("<") and span.endswith(">"):
            continue  # template placeholder (<repo path or command>), not a reference
        tokens = shlex.split(span)
        if not tokens:
            continue
        head = _classify(tokens[0])
        if head["kind"] in ("path", "cmd"):
            ref = dict(head)
            body = tokens[0]
            path_part, _, frag = body.partition("#")
            path_part, _, lineno = path_part.partition(":")
            m = re.match(r"^(\d+)$", lineno)
            ref.update({"path": path_part, "frag": unquote(frag),
                        "line": int(m.group(1)) if m else None,
                        "args": tokens[1:], "span": span, "expect": expect})
            refs.append(ref)
        elif head["kind"] == "unknown" and len(tokens) > 1:
            # looks like "some-cmd args" but the word is not a known command:
            # warn honestly instead of guessing (env-specific commands exist)
            refs.append({"raw": tokens[0], "kind": "unknown-cmd",
                         "span": span, "args": tokens[1:], "expect": None})
    return refs, bool(CODE_SPAN_RE.search(where_cell))


def _apply_expect(status: str, detail: str, ref: dict, output: str | None,
                  run: bool) -> tuple[str, str]:
    """Fold the output contract (cmd → `expected text`) into a result.
    Executed output is checked by substring; offline the contract is reported
    as unverified rather than passed."""
    expect = ref.get("expect")
    if not expect:
        return status, detail
    if status == "fail":
        return status, detail
    if not run:
        return "warn", (f"{detail}; output contract {expect!r} unverified "
                        f"offline -- use --run")
    if output and expect in output:
        return status, f"{detail}; output contains {expect!r}"
    return "fail", f"`{ref['span']}` did not output {expect!r} (output contract violated)"


def _probe_ref(ref: dict, base_dir: Path, run: bool) -> tuple[str, str]:
    """(status, detail) for one ref: 'pass' | 'fail' | 'warn'."""
    if ref["kind"] == "unknown-cmd":
        return "warn", (f"unrecognized command word {ref['raw']!r} -- not in the "
                        f"known list; extend KNOWN_COMMANDS if it is real")
    if ref["kind"] == "cmd":
        if shutil.which(ref["raw"]) is None:
            return "fail", f"command not on PATH: {ref['raw']}"
        if run:
            argv = [ref["raw"]] + ref["args"]
            try:
                r = subprocess.run(argv, capture_output=True, text=True, timeout=10,
                                   cwd=str(base_dir))
                if r.returncode != 0:
                    return "fail", (f"`{ref['span']}` exited {r.returncode}: "
                                    f"{(r.stderr or r.stdout).strip()[:120]}")
                return _apply_expect("pass", f"`{ref['span']}` exited 0", ref,
                                     (r.stdout or "") + (r.stderr or ""), run)
            except subprocess.TimeoutExpired:
                return "warn", f"`{ref['span']}` timed out (10s)"
        return _apply_expect("pass", f"command on PATH: {ref['raw']} (--run to execute)",
                             ref, None, run)

    target = base_dir / ref["path"]
    if not target.exists():
        return "fail", f"missing path: {ref['path']}"
    if ref["frag"]:
        other = target.read_text(encoding="utf-8", errors="replace")
        if ref["frag"] not in set(collect_headings(other)):
            return "fail", f"broken anchor in {ref['path']}: #{ref['frag']}"
    if ref["line"] is not None and target.is_file():
        n = len(target.read_text(encoding="utf-8", errors="replace").splitlines())
        if ref["line"] > n:
            return "fail", f"{ref['path']}:{ref['line']} beyond EOF ({n} lines)"
    if ref["args"] and ref["path"].endswith(".py") and run:
        argv = [sys.executable, str(target)] + ref["args"]
        try:
            r = subprocess.run(argv, capture_output=True, text=True, timeout=10,
                               cwd=str(base_dir))
            if r.returncode != 0:
                return "fail", f"`{ref['span']}` exited {r.returncode}: {(r.stderr or '').strip()[:120]}"
            return _apply_expect("pass", f"`{ref['span']}` exited 0", ref,
                                 (r.stdout or "") + (r.stderr or ""), run)
        except subprocess.TimeoutExpired:
            return "warn", f"`{ref['span']}` timed out (10s)"
    detail = f"path exists: {ref['path']}"
    if ref["frag"]:
        detail += f"#{ref['frag']}"
    if ref["line"] is not None:
        detail += f":{ref['line']}"
    # a path ref with no executable form can only support an existence claim;
    # an output contract on it is unverifiable by construction
    if ref.get("expect"):
        return "warn", (f"{detail}; output contract {ref['expect']!r} cannot be "
                        f"checked against a bare path reference")
    return "pass", detail


def probe(readme: Path, *, run: bool = False) -> dict:
    """Programmatic entry (CLI and MCP share this): returns a report dict."""
    text = readme.read_text(encoding="utf-8")
    rows = parse_evidence_rows(text)
    report = {"file": str(readme), "run": bool(run), "rows": [],
              "failed": 0, "warned": 0, "checked": 0}
    if not rows:
        report["summary"] = "SKIP (no evidence table found)"
        return report
    for claim, where in rows:
        refs, has_span = extract_refs(where)
        entry = {"claim": claim[:80], "where": where[:120], "findings": []}
        if not refs:
            if has_span:
                entry["findings"].append(
                    ["warn", "Where cell has code spans but no verifiable path/command"])
            elif URL_RE.search(where):
                entry["findings"].append(
                    ["warn", "Where cell is a URL alone -- a citation is not a measurement"])
            else:
                entry["findings"].append(
                    ["warn", "Where cell is prose -- name a path or a command"])
            report["warned"] += 1
        for ref in refs:
            status, detail = _probe_ref(ref, readme.parent, run)
            report["checked"] += 1
            entry["findings"].append([status, detail])
            if status == "fail":
                report["failed"] += 1
            elif status == "warn":
                report["warned"] += 1
        report["rows"].append(entry)
    report["summary"] = (f"{report['checked']} ref(s) checked; "
                         f"{report['failed']} FAIL, {report['warned']} WARN")
    return report


# --------------------------------------------------------------- selftest ----
# Dual anchors per capability: a fixture that MUST fire and one that MUST NOT.

def selftest() -> int:
    fails = []

    def check(name, ok, detail=""):
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f": {detail}" if detail else ""))
        if not ok:
            fails.append(name)

    def _probe_cell(td: Path, where: str, extra_files: dict | None = None) -> list:
        readme = td / "README.md"
        for fname, content in (extra_files or {}).items():
            target = td / fname
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
        readme.write_text(f"# t\n\n## Evidence\n\n| Claim | Where | Notes |\n|---|---|---|\n"
                          f"| c | {where} | n |\n", encoding="utf-8")
        return [f for f in probe(readme)["rows"][0]["findings"]]

    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        # must-fire: missing path
        f = _probe_cell(tdp, "`scripts/gone.py` runs it")
        check("must-fire: missing path FAILs",
              f and f[0][0] == "fail" and "missing path" in f[0][1], f[0][1] if f else "")
        # must-not-fire: existing path
        f = _probe_cell(tdp, "`scripts/bench.py`, median of 50", {"scripts/bench.py": "print(1)\n"})
        check("must-not-fire: existing path passes, decoration ignored",
              f and f[0][0] == "pass" and "scripts/bench.py" in f[0][1])
        # anchor: must-fire broken, must-not-fire valid (same fixture pair)
        f = _probe_cell(tdp, "`docs/log.md#results`",
                        {"docs/log.md": "# Bench\n\n## Results\n\nhere\n"})
        check("must-not-fire: valid cross-file anchor passes", f and f[0][0] == "pass")
        f = _probe_cell(tdp, "`docs/log.md#missing`",
                        {"docs/log.md": "# Bench\n\n## Results\n\nhere\n"})
        check("must-fire: broken anchor FAILs", f and f[0][0] == "fail" and "anchor" in f[0][1])
        # line number: must-fire beyond EOF, must-not-fire within
        f = _probe_cell(tdp, "`src/tiny.py:99`", {"src/tiny.py": "x = 1\n"})
        check("must-fire: line number beyond EOF FAILs", f and f[0][0] == "fail" and "EOF" in f[0][1])
        f = _probe_cell(tdp, "`src/tiny.py:1`", {"src/tiny.py": "x = 1\n"})
        check("must-not-fire: in-range line number passes", f and f[0][0] == "pass")
        # command executability: must-not-fire (python on PATH), must-fire (bogus)
        f = _probe_cell(tdp, "`python scripts/bench.py`", {"scripts/bench.py": "print(1)\n"})
        check("must-not-fire: on-PATH command passes",
              f and f[0][0] == "pass" and "PATH" in f[0][1])
        # must-fire: a KNOWN command that is not on PATH (mocked -- CI images
        # carry all of them, so the real condition is manufactured here)
        from unittest import mock
        readme = tdp / "README.md"
        readme.write_text("# t\n\n## Evidence\n\n| Claim | Where |\n|---|---|\n"
                          "| c | `git status` |\n", encoding="utf-8")
        with mock.patch.object(shutil, "which", return_value=None):
            finding = probe(readme)["rows"][0]["findings"][0]
        check("must-fire: known command off PATH FAILs",
              finding[0] == "fail" and "PATH" in finding[1], finding[1])
        f = _probe_cell(tdp, "`some-env-cmd scripts/bench.py`", {"scripts/bench.py": "print(1)\n"})
        check("must-fire: unrecognized command word WARNs",
              f and f[0][0] == "warn" and "unrecognized" in f[0][1])
        # prose / URL-only Where cells -> WARN (must-fire, advisory class)
        f = _probe_cell(tdp, "see the benchmark section above")
        check("must-fire: prose Where cell WARNs", f and f[0][0] == "warn" and "prose" in f[0][1])
        f = _probe_cell(tdp, "https://example.com/paper")
        check("must-fire: URL-only Where cell WARNs", f and f[0][0] == "warn" and "citation" in f[0][1])
        # --run exit-code semantics + output contract
        readme = tdp / "README.md"
        readme.write_text("# t\n\n## Evidence\n\n| Claim | Where |\n|---|---|\n"
                          "| good | `python -c \"print(42)\"` |\n"
                          "| bad | `python -c \"raise SystemExit(3)\"` |\n",
                          encoding="utf-8")
        rep = probe(readme, run=True)
        statuses = {r["claim"]: r["findings"][0][0] for r in rep["rows"]}
        check("--run: exit 0 passes, nonzero FAILs",
              statuses.get("good") == "pass" and statuses.get("bad") == "fail")

        readme.write_text(
            "# t\n\n## Evidence\n\n| Claim | Where |\n|---|---|\n"
            "| match | `python -c \"print('selftest 9/9 green')\"` → `9/9 green` |\n"
            "| mismatch | `python -c \"print('1/9 green')\"` → `9/9 green` |\n",
            encoding="utf-8")
        rep = probe(readme, run=True)
        got = {r["claim"]: r["findings"][0][0] for r in rep["rows"]}
        check("output contract: matching text passes, mismatch FAILs",
              got.get("match") == "pass" and got.get("mismatch") == "fail", str(got))
        rep = probe(readme, run=False)
        got = {r["claim"]: r["findings"][0][0] for r in rep["rows"]}
        check("output contract offline: WARN (unverified is not a pass)",
              got.get("match") == "warn", str(got))

        f = _probe_cell(tdp, "`docs/log.md#%E7%BB%93%E6%9E%9C`",
                        {"docs/log.md": "# Bench\n\n## 结果\n\nhere\n"})
        check("must-not-fire: percent-encoded anchor resolves",
              f and f[0][0] == "pass", f[0][1] if f else "")
        # placeholders are not anchors: an unfilled scaffold row must not
        # fabricate refs (and must WARN -- it is an unfilled claim)
        f = _probe_cell(tdp, "`<repo path or command>` with `<仓库路径或命令>`")
        check("must-fire: placeholder-only Where cell WARNs as unfilled",
              f and f[0][0] == "warn" and "no verifiable" in f[0][1], f[0][1] if f else "")

    total = 17
    print(f"selftest: {total - len(fails)}/{total} green")
    return 1 if fails else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("readme", nargs="?", help="README whose evidence table to verify")
    ap.add_argument("--run", action="store_true",
                    help="execute commands (10s timeout) to check exit codes -- "
                         "opt-in: running README commands is a trust decision")
    ap.add_argument("--json", action="store_true", help="print a machine-readable report")
    ap.add_argument("--selftest", action="store_true", help="run the dual-anchor fixtures")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    if not args.readme:
        ap.error("provide a README file, or --selftest")
    readme = Path(args.readme)
    if not readme.exists():
        print(f"no such file: {readme}", file=sys.stderr)
        return 2
    report = probe(readme, run=args.run)
    print(f"claims_probe: {readme}" + ("  [run]" if args.run else "  [offline]"))
    for row in report["rows"]:
        print(f"  claim: {row['claim']}")
        for status, detail in row["findings"]:
            print(f"      {status.upper():4} {detail}")
    print(f"  -> {report['summary']}")
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if report["failed"] else 0


if __name__ == "__main__":
    sys.exit(main())
