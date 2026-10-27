#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
readme_doctor.py -- six machine gates for README craft. (v0.2)

Gates
  1 anchors      internal anchor links resolve under GitHub slug rules
                 (emoji-prefixed headings produce a LEADING HYPHEN:
                 "## Install" -> #install, "## 🚀 Install" -> #-install;
                 duplicate headings get -1, -2 suffixes; setext headings
                 count too). Broken anchors get nearest-match suggestions.
  2 links        relative targets exist on disk (and cross-file fragments
                 resolve); reference-style links ([text][label]) resolve via
                 their definitions, an undefined label is a defect; http(s)
                 links are syntax-checked offline and liveness-checked with
                 --live using GET -- raw.githubusercontent and similar
                 endpoints reject HEAD, which causes false 404s
  3 spelling     one canonical surface form of the project name; case-only
                 variants count as one form (sentence-initial capitalization
                 is orthography, not drift), while separator variants are
                 identity drift ("Lumina CLI" vs "lumina-cli" vs "LuminaCLI");
                 unlisted variants can be whitelisted with --allow
  4 badges       <= 4 badges; every badge href is meaningful (not "#"/empty);
                 shields.io badges use style=flat-square
  5 bilingual    language switch line is bidirectional; zero stale
                 cross-language references (links into a README.<lang>.md that
                 does not exist, or fragment-bearing cross-language links)
  6 admonitions  [!NOTE]/[!TIP]/[!IMPORTANT]/[!WARNING]/[!CAUTION] only,
                 canonical casing, no more than 2 of one type per document

Usage
  python scripts/readme_doctor.py README.md [--name canonical-name]
                                        [--zh README.zh-CN.md] [--live]
                                        [--allow SURFACE] ... [--json] [--fix]
  python scripts/readme_doctor.py --selftest

--json emits a machine-readable report (one JSON object) to stdout -- for CI
jobs and agent loops; exit code is unchanged. --fix repairs only the mechanical
defect classes in place (badge flat-square style, drifted prose name surfaces
-- never inline code); everything else is reported for judgment. Stdlib only;
offline by default so runs are reproducible in CI.

Known limitations (v0.2): shortcut reference links ([label] without brackets)
are ambiguous and are not collected; setext h2 underlines are treated as
headings wherever a non-blank text line directly precedes a --- rule, matching
GitHub's parse; admonition semantics (which box for which job) are audited by
the agent against references/claims-posture.md, not by this script.
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
import tempfile
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path

ADMONITION_TYPES = ("NOTE", "TIP", "IMPORTANT", "WARNING", "CAUTION")
README_LANG_RE = re.compile(r"^README[\w.\-]*\.md$", re.IGNORECASE)


# ---------------------------------------------------------------- shared ----

def strip_code_fences(text: str) -> str:
    """Blank out fenced code blocks, preserving line positions."""
    out, in_fence, fence = [], False, ""
    for line in text.splitlines():
        m = re.match(r"^\s*(```+|~~~+)", line)
        if m:
            tok = m.group(1)
            if not in_fence:
                in_fence, fence = True, tok
            elif tok[:3] == fence[:3]:
                in_fence, fence = False, ""
            out.append("")
            continue
        out.append("" if in_fence else line)
    return "\n".join(out)


def strip_inline_code(text: str) -> str:
    """Blank out inline code spans (`...`), preserving positions.
    Code identifiers (package/module names, paths) legitimately differ in
    casing/separators from prose naming -- they are not drift."""
    return re.sub(r"`[^`\n]+`", "''", text)


def github_slug(heading: str, seen: Counter) -> str:
    """Approximate github-slugger: lowercase, drop punctuation (emoji go too),
    spaces -> hyphens, duplicates get -1/-2 suffixes."""
    s = heading.strip().lower()
    s = re.sub(r"[^\w\- ]", "", s)
    s = s.replace(" ", "-")
    if seen[s]:
        s = f"{s}-{seen[s]}"
    seen[s] += 1
    return s


