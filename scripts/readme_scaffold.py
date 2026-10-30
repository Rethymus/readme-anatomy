#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
readme_scaffold.py -- generate a gates-clean README skeleton (v0.1).

Implements SKILL.md mode **new**: the four questions give you the content,
this gives you the shape. Output is constructed to pass readme_doctor.py's
offline gates: anchors are computed with the doctor's own slug function,
badges are <= 4 and flat-square, the name appears in exactly one surface,
and bilingual output ships a bidirectional switch line plus the
source-of-truth [!NOTE]. The skeleton is a questionnaire, not a finished
document -- every <placeholder> is a claim awaiting its tier, and evidence
rows ship with Status `not-run` until their Where check has actually run
(references/claims-posture.md, evidence status vocabulary).

Usage
  python scripts/readme_scaffold.py --name my-tool --type cli-tool --lang both --out-dir .
  python scripts/readme_scaffold.py --selftest

Types: library | cli-tool | spec | dataset | skill (per-type emphasis from
references/anatomy.md). Stdlib only.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from readme_doctor import github_slug  # anchors stay consistent by construction

TYPES = ("library", "cli-tool", "spec", "dataset", "skill")
TYPE_PHRASE = {
    "library": "library",
    "cli-tool": "command-line tool",
    "spec": "specification and conformance suite",
    "dataset": "dataset",
    "skill": "agent skill",
}
TYPE_CAPABILITY_HINT = {
    "library": "each capability phrased as a checkable statement, with a minimal code sample",
    "cli-tool": "the one-liner above is the front door; each subcommand gets a checkable statement",
    "spec": "conformance criteria ARE the capabilities; reference the SPEC section for each",
    "dataset": "provenance outranks features; state coverage, format, and update policy",
    "skill": "skills are read by agents; every capability must be machine-checkable",
}

SECTIONS = [
    "Why this exists",
    "30-second contrast",
    "Install",
    "Capabilities",
    "How it works",
    "Boundaries — what {name} does not do",
    "Evidence",
    "FAQ",
    "Contributing",
    "License",
]

ANCHOR_PATH = ["3. Install", "2. 30-second contrast", "4. Capabilities", "7. Evidence"]

ZH_SECTIONS = {
    1: "为什么要有这个项目", 2: "30 秒对照", 3: "安装", 4: "能力",
    5: "工作原理", 6: "边界（{name} 不做什么）", 7: "证据",
    8: "常见问题", 9: "参与贡献", 10: "许可证",
}


def slug_for(title: str) -> str:
    return github_slug(title, Counter())


def toc_and_path(name: str) -> tuple[str, str]:
    toc, path = [], []
    for i, sec in enumerate(SECTIONS, 1):
        title = f"{i}. {sec.format(name=name)}"
        # link text unnumbered; the list carries the number (matches fix_toc's shape)
        toc.append(f"{i}. [{sec.format(name=name)}](#{slug_for(title)})")
    for sec in ANCHOR_PATH:
        title = sec.format(name=name)
        path.append(f"[{title.split('. ', 1)[1]}](#{slug_for(title)})")
    return "\n".join(toc), " · ".join(path)


def render_en(name: str, typ: str, bilingual: bool = False) -> str:
    toc, path = toc_and_path(name)
    switch = "\n**English** | [简体中文](README.zh-CN.md)\n" if bilingual else ""
    return f"""# {name}

*A {TYPE_PHRASE[typ]} that <differentiator: what it checks/builds/answers — no adjective a competitor couldn't claim>.*

<Hook question: the reader's question, not your slogan.>

[![CI](<workflow badge url>?style=flat-square)](<workflow runs url>)
[![License](<license badge url>?style=flat-square)](LICENSE)

30 seconds: {path}
{switch}
**Contents**

{toc}

## 1. Why this exists

<The problem in the reader's terms; end on the hook question's
answer-in-one-paragraph.>

## 2. 30-second contrast

| Without {name} | With {name} |
|---|---|
| <the current pain, concretely> | <the verifiable behavior that replaces it> |

## 3. Install

**One-liner for your agent:**

```text
Install {name} for me: <raw URL to INSTALL.md, tag-pinned — see references/install-one-liner.md>
```

<Fallback local install. A one-liner that only works on your machine is not a one-liner.>

## 4. Capabilities

- <{TYPE_CAPABILITY_HINT[typ]}>

## 5. How it works

<The mechanism in one diagram or worked example — this is the credibility section.>

## 6. Boundaries — what {name} does not do

> [!IMPORTANT]
> <Necessary/sufficient declarations. Anti-features prevent the wrong adopter.>

- <anti-feature 1>

## 7. Evidence

| Claim | Where | Status | Notes |
|---|---|---|---|
| <number with conditions> | `<repo path or command>` | `not-run` | platform, sample size, run date |

External corroboration is a separate row; a citation is not a measurement.

## 8. FAQ

- *<The hostile question — "Why not the obvious alternative?">*
  <One honest paragraph; if the alternative wins somewhere, say so.>

## 9. Contributing

<The smallest honest instruction.>

## 10. License

<License line matching the claims tier — narrow it until a reader cannot falsify it.>
"""


