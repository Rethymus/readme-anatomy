#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validate_skill.py -- validate SKILL.md against the agentskills.io spec (v0.1).

Closes the mechanical half of research.md's decay-watchlist item 3 (spec
evolution): a stricter official validator or a new required field would fail
here first, in CI, on every push. Constraint set verified against
https://agentskills.io/specification on 2026-10-27:

  name          required; 1-64 chars; ^[a-z0-9]+(-[a-z0-9]+)*$ (lowercase,
                no leading/trailing or consecutive hyphens); must equal the
                parent directory name
  description   required; 1-1024 chars
  license       optional; short string
  compatibility optional; 1-500 chars if present
  metadata      optional; map of string keys to string values
  allowed-tools optional; space-separated string (experimental)
  body          <= 500 lines (recommended; enforced here as FAIL)
  unknown top-level keys -> WARN (tolerant: the spec reserves future fields)

Usage
  python scripts/validate_skill.py [SKILL_DIR]   # default: this skill's dir
  python scripts/validate_skill.py --selftest

Stdlib only; parses the YAML subset skills actually use (flat keys, one
nested map, folded continuation lines) rather than shipping a YAML dep.
"""
from __future__ import annotations

import argparse
import re
import sys
import tempfile
from pathlib import Path

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
KNOWN_KEYS = {"name", "description", "license", "compatibility", "metadata",
              "allowed-tools"}
MAX_BODY_LINES = 500


def parse_frontmatter(text: str) -> tuple[dict, list[str], list[str]]:
    """Return (flat dict with metadata as nested dict, body_lines, problems).
    Continuation lines (indented, not 'key:' form) fold into the previous
    scalar with a space, mirroring YAML's folded style closely enough for
    the subset skills use."""
    fm: dict = {}
    problems: list[str] = []
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, [], ["file does not start with '---' frontmatter delimiter"]
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        return {}, [], ["frontmatter never closes (missing second '---')"]
    body = lines[end + 1:]

    current_key: str | None = None
    in_metadata = False
    for raw in lines[1:end]:
        if not raw.strip():
            continue
        top = re.match(r"^([A-Za-z][\w-]*):\s*(.*)$", raw)
        nested = re.match(r"^\s+([\w.-]+):\s*(.*)$", raw)
        if top:
            in_metadata = top.group(1) == "metadata"
            current_key = top.group(1)
            value = top.group(2).strip()
            if value == "":
                if in_metadata:
                    fm.setdefault("metadata", {})
                else:
                    fm[current_key] = ""
            else:
                fm[current_key] = _scalar(value)
        elif nested:
            if current_key != "metadata":
                problems.append(f"nested key outside 'metadata': {raw.strip()!r}")
                continue
            val = nested.group(2).strip()
            if val.startswith(("[", "{")):
                problems.append(f"metadata.{nested.group(1)} value is not a "
                                f"string scalar: {val!r}")
            else:
                fm.setdefault("metadata", {})[nested.group(1)] = _scalar(val)
        elif current_key is not None and current_key != "metadata":
            fm[current_key] = str(fm.get(current_key, "")) + " " + raw.strip()
        else:
            problems.append(f"unparseable frontmatter line: {raw.strip()!r}")
    return fm, body, problems


def _scalar(v: str) -> str:
    return v.strip().strip("'\"") if v.strip().startswith(("'", '"')) else v


def validate(skill_dir: Path) -> tuple[list[str], list[str]]:
    """Return (failures, warnings) for the SKILL.md inside skill_dir."""
    skill_dir = skill_dir.resolve()
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return [f"no SKILL.md in {skill_dir}"], []
    fails, warns = [], []
    fm, body, problems = parse_frontmatter(skill_md.read_text(encoding="utf-8"))
    fails += problems

    name = fm.get("name")
    if not name or not isinstance(name, str):
        fails.append("frontmatter: 'name' is required")
    else:
        if len(name) > 64:
            fails.append(f"name exceeds 64 chars ({len(name)})")
        if not NAME_RE.match(name):
            fails.append(f"name violates spec pattern: {name!r}")
        if name != skill_dir.name:
            fails.append(f"name {name!r} != directory name {skill_dir.name!r}")

    desc = fm.get("description")
    if not desc or not str(desc).strip():
        fails.append("'description' is required and non-empty")
    elif len(str(desc)) > 1024:
        fails.append(f"description exceeds 1024 chars ({len(str(desc))})")

    compat = fm.get("compatibility")
    if compat is not None and len(str(compat)) > 500:
        fails.append(f"compatibility exceeds 500 chars ({len(str(compat))})")

    meta = fm.get("metadata")
    if meta is not None:
        if not isinstance(meta, dict):
            fails.append("'metadata' must be a map of string keys to string values")
        else:
            for k, v in meta.items():
                if not isinstance(v, str):
                    fails.append(f"metadata.{k} value is not a string scalar")

    for key in fm:
        if key not in KNOWN_KEYS:
            warns.append(f"unknown frontmatter key (spec-reserved?): {key!r}")

    if len(body) > MAX_BODY_LINES:
        fails.append(f"SKILL.md body is {len(body)} lines (max {MAX_BODY_LINES})")
    return fails, warns


def selftest() -> int:
    good_fm = ("---\n"
               "name: demo-skill\n"
               "description: Does one thing well. Use when the user says demo.\n"
               "metadata:\n"
               "  version: \"1.0\"\n"
               "---\n# Demo\n")
    bad = []

    def _case(label: str, expect_fail: bool, files: dict, dirname: str = "demo-skill"):
        with tempfile.TemporaryDirectory() as td:
            d = Path(td) / dirname
            d.mkdir()
            for fname, content in files.items():
                (d / fname).write_text(content, encoding="utf-8")
            fails, _ = validate(d)
            ok = bool(fails) == expect_fail
            bad.append(not ok)
            print(f"  [{'PASS' if ok else 'FAIL'}] validate selftest: {label} "
                  f"(expected {'FAIL' if expect_fail else 'PASS'}, "
                  f"got {'FAIL: ' + fails[0] if fails else 'PASS'})")

    _case("valid minimal skill", False, {"SKILL.md": good_fm})
    _case("name/directory mismatch", True,
          {"SKILL.md": good_fm.replace("demo-skill", "other-skill")})
    _case("uppercase name", True,
          {"SKILL.md": good_fm.replace("demo-skill", "Demo-Skill")}, dirname="Demo-Skill")
    _case("consecutive hyphens in name", True,
          {"SKILL.md": good_fm.replace("demo-skill", "demo--skill")}, dirname="demo--skill")
    _case("name over 64 chars", True,
          {"SKILL.md": good_fm.replace("demo-skill", "a" * 65)}, dirname="a" * 65)
    _case("empty description", True,
          {"SKILL.md": good_fm.replace(
              "description: Does one thing well. Use when the user says demo.\n", "")})
    _case("description over 1024 chars", True,
          {"SKILL.md": good_fm.replace(
              "Does one thing well. Use when the user says demo.", "x" * 1025)})
    _case("compatibility over 500 chars", True,
          {"SKILL.md": good_fm.replace(
              "metadata:", f"compatibility: {'y' * 501}\nmetadata:")})
    _case("non-scalar metadata value", True,
          {"SKILL.md": good_fm.replace('  version: "1.0"', "  version: [1, 2]")})
    _case("body over 500 lines", True,
          {"SKILL.md": good_fm + "\n" * 501})

    def _warn_probe() -> str:
        with tempfile.TemporaryDirectory() as td:
            d = Path(td) / "demo-skill"
            d.mkdir()
            (d / "SKILL.md").write_text(
                good_fm.replace("metadata:", "future-field: x\nmetadata:"),
                encoding="utf-8")
            fails, warns = validate(d)
            return "warn-only" if not fails and warns else "other"

    got = _warn_probe()
    ok = got == "warn-only"
    bad.append(not ok)
    print(f"  [{'PASS' if ok else 'FAIL'}] validate selftest: unknown key warns "
          f"without failing (got {got})")

    total = len(bad)
    print(f"selftest: {total - sum(bad)}/{total} green")
    return 1 if sum(bad) else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("skill_dir", nargs="?",
                    default=str(Path(__file__).resolve().parent.parent),
                    help="skill directory containing SKILL.md (default: this skill)")
    ap.add_argument("--selftest", action="store_true",
                    help="run the built-in fixtures and exit")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    fails, warns = validate(Path(args.skill_dir))
    for w in warns:
        print(f"WARN: {w}")
    for f in fails:
        print(f"FAIL: {f}")
    print(f"validate_skill: {'FAIL' if fails else 'PASS'} "
          f"({len(fails)} failure(s), {len(warns)} warning(s))")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
