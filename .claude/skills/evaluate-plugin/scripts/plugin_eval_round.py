#!/usr/bin/env python3
"""Run one hill-climb round with `claude plugin eval` and write it in the hill-climb layout.

The claude-api skill's hill-climb guide (`shared/evals/eval-hillclimb.md`) reads one directory per
round: `results.jsonl` (one row per case and run), `traces/<case>_rep<k>.json`, `errors.jsonl`, and
`summary.json`. `claude plugin eval` writes one `aggregate-result.json` instead, and deletes each
run's transcript unless `--keep-temp` is passed. This script runs the eval with `--keep-temp`,
converts the result and the transcripts, then deletes the kept temp directories.

    python plugin_eval_round.py --plugin <plugin-dir> --flow <flow-dir> --variant baseline \
        [--runs 3] [--case GLOB] [--model M] [-j 4] [--max-cost-usd 20] [-- <extra eval args>]

Stdlib only. Exits with the eval's exit code, or 2 when the result file is missing.
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def run_eval(args: argparse.Namespace, raw: Path, extra: list[str]) -> int:
    cmd = [
        "claude",
        "plugin",
        "eval",
        str(args.plugin),
        "--ablation",
        "none",
        "--keep-temp",
    ]
    cmd += [
        "--no-publish",
        "--trust-plugin",
        "--output-dir",
        str(raw),
        "--runs",
        str(args.runs),
    ]
    for flag, value in (
        ("--case", args.case),
        ("--model", args.model),
        ("-j", args.concurrency),
        ("--max-cost-usd", args.max_cost_usd),
    ):
        if value is not None:
            cmd += [flag, str(value)]
    print("+", " ".join(cmd + extra), flush=True)
    # shell=True on Windows only: `claude` is a .cmd shim there, which CreateProcess cannot run.
    return subprocess.run(cmd + extra, shell=sys.platform == "win32").returncode


def read_trace(path: Path, prompt: str) -> tuple[list[dict], dict]:
    """Turn a Claude Code stream-json transcript into hill-climb turns, plus the final result event."""
    turns: list[dict] = [{"role": "user", "content": prompt}]
    result: dict = {}
    thinking = ""
    for line in path.read_text("utf-8").splitlines():
        event = json.loads(line)
        kind = event.get("type")
        if kind == "result":
            result = event
            continue
        if kind not in ("assistant", "user"):
            continue  # system init carries temp paths under the user's home, so it is dropped
        content = event["message"].get("content", [])
        if isinstance(content, str):
            content = [{"type": "text", "text": content}]
        for block in content:
            btype = block.get("type")
            if btype == "thinking":
                thinking += block.get("thinking", "")
                continue
            if btype == "text":
                turn = {
                    "role": "assistant" if kind == "assistant" else "user",
                    "content": block["text"],
                }
            elif btype == "tool_use":
                turn = {
                    "role": "tool_call",
                    "name": block.get("name", ""),
                    "content": json.dumps(block.get("input", {}), indent=2),
                }
            elif btype == "tool_result":
                body = block.get("content", "")
                if isinstance(body, list):
                    body = "\n".join(
                        b.get("text", "") for b in body if b.get("type") == "text"
                    )
                turn = {"role": "tool_result", "content": body}
            else:
                continue
            if thinking and turn["role"] in ("assistant", "tool_call"):
                turn["thinking"], thinking = thinking, ""
            turns.append(turn)
    return turns, result


def remove_temp(trace: Path) -> None:
    """Delete the `claude-eval-*` directory --keep-temp left, and nothing else."""
    root = trace.parent.parent
    temp = Path(tempfile.gettempdir()).resolve()
    if root.name.startswith("claude-eval-") and root.resolve().parent == temp:
        shutil.rmtree(root, ignore_errors=True)


def convert(aggregate: dict, out: Path) -> tuple[int, int, float]:
    (out / "traces").mkdir(parents=True, exist_ok=True)
    rows, errors, cost = [], [], 0.0
    for case in aggregate.get("cases", []):
        name = re.sub(r"[^\w.-]", "_", case["name"])
        prompt = case.get("promptMarkdown", "")
        for rep, run in enumerate(case.get("arms", {}).get("with", [])):
            cost += run.get("costUsd", 0) + run.get("judgeCostUsd", 0)
            trace = Path(run["tracePath"]) if run.get("tracePath") else None
            turns, result = (
                read_trace(trace, prompt) if trace and trace.exists() else ([], {})
            )
            model = next((u for u in result.get("modelUsage", {})), None)
            if not run.get(
                "graders"
            ):  # an API error scores 0 ungraded: plumbing, not the plugin
                errors.append(
                    {
                        "prompt_id": name,
                        "rep": rep,
                        "failure_class": "harness",
                        "error": run.get("error"),
                        "model": model,
                        "usage": result.get("usage"),
                    }
                )
                continue
            if not result:
                print(
                    f"WARNING {name} rep {rep}: no transcript, so no model or usage",
                    file=sys.stderr,
                )
            grade = {"pass": int(bool(run.get("passed"))), "score": run.get("score", 0)}
            grade.update(
                {g["name"]: int(bool(g.get("passed"))) for g in run["graders"]}
            )
            rows.append(
                {
                    "prompt_id": name,
                    "rep": rep,
                    "prompt": prompt,
                    "tags": case.get("tags") or [name],
                    "status": "truncated"
                    if result.get("stop_reason") == "max_tokens"
                    else "ok",
                    "stop_reason": result.get("stop_reason"),
                    "grade": grade,
                    "explanation": {
                        g["name"]: g.get("explanation", "") for g in run["graders"]
                    },
                    "model": model,
                    "usage": result.get("usage", {}),
                    "latency_s": run.get("durationSeconds"),
                    "tool_calls": sum(t["role"] == "tool_call" for t in turns),
                    "cost_usd": run.get("costUsd", 0),
                    "judge_cost_usd": run.get("judgeCostUsd", 0),
                    "meta": {
                        "error": run.get("error"),
                        "skippedPaidGraders": run.get("skippedPaidGraders"),
                    },
                }
            )
            (out / "traces" / f"{name}_rep{rep}.json").write_text(
                json.dumps(turns, indent=1), "utf-8"
            )
            if trace:
                remove_temp(trace)
    for file, items in (("results.jsonl", rows), ("errors.jsonl", errors)):
        with open(out / file, "w", encoding="utf-8") as f:
            f.writelines(json.dumps(i) + "\n" for i in items)
    return len(rows), len(errors), cost


def main() -> int:
    argv = sys.argv[1:]
    extra = argv[argv.index("--") + 1 :] if "--" in argv else []
    argv = argv[: argv.index("--")] if "--" in argv else argv
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--plugin", type=Path, required=True)
    p.add_argument("--flow", type=Path, required=True)
    p.add_argument("--variant", required=True, help="baseline, v1, v2, ...")
    p.add_argument("--runs", type=int, default=3)
    p.add_argument("--case")
    p.add_argument("--model")
    p.add_argument("-j", "--concurrency", type=int)
    p.add_argument("--max-cost-usd", type=float)
    args = p.parse_args(argv)
    if not re.fullmatch(r"baseline|v\d+", args.variant):
        p.error(
            "--variant must be baseline or v<N>: the report builder ignores any other name"
        )

    out = args.flow / args.variant
    raw = out / "raw"
    # less-code: a rerun repeats the whole variant; resume per (case, rep) only if rounds get long.
    code = run_eval(args, raw, extra)
    aggregate_path = raw / "aggregate-result.json"
    if not aggregate_path.exists():
        print(f"no {aggregate_path}: the eval did not finish", file=sys.stderr)
        return 2
    aggregate = json.loads(aggregate_path.read_text("utf-8"))
    rows, errors, cost = convert(aggregate, out)
    summary = out / "summary.json"
    if not summary.exists():
        summary.write_text(
            json.dumps({"description": args.variant, "target": "skill"}), "utf-8"
        )
    partial = (
        " PARTIAL: " + aggregate.get("partialReason", "")
        if aggregate.get("partial")
        else ""
    )
    print(
        f"{args.variant}: {rows} rows, {errors} errors, ${cost:.2f}{partial} -> {out}"
    )
    return code


if __name__ == "__main__":
    sys.exit(main())
