#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mcp_server.py -- expose the readme-anatomy toolchain as MCP tools over stdio. (v0.1)

Lets an agent session call the seven gates, the scaffold generator, and the
skill validator natively (no shell round-trip), following the house MCP
convention: newline-delimited JSON-RPC 2.0 on stdio, no SDK dependency.

Tools
  readme_doctor    run the seven gates on a README; optional in-place --fix;
                   returns the structured report (fixes, per-gate results)
  readme_scaffold  generate a gates-clean bilingual README skeleton
  validate_skill   validate a SKILL.md against the agentskills.io spec

Usage
  python scripts/mcp_server.py            # serve on stdio
  python scripts/mcp_server.py --selftest # dual-anchor selftest (spawns self)

Wire format (one JSON object per line):
  -> {"jsonrpc":"2.0","id":1,"method":"initialize","params":{...}}
  <- {"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2025-06-18",
       "capabilities":{"tools":{"listChanged":false}},"serverInfo":{...}}}
  then tools/list, tools/call; ping; notifications/* are ignored.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import readme_doctor  # noqa: E402
from readme_doctor import run_gates  # noqa: E402
from readme_scaffold import TYPES, render_en, render_zh  # noqa: E402
from validate_skill import validate as validate_skill_dir  # noqa: E402
from claims_probe import probe as claims_probe_run  # noqa: E402

PROTOCOL_VERSION = "2025-06-18"
SERVER_INFO = {"name": "readme-anatomy", "version": "0.10.1"}


# ------------------------------------------------------------------ tools ----

def t_readme_doctor(a: dict):
    readme = Path(a["readme"])
    if not readme.exists():
        raise ValueError(f"no such file: {readme}")
    report = run_gates(
        readme, name=a.get("name"), zh=a.get("zh"),
        live=bool(a.get("live", False)), allow=a.get("allow", []),
        fix=bool(a.get("fix", False)), dry_run=bool(a.get("dry_run", False)))
    text = (f"{readme}: {report['summary']}"
            + (f"; fixed: {'; '.join(report['fixes'])}" if report["fixes"] else ""))
    return report, text


def t_readme_scaffold(a: dict):
    name = a.get("name") or ""
    if not name:
        raise ValueError("name is required")
    typ = a.get("type", "library")
    if typ not in TYPES:
        raise ValueError(f"type must be one of {TYPES}")
    lang = a.get("lang", "both")
    out = Path(a.get("out_dir", "."))
    force = bool(a.get("force", False))
    plan = {
        "en": [("README.md", lambda: render_en(name, typ))],
        "zh": [("README.zh-CN.md", lambda: render_zh(name, typ))],
        "both": [("README.md", lambda: render_en(name, typ, bilingual=True)),
                 ("README.zh-CN.md", lambda: render_zh(name, typ))],
    }[lang]
    written = []
    for fname, render in plan:
        target = out / fname
        if target.exists() and not force:
            raise ValueError(f"refusing to overwrite {target} (pass force=true)")
        target.write_text(render(), encoding="utf-8")
        written.append(str(target))
    return ({"written": written,
             "note": "skeleton passes the gates by construction; every "
                     "<placeholder> is a claim awaiting its tier"},
            "wrote " + ", ".join(written))


def t_validate_skill(a: dict):
    skill_dir = Path(a.get("skill_dir") or HERE.parent)
    fails, warns = validate_skill_dir(skill_dir)
    text = f"validate_skill: {'FAIL' if fails else 'PASS'} " \
           f"({len(fails)} failure(s), {len(warns)} warning(s))"
    return {"failures": fails, "warnings": warns,
            "summary": "FAIL" if fails else "PASS"}, text


def t_claims_probe(a: dict):
    readme = Path(a["readme"])
    if not readme.exists():
        raise ValueError(f"no such file: {readme}")
    report = claims_probe_run(readme, run=bool(a.get("run", False)))
    return report, f"{readme}: {report['summary']}"


def _obj(props: dict, required: list[str] | None = None) -> dict:
    return {"type": "object", "properties": props,
            "required": required or [], "additionalProperties": False}


TOOLS = [
    {"name": "readme_doctor", "title": "README gates",
     "description": ("Run the seven readme-anatomy gates (anchors, links, "
                     "spelling, badges, bilingual, admonitions, cross-surface "
                     "consistency) on a README. Pass fix=true to repair the "
                     "mechanical classes in place (TOC, badge style, prose-name "
                     "drift). live=true GET-probes external links."),
     "inputSchema": _obj({
         "readme": {"type": "string", "description": "path to the README file"},
         "name": {"type": "string", "description": "canonical project name"},
         "zh": {"type": "string", "description": "companion translation, e.g. README.zh-CN.md"},
         "live": {"type": "boolean", "description": "GET-probe external links (default offline)"},
         "fix": {"type": "boolean", "description": "apply mechanical fixes in place"},
         "dry_run": {"type": "boolean", "description": "compute the fix set, return a unified diff, never write"},
         "allow": {"type": "array", "items": {"type": "string"},
                   "description": "extra whitelisted surface forms of the name"},
     }, ["readme"]),
     "handler": t_readme_doctor},
    {"name": "readme_scaffold", "title": "README skeleton generator",
     "description": ("Generate a gates-clean README skeleton (the 'new' task "
                     "mode). Output passes the gates by construction; every "
                     "<placeholder> is a claim awaiting its tier."),
     "inputSchema": _obj({
         "name": {"type": "string", "description": "canonical project name"},
         "type": {"type": "string", "enum": list(TYPES)},
         "lang": {"type": "string", "enum": ["en", "zh", "both"]},
         "out_dir": {"type": "string", "description": "output directory (default .)"},
         "force": {"type": "boolean", "description": "overwrite existing files"},
     }, ["name"]),
     "handler": t_readme_scaffold},
    {"name": "validate_skill", "title": "agentskills.io spec validation",
     "description": ("Validate a SKILL.md against the agentskills.io spec "
                     "(frontmatter constraints, name==directory, <=500-line "
                     "body). Defaults to this skill's own directory."),
     "inputSchema": _obj({
         "skill_dir": {"type": "string", "description": "skill directory (default: this skill)"},
     }, []),
     "handler": t_validate_skill},
    {"name": "claims_probe", "title": "evidence-table verification",
     "description": ("READU-style check of the evidence table's Where column: "
                     "paths exist, cross-file anchors resolve, line numbers are "
                     "in range, commands are on PATH (run=true executes them "
                     "with a 10s timeout and checks exit codes -- a trust "
                     "decision). Prose or URL-only cells WARN."),
     "inputSchema": _obj({
         "readme": {"type": "string", "description": "path to the README with the evidence table"},
         "run": {"type": "boolean", "description": "execute commands to check exit codes (default offline)"},
     }, ["readme"]),
     "handler": t_claims_probe},
]

BY_NAME = {t["name"]: t for t in TOOLS}


# ---------------------------------------------------------- JSON-RPC loop ----

def _write(obj: dict):
    sys.stdout.write(json.dumps(obj, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def handle(msg: dict):
    method = msg.get("method", "")
    mid = msg.get("id")
    if method == "initialize":
        _write({"jsonrpc": "2.0", "id": mid, "result": {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {"tools": {"listChanged": False}},
            "serverInfo": SERVER_INFO}})
    elif method == "tools/list":
        _write({"jsonrpc": "2.0", "id": mid, "result": {
            "tools": [{k: t[k] for k in ("name", "title", "description", "inputSchema")}
                      for t in sorted(TOOLS, key=lambda t: t["name"])]}})
    elif method == "tools/call":
        params = msg.get("params") or {}
        tool = BY_NAME.get(params.get("name"))
        if tool is None:
            _write({"jsonrpc": "2.0", "id": mid, "error": {"code": -32602,
                    "message": f"Unknown tool: {params.get('name')!r}"}})
            return
        try:
            structured, text = tool["handler"](params.get("arguments") or {})
        except Exception as e:  # noqa: BLE001 — execution errors are model-recoverable
            _write({"jsonrpc": "2.0", "id": mid, "result": {
                "content": [{"type": "text", "text": f"{type(e).__name__}: {e}"}],
                "isError": True}})
            return
        _write({"jsonrpc": "2.0", "id": mid, "result": {
            "content": [{"type": "text", "text": text}],
            "structuredContent": structured, "isError": False}})
    elif method == "ping":
        _write({"jsonrpc": "2.0", "id": mid, "result": {}})
    elif method.startswith("notifications/"):
        pass
    elif mid is not None:
        _write({"jsonrpc": "2.0", "id": mid,
                "error": {"code": -32601, "message": f"Method not found: {method}"}})


def serve():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except ValueError:
            continue
        try:
            handle(msg)
        except Exception as e:  # noqa: BLE001 — the server must survive handler bugs
            if msg.get("id") is not None:
                _write({"jsonrpc": "2.0", "id": msg["id"],
                        "error": {"code": -32603,
                                  "message": f"internal error: {type(e).__name__}: {e}"}})


# --------------------------------------------------------------- selftest ----
# Dual anchors: each capability gets a must-fire and a must-not-fire probe,
# driven through a real child process over the real wire (not direct calls).

def selftest() -> int:
    fails = []

    def check(name, ok, detail=""):
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f": {detail}" if detail else ""))
        if not ok:
            fails.append(name)

    with tempfile.TemporaryDirectory() as td:
        proc = subprocess.Popen(
            [sys.executable, str(Path(__file__).resolve())],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            text=True, encoding="utf-8")
        mid = [0]

        def rpc(method, params=None):
            mid[0] += 1
            req = {"jsonrpc": "2.0", "id": mid[0], "method": method}
            if params is not None:
                req["params"] = params
            proc.stdin.write(json.dumps(req, ensure_ascii=False) + "\n")
            proc.stdin.flush()
            while True:
                line = proc.stdout.readline()
                if not line:
                    raise RuntimeError("server closed the stream")
                resp = json.loads(line)
                if resp.get("id") == mid[0]:
                    return resp

        def call(tool, args):
            return rpc("tools/call", {"name": tool, "arguments": args})

        # -- handshake & discovery (must-not-fire: sane surface) --
        r = rpc("initialize")
        info = r.get("result", {}).get("serverInfo", {})
        check("initialize handshake returns serverInfo",
              info.get("name") == "readme-anatomy", str(info))
        r = rpc("tools/list")
        names = sorted(t["name"] for t in r.get("result", {}).get("tools", []))
        check("tools/list exposes the four tools",
              names == ["claims_probe", "readme_doctor", "readme_scaffold",
                        "validate_skill"],
              ",".join(names))

        # -- readme_doctor: report shape (stable across release windows --
        # asserting "own README is green" would fail every version bump) --
        good = Path(HERE.parent / "README.md").resolve()
        r = call("readme_doctor", {"readme": str(good), "name": "readme-anatomy",
                                   "zh": "README.zh-CN.md"})
        rep = r["result"]["structuredContent"]
        check("readme_doctor returns the full seven-gate report",
              len(rep["gates"]) == 7
              and isinstance(rep["failed_gates"], int)
              and rep["summary"].endswith("GREEN") == (rep["failed_gates"] == 0),
              rep["summary"])

        # -- readme_doctor: must-fire (the desensitized pre-rework sample fails) --
        bad = Path(HERE.parent / "assets" / "before.md").resolve()
        r = call("readme_doctor", {"readme": str(bad), "name": "glasswing"})
        rep = r["result"]["structuredContent"]
        check("readme_doctor on the pre-rework sample: gates FAIL",
              rep["failed_gates"] >= 1, rep["summary"])

        # -- readme_doctor: must-fire (missing path is an error result, not a crash) --
        r = call("readme_doctor", {"readme": str(Path(td) / "nope.md")})
        check("readme_doctor on missing file: isError, server survives",
              r["result"].get("isError") is True)

        # -- readme_scaffold: round-trip (must-not-fire: generated output is
        # green by construction, independent of this repo's release state) --
        out_dir = Path(td) / "scaffold"
        out_dir.mkdir()
        r = call("readme_scaffold", {"name": "demo-tool", "type": "cli-tool",
                                     "lang": "both", "out_dir": str(out_dir)})
        written = r["result"]["structuredContent"]["written"]
        r = call("readme_doctor", {"readme": written[0], "name": "demo-tool",
                                   "zh": "README.zh-CN.md"})
        check("scaffold output passes all seven gates through the wire",
              r["result"]["structuredContent"]["failed_gates"] == 0)

        # -- validate_skill (must-not-fire: this repo passes) --
        r = call("validate_skill", {})
        check("validate_skill on this repo: PASS",
              r["result"]["structuredContent"]["summary"] == "PASS")

        # -- claims_probe (must-not-fire: this repo's evidence table verifies) --
        r = call("claims_probe", {"readme": str(good)})
        rep = r["result"]["structuredContent"]
        check("claims_probe on this repo's evidence table: 0 FAIL",
              rep["failed"] == 0, rep["summary"])

        # -- dry_run preview over the wire (must-not-fire: never writes) --
        scratch = Path(td) / "scratch"
        scratch.mkdir()
        scratch_file = scratch / "README.md"
        scratch_file.write_text("# Lumina CLI\n\nLuminaCLI drift.\n", encoding="utf-8")
        before = scratch_file.read_text(encoding="utf-8")
        r = call("readme_doctor", {"readme": str(scratch_file), "name": "lumina-cli",
                                   "dry_run": True})
        rep = r["result"]["structuredContent"]
        check("dry_run returns a diff and leaves the file untouched",
              bool(rep.get("fixes")) and "-LuminaCLI" in (rep.get("diff") or "")
              and scratch_file.read_text(encoding="utf-8") == before)

        # -- protocol guards (must-fire: bogus names are refused) --
        r = call("no_such_tool", {})
        check("unknown tool -> JSON-RPC -32602",
              r.get("error", {}).get("code") == -32602)
        r = rpc("no/such/method")
        check("unknown method -> JSON-RPC -32601",
              r.get("error", {}).get("code") == -32601)

        proc.stdin.close()
        proc.wait(timeout=10)

    print(f"selftest: {11 - len(fails)}/11 green")
    return 1 if fails else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--selftest", action="store_true",
                    help="run the dual-anchor selftest (spawns a child server) and exit")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    serve()
    return 0


if __name__ == "__main__":
    sys.exit(main())
