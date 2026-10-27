#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
readme_doctor.py -- six machine gates for README craft.

Gates
  1 anchors      internal anchor links resolve under GitHub slug rules
                 (emoji-prefixed headings produce a LEADING HYPHEN:
                 "## Install" -> #install, "## 🚀 Install" -> #-install;
                 duplicate headings get -1, -2 suffixes)
  2 links        relative targets exist on disk (and cross-file fragments
                 resolve); http(s) links are syntax-checked offline and
                 liveness-checked with --live using GET -- raw.githubusercontent
                 and similar endpoints reject HEAD, which causes false 404s
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
                                        [--allow SURFACE] ...
  python scripts/readme_doctor.py --selftest

Exit code 0 = no FAIL. WARN never fails the run. Stdlib only; offline by
default so runs are reproducible in CI.

Known limitations (v0.1): reference-style links ([text][ref]) are not
collected; setext headings (=== underline) are not parsed; admonition
semantics (which box for which job) are audited by the agent against
references/claims-posture.md, not by this script.
"""
from __future__ import annotations

import argparse
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
    seen: Counter = Counter()
    slugs = []
    for line in strip_code_fences(text).splitlines():
        m = re.match(r"^(#{1,6})\s+(.+?)\s*#*\s*$", line)
        if m:
            slugs.append(github_slug(m.group(2), seen))
    return slugs


LINK_RE = re.compile(r"(?<!\!)\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
BADGE_RE = re.compile(r"\[!\[([^\]]*)\]\(([^)]+)\)\]\(([^)]+)\)")
IMG_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
# a badge line: a line consisting solely of bare images and/or linked images
BADGE_LINE_RE = re.compile(
    r"^\s{0,3}(?:\s*(?:\[!\[[^\]]*\]\([^)]+\)\]\([^)]+\)|!\[[^\]]*\]\([^)]+\)))+\s*$")
BADGE_HOSTS = ("shields.io", "badgen.net", "badgecdn.com", "badge.fury.io")


def collect_links(text: str) -> list[str]:
    """Normal markdown links (anchors included). Linked-badge constructs are
    masked first so their inner image URL is not misread as a link target."""
    stripped = strip_code_fences(text)
    masked = BADGE_RE.sub("[badge]", stripped)
    return [m.group(1) for m in LINK_RE.finditer(masked)]


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
            problems.append(f"broken anchor: #{frag}")
    return ("fail" if problems else "pass"), problems, []


def _check_http(url: str, live: bool) -> tuple[list[str], list[str]]:
    problems, warnings = [], []
    m = re.match(r"^([a-zA-Z][a-zA-Z0-9+.\-]*)://", url)
    if not m or m.group(1) not in ("http", "https"):
        return ([f"malformed http(s) link: {url}"], [])
    if live:
        req = urllib.request.Request(
            url, method="GET", headers={"User-Agent": "readme-doctor/0.1"})
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

    for url in collect_links(text):
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


def gate_spelling(text: str, ctx: dict) -> tuple[str, list[str], list[str]]:
    name = ctx.get("name")
    if not name:
        first_h1 = re.search(r"^# (.+)$", strip_code_fences(text), re.MULTILINE)
        if not first_h1:
            return "skip", ["no --name given and no H1 to infer from"], []
        name = first_h1.group(1).strip()
    pat = _name_pattern(name)
    allow_keys = {s.lower() for s in ctx.get("allow", set())} | {name.lower()}
    counts: Counter = Counter(m.group(0) for m in pat.finditer(strip_code_fences(text)))
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

    cross = []
    for url in collect_links(text):
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
        main = base_dir / self_name
        zh_path = base_dir / zh
        if not zh_path.exists():
            problems.append(f"--zh file not found: {zh}")
        else:
            plain_to_zh = any(u.partition("#")[0] == zh for u in collect_links(text))
            if not plain_to_zh:
                problems.append(f"no switch line: {self_name} never links {zh}")
            zh_links = collect_links(zh_path.read_text(encoding="utf-8"))
            if not any(u.partition("#")[0] == self_name for u in zh_links):
                problems.append(f"switch line not bidirectional: {zh} never links {self_name}")
    else:
        for sibling in base_dir.glob("README*.md"):
            if sibling.name != self_name and not any(
                    u.partition("#")[0] == sibling.name for u in collect_links(text)):
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
    ("anchors", "internal anchors resolve (GitHub slug rules)", gate_anchors),
    ("links", "link targets exist (GET, not HEAD, when --live)", gate_links),
    ("spelling", "one canonical surface form of the project name", gate_spelling),
    ("badges", "<= 4 badges, meaningful hrefs, flat-square", gate_badges),
    ("bilingual", "bidirectional switch line, zero stale cross-refs", gate_bilingual),
    ("admonitions", "canonical [!TYPE] set, correct casing", gate_admonitions),
]


# ------------------------------------------------------------------ main ----

def run_doctor(readme: Path, args) -> int:
    text = readme.read_text(encoding="utf-8")
    ctx = {
        "base_dir": readme.parent,
        "self_name": readme.name,
        "name": args.name,
        "zh": args.zh,
        "live": args.live,
        "allow": set(args.allow or []),
    }
    fails = 0
    print(f"readme_doctor: {readme}"
          + ("  [live]" if args.live else "  [offline]"))
    for i, (name, desc, fn) in enumerate(GATES, 1):
        status, details, warnings = fn(text, ctx)
        tag = {"pass": "PASS", "fail": "FAIL", "skip": "SKIP"}[status]
        if warnings:
            tag += "+WARN"
        if status == "fail":
            fails += 1
        print(f"  gate {i} {name:<11} {tag}  -- {desc}")
        for line in details:
            print(f"      {line}")
        for line in warnings:
            print(f"      WARN: {line}")
    print(f"  -> {'ALL GREEN' if fails == 0 else str(fails) + ' GATE(S) FAILED'}")
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

    # gate 2 links
    cases.append(("2", "must-not-fire: well-formed https offline", "pass",
                  gate_links, "[x](https://example.com/a)\n", {"base_dir": Path("."), "self_name": "README.md"}))
    cases.append(("2", "must-fire: malformed scheme", "fail",
                  gate_links, "[x](htp:/oops)\n", {"base_dir": Path("."), "self_name": "README.md"}))

    def _link_file_cases(tmp: Path):
        (tmp / "exists.md").write_text("# Real\n", encoding="utf-8")
        (tmp / "README.md").write_text("[a](exists.md#real) [b](gone.md)\n", encoding="utf-8")
        text = (tmp / "README.md").read_text(encoding="utf-8")
        return [
            ("2", "must-fire: missing relative target + bad cross-file frag", "fail",
             gate_links, text, {"base_dir": tmp, "self_name": "README.md"}),
            ("2", "must-not-fire: existing target, valid cross-file frag", "pass",
             gate_links, "[a](exists.md#real)\n", {"base_dir": tmp, "self_name": "README.md"}),
        ]

    # gate 3 spelling
    cases.append(("3", "must-fire: mixed surfaces", "fail",
                  gate_spelling, "# Lumina CLI\nUse lumina-cli or LuminaCLI.\n", {"name": "lumina-cli", "allow": set()}))
    cases.append(("3", "must-not-fire: single surface", "pass",
                  gate_spelling, "# lumina-cli\nlumina-cli rocks.\n", {"name": "lumina-cli", "allow": set()}))
    cases.append(("3", "must-not-fire: case-only variants are one form", "pass",
                  gate_spelling, "# glasswing\nGlasswing appears here too.\n",
                  {"name": "glasswing", "allow": set()}))
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

    # gate 5 bilingual
    cases.append(("5", "must-fire: stale zh reference", "fail",
                  gate_bilingual, "[zh](README.zh-CN.md#quick-start)\n",
                  {"base_dir": Path("."), "self_name": "README.md"}))

    def _zh_cases(tmp: Path):
        (tmp / "README.md").write_text(
            "**English** | [zh](README.zh-CN.md)\n", encoding="utf-8")
        (tmp / "README.zh-CN.md").write_text(
            "[en](README.md) | **zh**\n", encoding="utf-8")
        (tmp2 := Path(tempfile.mkdtemp(dir=tmp)))
        (tmp2 / "README.md").write_text("[zh](README.zh-CN.md)\n", encoding="utf-8")
        (tmp2 / "README.zh-CN.md").write_text("no back link\n", encoding="utf-8")
        return [
            ("5", "must-not-fire: bidirectional pair", "pass", gate_bilingual,
             (tmp / "README.md").read_text(encoding="utf-8"),
             {"base_dir": tmp, "self_name": "README.md", "zh": "README.zh-CN.md"}),
            ("5", "must-fire: missing reverse switch line", "fail", gate_bilingual,
             (tmp2 / "README.md").read_text(encoding="utf-8"),
             {"base_dir": tmp2, "self_name": "README.md", "zh": "README.zh-CN.md"}),
        ]

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
        cases += _link_file_cases(tmp)
        cases += _zh_cases(tmp)
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
    total = len(cases) + 1
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
