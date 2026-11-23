#!/usr/bin/env python3
"""Run one hill-climb round with `claude plugin eval` and write it in the hill-climb layout.

The claude-api skill's hill-climb guide (`shared/evals/eval-hillclimb.md`) reads one directory per
round: `results.jsonl` (one row per case and run), `traces/<case>_rep<k>.json`, `errors.jsonl`, and
`summary.json`. `claude plugin eval` writes one `aggregate-result.json` instead, and deletes each
run's transcript unless `--keep-temp` is passed. This script clears what an earlier run of the same
variant left, runs the eval with `--keep-temp`, converts the result and the transcripts, then
deletes the kept temp directories. A run it cannot convert becomes a row in `errors.jsonl`, and
the other runs are still written.

A `results.jsonl` row carries `prompt_id`, `rep`, `prompt`, `tags`, `status`, `stop_reason`, the
`grade` and `explanation` per grader, the `model` that cost most and every model as `models`,
`usage`, `latency_s`, `tool_calls`, and exact `cost_usd` and `judge_cost_usd`.

    python plugin_eval_round.py --plugin <plugin-dir> --flow <flow-dir> --variant baseline \
        [--target skill|hook|agent|mcp] [--runs 3] [--case GLOB] [--model M] [-j 4] \
        [--max-cost-usd 20] [--timeout-s 3600] [-- <extra eval args>]

Stdlib only, Python 3.9+. Exits with the eval's exit code, 2 when `claude` or the result file is
missing, or 124 when `--timeout-s` ran out.
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
    # The resolved path, never a shell: on Windows a shell would read `&` or `|` in an argument.
    exe = shutil.which("claude")
    if not exe:
        print("claude is not on PATH", file=sys.stderr)
        return 2
    cmd = [
        exe,
        "plugin",
        "eval",
        str(args.plugin),
        "--ablation",
        "none",
        "--keep-temp",
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
    cmd += extra
    # A .cmd or .bat shim still runs through cmd.exe, which reads these characters as syntax.
    if exe.lower().endswith((".cmd", ".bat")) and any(
        set(a) & set('&|^%<>"') for a in cmd[1:]
    ):
        print(
            f'{exe} is a batch shim: an argument holding one of & | ^ % < > " cannot be passed',
            file=sys.stderr,
        )
        return 2
    print("+", " ".join(cmd), flush=True)
    try:
        return subprocess.run(cmd, timeout=args.timeout_s).returncode
    except subprocess.TimeoutExpired:
        print(f"the eval ran past --timeout-s {args.timeout_s}", file=sys.stderr)
        return 124


def read_trace(path: Path, prompt: str) -> tuple[list[dict], dict]:
    """Turn a Claude Code stream-json transcript into hill-climb turns, plus the final result event."""
    turns: list[dict] = [{"role": "user", "content": prompt}]
    result: dict = {}
    thinking = ""
    for line in path.read_text("utf-8").splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue  # a blank or cut-off line must not cost the round
        if not isinstance(event, dict):
            continue
        kind = event.get("type")
        if kind == "result":
            result = event
            continue
        message = event.get("message")
        if kind not in ("assistant", "user") or not isinstance(message, dict):
            continue  # system init carries temp paths under the user's home, so it is dropped
        content = message.get("content") or []
        if isinstance(content, str):
            content = [{"type": "text", "text": content}]
        for block in content:
            if not isinstance(block, dict):
                continue
            btype = block.get("type")
            if btype == "thinking":
                thinking += block.get("thinking", "")
                continue
            if btype == "text":
                turn = {
                    "role": "assistant" if kind == "assistant" else "user",
                    "content": block.get("text", ""),
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
                        b.get("text", "")
                        for b in body
                        if isinstance(b, dict) and b.get("type") == "text"
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
    if root.exists():
        print(f"WARNING not removed, delete it by hand: {root}", file=sys.stderr)


def convert_run(
    name: str, rep: int, prompt: str, case: dict, run: dict, trace: "Path | None"
) -> tuple["dict | None", "dict | None", list[dict]]:
    """One run as a results row, or as an errors row when it was never graded."""
    turns, result = read_trace(trace, prompt) if trace and trace.exists() else ([], {})
    usage = result.get("modelUsage") or {}

    def spent(model: str) -> float:
        return (
            (usage[model].get("costUSD") or 0) if isinstance(usage[model], dict) else 0
        )

    # The model that cost most is the one the run was served by: a helper model costs little.
    model = max(usage, key=spent) if usage else None
    graders = run.get("graders")
    if not graders:  # an API error scores 0 ungraded: plumbing, not the plugin
        error = {
            "prompt_id": name,
            "rep": rep,
            "failure_class": "harness",
            "error": run.get("error"),
            "model": model,
            "usage": result.get("usage"),
        }
        return None, error, turns
    if not result:
        print(
            f"WARNING {name} rep {rep}: no transcript, so no model or usage",
            file=sys.stderr,
        )
    grade = {"pass": int(bool(run.get("passed"))), "score": run.get("score", 0)}
    grade.update({g["name"]: int(bool(g.get("passed"))) for g in graders})
    row = {
        "prompt_id": name,
        "rep": rep,
        "prompt": prompt,
        "tags": case.get("tags") or [name],
        "status": "truncated" if result.get("stop_reason") == "max_tokens" else "ok",
        "stop_reason": result.get("stop_reason"),
        "grade": grade,
        "explanation": {g["name"]: g.get("explanation", "") for g in graders},
        "model": model,
        "models": sorted(usage),
        "usage": result.get("usage", {}),
        "latency_s": run.get("durationSeconds"),
        "tool_calls": sum(t["role"] == "tool_call" for t in turns),
        "cost_usd": run.get("costUsd") or 0,
        "judge_cost_usd": run.get("judgeCostUsd") or 0,
        "meta": {
            "error": run.get("error"),
            "skippedPaidGraders": run.get("skippedPaidGraders"),
        },
    }
    return row, None, turns


def convert(aggregate: dict, out: Path) -> tuple[int, int, float]:
    (out / "traces").mkdir(parents=True, exist_ok=True)
    rows, errors, cost = [], [], 0.0
    for index, case in enumerate(aggregate.get("cases") or []):
        name = re.sub(r"[^\w.-]", "_", str(case.get("name") or f"case{index}"))
        prompt = case.get("promptMarkdown") or ""
        for rep, run in enumerate((case.get("arms") or {}).get("with") or []):
            cost += (run.get("costUsd") or 0) + (run.get("judgeCostUsd") or 0)
            trace = Path(run["tracePath"]) if run.get("tracePath") else None
            try:
                row, error, turns = convert_run(name, rep, prompt, case, run, trace)
            # The eval is paid for by now, so one unreadable run must not lose the others.
            except (AttributeError, KeyError, OSError, TypeError, ValueError) as exc:
                row, turns = None, []
                error = {
                    "prompt_id": name,
                    "rep": rep,
                    "failure_class": "harness",
                    "error": f"not converted: {exc!r}",
                }
            finally:
                if trace:
                    remove_temp(trace)
            if error:
                errors.append(error)
                continue
            rows.append(row)
            (out / "traces" / f"{name}_rep{rep}.json").write_text(
                json.dumps(turns, indent=1), "utf-8"
            )
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
    p.add_argument(
        "--target",
        default="skill",
        choices=("skill", "hook", "agent", "mcp"),
        help="the kind of component under change, written to summary.json",
    )
    p.add_argument("--runs", type=int, default=3)
    p.add_argument("--case")
    p.add_argument("--model")
    p.add_argument("-j", "--concurrency", type=int)
    p.add_argument("--max-cost-usd", type=float)
    p.add_argument(
        "--timeout-s",
        type=float,
        help="stop the eval after this many seconds (default: no limit)",
    )
    args = p.parse_args(argv)
    if not re.fullmatch(r"baseline|v\d+", args.variant):
        p.error(
            "--variant must be baseline or v<N>: the report builder ignores any other name"
        )

    out = args.flow / args.variant
    raw = out / "raw"
    # An earlier run of this variant must not pass for this one when the eval dies early.
    for stale in (raw, out / "traces"):
        shutil.rmtree(stale, ignore_errors=True)
    for stale in ("results.jsonl", "errors.jsonl"):
        (out / stale).unlink(missing_ok=True)
    # less-code: a rerun repeats the whole variant; resume per (case, rep) only if rounds get long.
    code = run_eval(args, raw, extra)
    aggregate_path = raw / "aggregate-result.json"
    if not aggregate_path.exists():
        print(
            f"no {aggregate_path}: the eval did not finish. Any claude-eval-* directory it "
            f"kept is still in {tempfile.gettempdir()}",
            file=sys.stderr,
        )
        return code if code in (2, 124) else 2
    aggregate = json.loads(aggregate_path.read_text("utf-8"))
    rows, errors, cost = convert(aggregate, out)
    summary = out / "summary.json"
    if not summary.exists():
        summary.write_text(
            json.dumps({"description": args.variant, "target": args.target}), "utf-8"
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
