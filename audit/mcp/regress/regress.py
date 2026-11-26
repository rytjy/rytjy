#!/usr/bin/env python3
"""MCP 审计回归包：版本一变就跑同一套用例，出差异表。

用法：python3 regress.py [--case fs-001] [--keep]
退出码：0 全部命中且版本未变；1 有失败或版本变了；2 环境错误。
"""
import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]  # audit/mcp/regress -> workspace
CASES_FILE = HERE / "cases.json"

ENV = os.environ.copy()
for k in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy",
          "all_proxy", "NO_PROXY", "no_proxy"):
    ENV.pop(k, None)


def load_cases():
    return json.loads(CASES_FILE.read_text(encoding="utf-8"))


def detect_version(case):
    v = case["version"]
    try:
        if v["kind"] == "npm":
            meta = json.loads((ROOT / v["path"]).read_text(encoding="utf-8"))
            return meta.get("version")
        if v["kind"] == "pip":
            out = subprocess.run(
                [str(ROOT / case["cwd"] / v["python"]), "-c",
                 f"from importlib.metadata import version; print(version({v['dist']!r}))"],
                capture_output=True, text=True, timeout=60)
            return out.stdout.strip() or None
    except Exception as e:  # noqa: BLE001
        return f"<error: {e}>"
    return None


def run_case(case, outdir):
    cwd = ROOT / case["cwd"]
    version = detect_version(case)
    version_changed = version != case["version"]["baseline"]
    results = []
    for run in case["runs"]:
        try:
            proc = subprocess.run(run["cmd"], cwd=cwd, env=ENV, capture_output=True,
                                  text=True, timeout=run.get("timeout", 180))
            output = (proc.stdout or "") + (proc.stderr or "")
            rc = proc.returncode
        except subprocess.TimeoutExpired as e:
            output = (e.stdout or "") + "\n<TIMEOUT>"
            rc = -9
        outfile = outdir / f"{case['id']}-{run['name']}.txt"
        outfile.write_text(output, encoding="utf-8")
        for label, pattern in run["checks"]:
            ok = re.search(pattern, output, re.M) is not None
            results.append((f"{case['id']}/{run['name']}", label, ok, rc))
    return version, version_changed, results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", action="append", default=None)
    args = ap.parse_args()

    data = load_cases()
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    outdir = HERE / "results" / stamp
    outdir.mkdir(parents=True, exist_ok=True)

    rows = []
    ok_all = True
    for case in data["cases"]:
        if args.case and case["id"] not in args.case:
            continue
        version, changed, results = run_case(case, outdir)
        rows.append((case, version, changed, results))
        if changed or any(not ok for _, _, ok, _ in results):
            ok_all = False

    lines = [f"# MCP 审计回归 · {stamp}", "",
             "| 案例 | 版本（本次/基线） | 通过 | 结果 |", "|---|---|---|---|"]
    details = []
    for case, version, changed, results in rows:
        passed = sum(1 for r in results if r[2])
        total = len(results)
        state = "OK"
        if changed:
            state = "VERSION CHANGED"
        if passed != total:
            state = "FAIL"
        lines.append(f"| {case['id']} | {version} / {case['version']['baseline']} | {passed}/{total} | {state} |")
        details.append(f"\n## {case['id']} · {case['title']}\n")
        for _, label, ok, rc in results:
            details.append(f"- {'PASS' if ok else 'FAIL'} · {label}" + (f" （exit {rc}）" if not ok else ""))
        if changed:
            details.append(f"- 版本变了：{case['version']['baseline']} → {version}，需要人工看差异。")

    summary = "\n".join(lines + details) + "\n"
    (outdir / "SUMMARY.md").write_text(summary, encoding="utf-8")
    print(summary)
    print(f"输出目录：{outdir}")
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
