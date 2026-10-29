#!/usr/bin/env python3
"""ledger_probe.py -- link-liveness probe for markdown ledgers (stdlib only).

Decay-watchlist item 8 automation (references/research.md): the anchor
ledger's links rot silently; this probe turns that rot into a red light
instead of a manual re-verification ritual.  It parses every http(s) URL in
a markdown file, GETs each unique one (10s timeout,
User-Agent ledger-probe/0.1), and classifies the outcome:

  HTTP < 400 (after redirects)      alive
  HTTP >= 400                       DEAD -> listed, exit 1 (real rot: the
                                    only class this tool fails on)
  URLError / timeout / socket error WARN -> exit 0 (network weather is not
                                    rot evidence -- a probe that fails on a
                                    flaky mirror cries wolf, per the
                                    decay-watch stance)

Every http(s) span is a candidate -- quotes and code fences included (a
ledger cites anchors, it does not carry fixture snippets).  Extraction
trims trailing markdown punctuation; a trailing ')' survives only while the
URL's own parentheses stay balanced, so wiki-style ``Page_(x)`` links keep
their close paren while markdown link wrappers ``[t](url)`` do not leak one
into the URL.

Usage:
    python scripts/ledger_probe.py <mdfile>          # human-readable report
    python scripts/ledger_probe.py <mdfile> --json   # machine-readable report

Exit codes: 0 = no dead links (dead links are the only failure class),
1 = at least one dead link, 2 = usage error.  Read-only.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

USER_AGENT = "ledger-probe/0.1"
TIMEOUT_S = 10.0

_URL_RE = re.compile(r"""https?://[^\s<>"'`|]+""", re.IGNORECASE)
_TRAILING_PUNCT = ".,;:!?"


def clean_url(raw: str) -> str:
    """Trim markdown's trailing punctuation without eating URL content."""
    url = raw.rstrip(_TRAILING_PUNCT)
    while url.endswith(")") and url.count("(") < url.count(")"):
        url = url[:-1].rstrip(_TRAILING_PUNCT)
    return url


def collect_urls(text: str) -> list[tuple[str, int]]:
    """Unique http(s) URLs with their first-seen 1-based line number,
    in document order.  One URL, one GET -- duplicates add lines, not
    requests."""
    seen: dict[str, int] = {}
    for lineno, line in enumerate(text.splitlines(), start=1):
        for m in _URL_RE.finditer(line):
            url = clean_url(m.group(0))
            if url and url not in seen:
                seen[url] = lineno
    return sorted(seen.items(), key=lambda kv: kv[1])


def probe_url(url: str) -> tuple[str, str]:
    """('ok' | 'dead' | 'warn', detail) for one URL.  HTTPError must be
    caught before URLError: it IS a URLError, but its .code is a real HTTP
    verdict, not weather."""
    req = Request(url, headers={"User-Agent": USER_AGENT}, method="GET")
    try:
        with urlopen(req, timeout=TIMEOUT_S) as resp:  # noqa: S310 -- probe by contract
            return "ok", f"HTTP {resp.status}"
    except HTTPError as e:
        if e.code >= 400:
            return "dead", f"HTTP {e.code}"
        return "ok", f"HTTP {e.code}"
    except (URLError, OSError, ValueError) as e:
        return "warn", f"{type(e).__name__}: {e}"


def probe_file(path: Path) -> dict:
    """Probe every link in `path`; returns the report dict (never mutates)."""
    text = path.read_text(encoding="utf-8")
    urls = collect_urls(text)
    dead: list[dict] = []
    warned: list[dict] = []
    alive = 0
    for url, lineno in urls:
        status, detail = probe_url(url)
        if status == "dead":
            dead.append({"url": url, "line": lineno, "detail": detail})
        elif status == "warn":
            warned.append({"url": url, "line": lineno, "detail": detail})
        else:
            alive += 1
    return {"file": str(path), "checked": len(urls), "alive": alive,
            "dead": dead, "warned": warned, "passed": not dead}


def render(report: dict) -> list[str]:
    out = [f"ledger_probe: {report['file']}"]
    for d in report["dead"]:
        out.append(f"  DEAD line {d['line']}: {d['url']} ({d['detail']})")
    for w in report["warned"]:
        out.append(f"  WARN line {w['line']}: {w['url']} ({w['detail']})")
    out.append(f"  -> {report['checked']} link(s): {report['alive']} alive, "
               f"{len(report['dead'])} dead, {len(report['warned'])} warn "
               f"(network weather warns; only HTTP >= 400 fails)")
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Link-liveness probe for markdown ledgers "
                    "(dead links fail; network weather warns).")
    ap.add_argument("file", help="markdown file whose http(s) links to probe")
    ap.add_argument("--json", action="store_true",
                    help="emit the report as JSON")
    args = ap.parse_args(argv)
    path = Path(args.file)
    if not path.is_file():
        print(f"ledger_probe: no such file: {path}", file=sys.stderr)
        return 2
    report = probe_file(path)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print("\n".join(render(report)))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