def render_zh(name: str, typ: str) -> str:
    def ztitle(i: int) -> str:
        return f"{i}. {ZH_SECTIONS[i].format(name=name)}"

    links = [f"{i}. [{ZH_SECTIONS[i].format(name=name)}](#{slug_for(ztitle(i))})"
             for i in range(1, 11)]
    path_zh = " · ".join(
        f"[{ztitle(i).split('. ', 1)[1]}](#{slug_for(ztitle(i))})"
        for i in (3, 2, 4, 7))
    toc = "\n".join(links)
    return f"""<!-- 简体中文骨架 · 由 readme_scaffold.py 生成。 -->

# {name}

*<{TYPE_PHRASE[typ]} 的中文定位语——类别 + 它检查/构建/回答什么。>*

> [!NOTE]
> 英文 `README.md` 是 source of truth。本翻译可能滞后；冲突时以英文版为准。
> 最后同步：<date>。

<钩子问句：读者的问题，不是你的口号。>

30 秒：{path_zh}

[English](README.md) | **简体中文**

**目录**

{toc}

## 1. 为什么要有这个项目

<用读者的话说问题；以钩子问句的一段式回答收尾。>

## 2. 30 秒对照

| 没有 {name} | 有 {name} |
|---|---|
| <当前痛点，具体化> | <取而代之的可验证行为> |

## 3. 安装

**给你的 agent 的一句话：**

```text
Install {name} for me: <指向 INSTALL.md 的 raw URL，锁定 tag>
```

<本地安装回退。>

## 4. 能力

- <{TYPE_CAPABILITY_HINT[typ]}>

## 5. 工作原理

<机制的一图或一例——这是可信度章节。>

## 6. 边界（{name} 不做什么）

> [!IMPORTANT]
> <必要/充分条件声明。反特性防止错误的采用者。>

- <反特性 1>

## 7. 证据

| 主张 | 在哪 | 状态 | 备注 |
|---|---|---|---|
| <带条件的数字> | `<仓库路径或命令>` | `not-run` | 平台、样本量、日期 |

## 8. 常见问题

- *<最不客气的问题>* <一段诚实回答。>

## 9. 参与贡献

<最小而诚实的指引。>

## 10. 许可证

<与主张层级匹配的许可声明——收窄到读者无法证伪为止。>
"""


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--name", default=None, help="canonical project name")
    ap.add_argument("--type", choices=TYPES, default="library")
    ap.add_argument("--lang", choices=("en", "zh", "both"), default="en")
    ap.add_argument("--out-dir", default=".")
    ap.add_argument("--force", action="store_true", help="overwrite existing files")
    ap.add_argument("--selftest", action="store_true",
                    help="scaffold a bilingual pair into a temp dir and gate it")
    args = ap.parse_args(argv)
    if not args.name:
        args.name = "demo-tool" if args.selftest else ap.error("--name is required")

    if args.selftest:
        with tempfile.TemporaryDirectory() as td:
            out = Path(td)
            (out / "LICENSE").write_text("License placeholder\n", encoding="utf-8")
            (out / "README.md").write_text(
                render_en(args.name, args.type, bilingual=True), encoding="utf-8")
            (out / "README.zh-CN.md").write_text(
                render_zh(args.name, args.type), encoding="utf-8")
            doctor = Path(__file__).parent / "readme_doctor.py"
            checks = [("README.md", ["--zh", "README.zh-CN.md"]),
                      ("README.zh-CN.md", [])]
            for f, extra in checks:
                r = subprocess.run(
                    [sys.executable, str(doctor), str(out / f), "--name", args.name] + extra,
                    capture_output=True, text=True)
                ok = r.returncode == 0
                print(f"  [{'PASS' if ok else 'FAIL'}] scaffold selftest: {f} "
                      f"passes the gates by construction")
                if not ok:
                    print(r.stdout)
                    return 1
        return 0

    out = Path(args.out_dir)
    plan = {"en": [("README.md", lambda: render_en(args.name, args.type))],
            "zh": [("README.zh-CN.md", lambda: render_zh(args.name, args.type))],
            "both": [("README.md", lambda: render_en(args.name, args.type, bilingual=True)),
                     ("README.zh-CN.md", lambda: render_zh(args.name, args.type))]}[args.lang]
    for fname, render in plan:
        target = out / fname
        if target.exists() and not args.force:
            print(f"refusing to overwrite {target} (pass --force)", file=sys.stderr)
            return 2
        target.write_text(render(), encoding="utf-8")
        print(f"wrote {target}")
    if args.lang in ("zh", "both"):
        print("note: fill the Last-synced date in the [!NOTE] before publishing")
    return 0


if __name__ == "__main__":
    sys.exit(main())