def collect_headings(text: str) -> list[str]:
    """ATX headings plus setext headings (text line directly followed by a
    === or --- underline), both outside code fences."""
    seen: Counter = Counter()
    slugs: list[str] = []
    lines = strip_code_fences(text).splitlines()
    for i, line in enumerate(lines):
        m = re.match(r"^(#{1,6})\s+(.+?)\s*#*\s*$", line)
        if m:
            slugs.append(github_slug(m.group(2), seen))
            continue
        if not line.strip():
            continue
        nxt = lines[i + 1].strip() if i + 1 < len(lines) else ""
        if re.fullmatch(r"={2,}", nxt) or re.fullmatch(r"-{2,}", nxt):
            slugs.append(github_slug(line, seen))
    return slugs


LINK_RE = re.compile(r"(?<!\!)\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
BADGE_RE = re.compile(r"\[!\[([^\]]*)\]\(([^)]+)\)\]\(([^)]+)\)")
IMG_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
REF_LINK_RE = re.compile(r"\[([^\]]*)\]\[([^\]]*)\]")
LINK_DEF_RE = re.compile(
    r"^\s{0,3}\[([^\]]+)\]:\s*<?([^\s>]+)>?(?:\s+[\"'(](?:.+?)[\"')])?\s*$")
# a badge line: a line consisting solely of bare images and/or linked images
BADGE_LINE_RE = re.compile(
    r"^\s{0,3}(?:\s*(?:\[!\[[^\]]*\]\([^)]+\)\]\([^)]+\)|!\[[^\]]*\]\([^)]+\)))+\s*$")
BADGE_HOSTS = ("shields.io", "badgen.net", "badgecdn.com", "badge.fury.io")


def collect_link_info(text: str) -> tuple[list[str], list[str]]:
    """All link targets (inline plus reference-style resolved through their
    definitions) and the list of reference links whose label is undefined."""
    stripped = BADGE_RE.sub("[badge]", strip_code_fences(text))
    urls = [m.group(1) for m in LINK_RE.finditer(stripped)]
    defs: dict[str, str] = {}
    for line in stripped.splitlines():
        m = LINK_DEF_RE.match(line)
        if m:
            defs.setdefault(m.group(1).strip().lower(), m.group(2))
    undefined: list[str] = []
    for m in REF_LINK_RE.finditer(stripped):
        label = (m.group(2) or m.group(1)).strip().lower()
        if not label and not m.group(1).strip():
            undefined.append(m.group(0))
        elif label in defs:
            urls.append(defs[label])
        else:
            undefined.append(m.group(0))
    return urls, undefined


def collect_links(text: str) -> list[str]:
    """Link targets only (inline and resolved reference-style)."""
    return collect_link_info(text)[0]


def collect_images(text: str) -> list[str]:
    """Image srcs from bare images (linked badges are badges, not images)."""
    stripped = BADGE_RE.sub("", strip_code_fences(text))
    return [m.group(2) for m in IMG_RE.finditer(stripped)]


# ------------------------------------------------------------------ gates ----
# Each gate returns (status, details, warnings): status in {"pass","fail","skip"}

def gate_anchors(text: str, ctx: dict) -> tuple[str, list[str], list[str]]:
    slugs = set(collect_headings(text))
    problems = []
    for url in collect_links(text):
        if not url.startswith("#"):
            continue
        frag = url[1:]
        if frag and frag not in slugs:
            near = difflib.get_close_matches(frag, sorted(slugs), n=2, cutoff=0.6)
            hint = f" (did you mean: #{near[0]}?)" if near else ""
            problems.append(f"broken anchor: #{frag}{hint}")
    return ("fail" if problems else "pass"), problems, []


def _check_http(url: str, live: bool) -> tuple[list[str], list[str]]:
    problems, warnings = [], []
    m = re.match(r"^([a-zA-Z][a-zA-Z0-9+.\-]*)://", url)
    if not m or m.group(1) not in ("http", "https"):
        return ([f"malformed http(s) link: {url}"], [])
    if live:
        req = urllib.request.Request(
            url, method="GET", headers={"User-Agent": "readme-doctor/0.2"})
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                if resp.status >= 400:
                    problems.append(f"dead link ({resp.status}): {url}")
        except urllib.error.HTTPError as e:
            problems.append(f"dead link ({e.code}): {url}")
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            warnings.append(f"unreachable (network, not proven dead): {url} [{e}]")
    return problems, warnings


def gate_links(text: str, ctx: dict) -> tuple[str, list[str], list[str]]:
    base_dir: Path = ctx["base_dir"]
    self_name: str = ctx["self_name"]
    live = ctx.get("live", False)
    problems, warnings = [], []

    urls, undefined = collect_link_info(text)
    problems += [f"undefined reference link: {u}" for u in undefined]

    for url in urls:
        if url.startswith("#") or url.startswith("mailto:"):
            continue
        path_part, _, frag = url.partition("#")
        if re.match(r"^[a-zA-Z][a-zA-Z0-9+.\-]*://", path_part):
            p, w = _check_http(path_part, live)
            problems, warnings = problems + p, warnings + w
            continue
        target = (base_dir / path_part).resolve()
        if not target.exists():
            problems.append(f"missing local target: {url}")
            continue
        if path_part and path_part != self_name and target.is_file() and frag:
            other_slugs = set(collect_headings(target.read_text(encoding="utf-8")))
            if frag not in other_slugs:
                problems.append(f"broken cross-file anchor: {url}")

    for src in collect_images(text):
        if re.match(r"^[a-zA-Z][a-zA-Z0-9+.\-]*://", src):
            p, w = _check_http(src, live)
            problems, warnings = problems + p, warnings + w
        elif not (base_dir / src).resolve().exists():
            problems.append(f"missing local image: {src}")
    return ("fail" if problems else "pass"), problems, warnings


def _name_pattern(name: str) -> re.Pattern:
    words = [w for w in re.split(r"[-_ ]+", name) if w]
    if not words:
        raise ValueError("empty project name")
    body = r"[-_ ]{0,3}".join(re.escape(w) for w in words)
    return re.compile(rf"(?<![A-Za-z0-9]){body}(?![A-Za-z0-9])", re.IGNORECASE)


CODE_SPAN_SPLIT = re.compile(r"(`[^`\n]+`)")


def fix_name_surfaces(text: str, name: str, allow: set[str] | None = None) -> tuple[str, int]:
    """Repair gate-3 FAIL drift: rewrite non-canonical PROSE surface forms to
    the canonical name. Fires only when prose carries more than one surface
    key (a single display surface is orthography, not drift) and never
    touches inline code spans (identifiers are code, not naming)."""
    allow = allow or set()
    segments = CODE_SPAN_SPLIT.split(text)
    prose = "".join(s for s in segments if not (s.startswith("`") and s.endswith("`")))
    pat = _name_pattern(name)
    allow_keys = {s.lower() for s in allow} | {name.lower()}
    keys = {m.group(0).lower() for m in pat.finditer(prose)} - allow_keys
    if len(keys) <= 1:
        return text, 0
    changes = 0

    def repl(m: re.Match) -> str:
        nonlocal changes
        if m.group(0).lower() in allow_keys:
            return m.group(0)
        changes += 1
        return name

    fixed_segments = [
        pat.sub(repl, s) if not (s.startswith("`") and s.endswith("`")) else s
        for s in segments
    ]
    return "".join(fixed_segments), changes


def fix_badge_styles(text: str) -> tuple[str, int]:
    """Append style=flat-square to shields.io badge image URLs missing it
    (gate 4's WARN class). Only flat-square is enforced; logos/labels are
    the author's business. Handles bare images and linked badges without
    disturbing the surrounding brackets."""
    changes = 0
    pat = re.compile(r"(!?)\[([^\]]*)\]\((https://img\.shields\.io/[^)]+)\)")

    def repl(m: re.Match) -> str:
        nonlocal changes
        url = m.group(3)
        if "style=flat-square" in url:
            return m.group(0)
        changes += 1
        styled = url + ("&" if "?" in url else "?") + "style=flat-square"
        return f"{m.group(1)}[{m.group(2)}]({styled})"

    return pat.sub(repl, text), changes


def gate_spelling(text: str, ctx: dict) -> tuple[str, list[str], list[str]]:
    name = ctx.get("name")
    if not name:
        first_h1 = re.search(r"^# (.+)$", strip_code_fences(text), re.MULTILINE)
        if not first_h1:
            return "skip", ["no --name given and no H1 to infer from"], []
        name = first_h1.group(1).strip()
    pat = _name_pattern(name)
    allow_keys = {s.lower() for s in ctx.get("allow", set())} | {name.lower()}
    haystack = strip_inline_code(strip_code_fences(text))
    counts: Counter = Counter(m.group(0) for m in pat.finditer(haystack))
    if not counts:
        return "skip", [f"no occurrence of project name {name!r} found"], []
    keys: dict[str, Counter] = {}
    for raw, n in counts.items():
        k = raw.lower()  # case-only variants are one form; separators are identity
        if k in allow_keys:
            continue
        keys.setdefault(k, Counter())[raw] += n
    if not keys:
        return "pass", [f"single surface form (modulo case): {name.lower()!r}"], []
    if len(keys) > 1:
        canonical = name.lower() if name.lower() in keys else max(
            keys, key=lambda k: sum(keys[k].values()))
        detail = ["project name appears in multiple surface forms; pick one "
                  f"(suggested canonical: {canonical!r}):"]
        for k, c in sorted(keys.items(), key=lambda kv: -sum(kv[1].values())):
            detail.append("  " + ", ".join(f"{n}x {raw!r}" for raw, n in c.most_common()))
        return "fail", detail, []
    return "pass", [f"single surface form (modulo case): {next(iter(keys))!r}"], []


def gate_badges(text: str, ctx: dict) -> tuple[str, list[str], list[str]]:
    problems, warnings = [], []
    badges = 0
    for line in strip_code_fences(text).splitlines():
        if not BADGE_LINE_RE.match(line):
            continue
        units = list(BADGE_RE.finditer(line)) + list(
            m for m in IMG_RE.finditer(BADGE_RE.sub("", line)))
        badges += len(units)
        for m in BADGE_RE.finditer(line):
            alt, img, href = m.group(1), m.group(2), m.group(3)
            if href in ("", "#"):
                problems.append(f"badge {alt!r} links nowhere ({href!r})")
            if "shields.io" in img and "style=flat-square" not in img:
                warnings.append(f"badge {alt!r} not flat-square: {img}")
        for m in IMG_RE.finditer(BADGE_RE.sub("", line)):
            if any(h in m.group(2) for h in BADGE_HOSTS):
                warnings.append(f"badge {m.group(1)!r} is an unlinked image "
                                f"(badges must link somewhere meaningful)")
    if badges > 4:
        problems.append(f"{badges} badges (max 4)")
    return ("fail" if problems else "pass"), problems, warnings


def gate_bilingual(text: str, ctx: dict) -> tuple[str, list[str], list[str]]:
    base_dir: Path = ctx["base_dir"]
    self_name: str = ctx["self_name"]
    zh: str | None = ctx.get("zh")
    problems, warnings = [], []

    urls, _ = collect_link_info(text)
    cross = []
    for url in urls:
        path_part = url.partition("#")[0]
        if (path_part.endswith(".md") and README_LANG_RE.match(Path(path_part).name)
                and path_part != self_name):
            cross.append(url)

    for url in cross:
        frag = url.partition("#")[2]
        target = base_dir / url.partition("#")[0]
        if not target.exists():
            problems.append(f"stale cross-language reference (file missing): {url}")
        elif frag:
            warnings.append(f"cross-language link carries a fragment "
                            f"(switch documents, not sections): {url}")

    if zh:
        zh_name = Path(zh).name  # --zh may be absolute or relative; compare by name
        zh_path = base_dir / zh
        if not zh_path.exists():
            problems.append(f"--zh file not found: {zh}")
        else:
            plain_to_zh = any(u.partition("#")[0] == zh_name for u in urls)
            if not plain_to_zh:
                problems.append(f"no switch line: {self_name} never links {zh_name}")
            zh_links = collect_links(zh_path.read_text(encoding="utf-8"))
            if not any(u.partition("#")[0] == self_name for u in zh_links):
                problems.append(f"switch line not bidirectional: {zh_name} never links {self_name}")
    else:
        for sibling in base_dir.glob("README*.md"):
            if sibling.name != self_name and not any(
                    u.partition("#")[0] == sibling.name for u in urls):
                warnings.append(f"translation on disk but unlinked: {sibling.name}")
    return ("fail" if problems else "pass"), problems, warnings


def gate_admonitions(text: str, ctx: dict) -> tuple[str, list[str], list[str]]:
    problems, warnings = [], []
    counts: Counter = Counter()
    for m in re.finditer(r"^\s{0,3}>\s*\[!\s*([A-Za-z]+)\s*\]", strip_code_fences(text),
                         re.MULTILINE):
        kind = m.group(1)
        if kind not in ADMONITION_TYPES:
            if kind.upper() in ADMONITION_TYPES:
                problems.append(f"wrong casing: [!{kind}] -> [!{kind.upper()}]")
            else:
                problems.append(f"unknown admonition: [!{kind}] "
                                f"(allowed: {', '.join(ADMONITION_TYPES)})")
        else:
            counts[kind] += 1
    for kind, n in counts.items():
        if n > 2:
            warnings.append(f"{n}x [!{kind}] -- admonitions mark policy, not "
                            "emphasis; 3+ of one type means prose failed")
    return ("fail" if problems else "pass"), problems, warnings


GATES = [
    ("anchors", "internal anchors resolve (GitHub slug rules, setext too)", gate_anchors),
    ("links", "link targets exist; reference links defined (GET when --live)", gate_links),
    ("spelling", "one canonical surface form of the project name", gate_spelling),
    ("badges", "<= 4 badges, meaningful hrefs, flat-square", gate_badges),
    ("bilingual", "bidirectional switch line, zero stale cross-refs", gate_bilingual),
    ("admonitions", "canonical [!TYPE] set, correct casing", gate_admonitions),
]


# ------------------------------------------------------------------ main ----

def run_doctor(readme: Path, args) -> int:
    text = readme.read_text(encoding="utf-8")
    fixes: list[str] = []
    if args.fix:
        text, n_badges = fix_badge_styles(text)
        if n_badges:
            fixes.append(f"{n_badges} badge URL(s) -> style=flat-square")
        if args.name:
            text, n_names = fix_name_surfaces(
                text, args.name, set(args.allow or []))
            if n_names:
                fixes.append(f"{n_names} drifted name occurrence(s) -> {args.name!r}")
        if fixes:
            readme.write_text(text, encoding="utf-8")
            for f in fixes:
                print(f"  fixed: {f}")
        else:
            print("  fix: nothing mechanical to repair")
    ctx = {
        "base_dir": readme.parent,
        "self_name": readme.name,
        "name": args.name,
        "zh": args.zh,
        "live": args.live,
        "allow": set(args.allow or []),
    }
    fails = 0
    report = {"file": str(readme), "name": args.name, "live": bool(args.live),
              "fixes": fixes, "gates": []}
    print(f"readme_doctor: {readme}"
          + ("  [live]" if args.live else "  [offline]"))
    for i, (name, desc, fn) in enumerate(GATES, 1):
        status, details, warnings = fn(text, ctx)
        tag = {"pass": "PASS", "fail": "FAIL", "skip": "SKIP"}[status]
        if warnings:
            tag += "+WARN"
        if status == "fail":
            fails += 1
        report["gates"].append({"gate": i, "name": name, "status": status,
                                "details": details, "warnings": warnings})
        print(f"  gate {i} {name:<11} {tag}  -- {desc}")
        for line in details:
            print(f"      {line}")
        for line in warnings:
            print(f"      WARN: {line}")
    summary = "ALL GREEN" if fails == 0 else f"{fails} GATE(S) FAILED"
    print(f"  -> {summary}")
    if args.json:
        report["failed_gates"] = fails
        print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if fails else 0


# --------------------------------------------------------------- selftest ----
# Dual anchors per gate: a fixture that MUST fire and one that MUST NOT
# (false-positive guard). File-based fixtures use a temp dir.

def _run_one(gate_fn, text: str, ctx: dict) -> str:
    status, _, _ = gate_fn(text, ctx)
    return status


def selftest() -> int:
    cases = []

    # gate 1 anchors
    cases.append(("1", "must-fire: emoji heading, wrong anchor", "fail",
                  gate_anchors, "## 🚀 Install\nsee [install](#install)\n", {}))
    cases.append(("1", "must-not-fire: emoji leading-hyphen anchor", "pass",
                  gate_anchors, "## 🚀 Install\nsee [install](#-install)\n", {}))
    cases.append(("1", "must-not-fire: duplicate heading suffix", "pass",
                  gate_anchors, "## Install\n## Install\n[a](#install) [b](#install-1)\n", {}))
    cases.append(("1", "must-not-fire: setext heading anchor", "pass",
                  gate_anchors, "Install\n========\nsee [install](#install)\n", {}))

    # gate 2 links
    cases.append(("2", "must-not-fire: well-formed https offline", "pass",
                  gate_links, "[x](https://example.com/a)\n", {"base_dir": Path("."), "self_name": "README.md"}))
    cases.append(("2", "must-fire: malformed scheme", "fail",
                  gate_links, "[x](htp:/oops)\n", {"base_dir": Path("."), "self_name": "README.md"}))
    cases.append(("2", "must-fire: undefined reference-style label", "fail",
                  gate_links, "[docs][nope]\n", {"base_dir": Path("."), "self_name": "README.md"}))

    # gate 3 spelling
    cases.append(("3", "must-fire: mixed surfaces", "fail",
                  gate_spelling, "# Lumina CLI\nUse lumina-cli or LuminaCLI.\n", {"name": "lumina-cli", "allow": set()}))
    cases.append(("3", "must-not-fire: single surface", "pass",
                  gate_spelling, "# lumina-cli\nlumina-cli rocks.\n", {"name": "lumina-cli", "allow": set()}))
    cases.append(("3", "must-not-fire: case-only variants are one form", "pass",
                  gate_spelling, "# glasswing\nGlasswing appears here too.\n",
                  {"name": "glasswing", "allow": set()}))
    cases.append(("3", "must-not-fire: prose display name + inline-code identifiers",
                  "pass", gate_spelling,
                  "# Agent Comparability\nAgent Comparability adjudicates records; "
                  "the module `agent_comparability` and package `agent-comparability` "
                  "are code surfaces.\n",
                  {"name": "agent-comparability", "allow": set()}))
    cases.append(("3", "must-not-fire: whitelist absorbs variant", "pass",
                  gate_spelling, "# lumina-cli\nLumina CLI in prose.\n",
                  {"name": "lumina-cli", "allow": {"Lumina CLI"}}))

    # gate 4 badges
    _b = lambda n, href="https://x": "\n".join(
        f"[![b{i}](https://img.shields.io/badge/b{i}-1?style=flat-square)]({href})" for i in range(n))
    cases.append(("4", "must-fire: 5 badges", "fail", gate_badges, _b(5), {}))
    _bare = "\n".join(
        f"![b{i}](https://img.shields.io/badge/b{i}-1)" for i in range(5))
    cases.append(("4", "must-fire: 5 bare-image badges (badge wall)", "fail",
                  gate_badges, _bare, {}))
    cases.append(("4", "must-fire: badge href '#'", "fail", gate_badges, _b(1, "#"), {}))
    cases.append(("4", "must-not-fire: 4 clean badges", "pass", gate_badges, _b(4), {}))

    def _badge_warn_case():
        text = "[![b](https://img.shields.io/badge/b-1)](https://x)\n"
        status, _, warnings = gate_badges(text, {})
        return "pass-with-warn" if status == "pass" and warnings else "other"

    def _anchor_suggest_case():
        status, details, _ = gate_anchors("## Install\nsee [go](#instal)\n", {})
        ok = status == "fail" and any("did you mean" in d for d in details)
        return "fail-with-suggestion" if ok else "other"

    # gate 5 bilingual (file-dependent cases run in the temp dir below)

    # gate 6 admonitions
    cases.append(("6", "must-fire: lowercase [!important]", "fail",
                  gate_admonitions, "> [!important]\nboundary\n", {}))
    cases.append(("6", "must-fire: unknown [!URGENT]", "fail",
                  gate_admonitions, "> [!URGENT]\nread me\n", {}))
    cases.append(("6", "must-not-fire: canonical IMPORTANT", "pass",
                  gate_admonitions, "> [!IMPORTANT]\nboundary\n", {}))

    failed = 0
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)

        def _link_file_cases():
            (tmp / "exists.md").write_text("# Real\n", encoding="utf-8")
            (tmp / "README.md").write_text("[a](exists.md#real) [b](gone.md)\n", encoding="utf-8")
            text = (tmp / "README.md").read_text(encoding="utf-8")
            return [
                ("2", "must-fire: missing relative target + bad cross-file frag", "fail",
                 gate_links, text, {"base_dir": tmp, "self_name": "README.md"}),
                ("2", "must-not-fire: existing target, valid cross-file frag", "pass",
                 gate_links, "[a](exists.md#real)\n", {"base_dir": tmp, "self_name": "README.md"}),
                ("2", "must-not-fire: defined reference-style link resolves", "pass",
                 gate_links, "[docs][guide]\n\n[guide]: exists.md#real\n",
                 {"base_dir": tmp, "self_name": "README.md"}),
                ("1", "must-fire: reference link to missing fragment", "fail",
                 gate_anchors, "[top][up]\n\n[up]: #nope\n", {}),
            ]

        def _zh_cases():
            (tmp / "README.md").write_text(
                "**English** | [zh](README.zh-CN.md)\n", encoding="utf-8")
            (tmp / "README.zh-CN.md").write_text(
                "[en](README.md) | **zh**\n", encoding="utf-8")
            (tmp2 := tmp / "no-back")
            tmp2.mkdir()
            (tmp2 / "README.md").write_text("[zh](README.zh-CN.md)\n", encoding="utf-8")
            (tmp2 / "README.zh-CN.md").write_text("no back link\n", encoding="utf-8")
            (tmp3 := tmp / "stale")
            tmp3.mkdir()
            return [
                ("5", "must-not-fire: bidirectional pair", "pass", gate_bilingual,
                 (tmp / "README.md").read_text(encoding="utf-8"),
                 {"base_dir": tmp, "self_name": "README.md", "zh": "README.zh-CN.md"}),
                ("5", "must-fire: missing reverse switch line", "fail", gate_bilingual,
                 (tmp2 / "README.md").read_text(encoding="utf-8"),
                 {"base_dir": tmp2, "self_name": "README.md", "zh": "README.zh-CN.md"}),
                ("5", "must-fire: stale zh reference (file missing)", "fail",
                 gate_bilingual, "[zh](README.zh-CN.md#quick-start)\n",
                 {"base_dir": tmp3, "self_name": "README.md"}),
                ("5", "must-not-fire: --zh given as absolute path", "pass",
                 gate_bilingual,
                 (tmp / "README.md").read_text(encoding="utf-8"),
                 {"base_dir": tmp, "self_name": "README.md",
                  "zh": str((tmp / "README.zh-CN.md").resolve())}),
            ]

        cases += _link_file_cases()
        cases += _zh_cases()
        for gate, label, expect, fn, text, ctx in cases:
            got = _run_one(fn, text, ctx)
            ok = (got == expect)
            if not ok:
                failed += 1
            print(f"  [{'PASS' if ok else 'FAIL'}] gate {gate} selftest: {label} "
                  f"(expected {expect}, got {got})")
        warn_probe = _badge_warn_case()
        ok = warn_probe == "pass-with-warn"
        if not ok:
            failed += 1
        print(f"  [{'PASS' if ok else 'FAIL'}] gate 4 selftest: non-flat-square "
              f"badge warns without failing (got {warn_probe})")
        suggest_probe = _anchor_suggest_case()
        ok = suggest_probe == "fail-with-suggestion"
        if not ok:
            failed += 1
        print(f"  [{'PASS' if ok else 'FAIL'}] gate 1 selftest: broken anchor "
              f"carries nearest-slug suggestion (got {suggest_probe})")

        def _fix_badge_probe():
            linked = "[![a](https://img.shields.io/badge/a-1?logo=x)](https://x)"
            bare = "![b](https://img.shields.io/badge/b-2)"
            new, n = fix_badge_styles(linked + "\n" + bare)
            ok = (n == 2 and "[[!" not in new
                  and "a-1?logo=x&style=flat-square" in new
                  and f"{bare.split('(')[0]}(https://img.shields.io/badge/b-2?style=flat-square)" in new
                  and linked.split("](")[1].split("?")[0] in new)
            return f"fixed-{n}" if ok else "other"

        def _fix_name_probe():
            drift = ("# lumina-cli\nLumina CLI and LuminaCLI differ; "
                     "keep `agent_comparability` untouched.\n")
            new, n = fix_name_surfaces(drift, "lumina-cli")
            ok = (n == 2 and "Lumina CLI" not in new and "LuminaCLI" not in new
                  and "`agent_comparability`" in new)
            return f"fixed-{n}" if ok else "other"

        def _fix_name_noop_probe():
            single = ("# Agent Comparability\nAgent Comparability is fine; "
                      "`agent_comparability` is code.\n")
            new, n = fix_name_surfaces(single, "agent-comparability")
            ok = n == 0 and new == single
            return "noop" if ok else "other"

        for label, probe, expect in [
                ("badge style autofix handles linked + bare without bracket damage",
                 _fix_badge_probe, "fixed-2"),
                ("name drift fixer rewrites prose, spares inline code", _fix_name_probe, "fixed-2"),
                ("name fixer no-ops on a single display surface", _fix_name_noop_probe, "noop")]:
            got = probe()
            ok = got == expect
            if not ok:
                failed += 1
            print(f"  [{'PASS' if ok else 'FAIL'}] --fix selftest: {label} (got {got})")
    total = len(cases) + 5
    print(f"selftest: {total - failed}/{total} green")
    return 1 if failed else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("readme", nargs="?", help="README file to check")
    ap.add_argument("--name", help="canonical project name (default: inferred from H1)")
    ap.add_argument("--zh", help="companion translation file, e.g. README.zh-CN.md")
    ap.add_argument("--live", action="store_true",
                    help="liveness-check http(s) links with GET (default: offline)")
    ap.add_argument("--allow", action="append", default=[],
                    help="whitelist an extra surface form of the name (repeatable)")
    ap.add_argument("--json", action="store_true",
                    help="also print a machine-readable JSON report (for CI/agent loops)")
    ap.add_argument("--fix", action="store_true",
                    help="repair mechanical defect classes in place (badge style, "
                         "drifted prose name surfaces); judgment repairs stay manual")
    ap.add_argument("--selftest", action="store_true",
                    help="run the built-in dual-anchor fixtures and exit")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    if not args.readme:
        ap.error("provide a README file, or --selftest")
    readme = Path(args.readme)
    if not readme.exists():
        print(f"no such file: {readme}", file=sys.stderr)
        return 2
    return run_doctor(readme, args)


if __name__ == "__main__":
    sys.exit(main())
