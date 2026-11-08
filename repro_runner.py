"""Multi-trial runner for the A-MEM / LoCoMo reproduction.

Why this exists: the upstream harness runs once and prints one number. Reproducibility work
needs repeated trials and a cost log, so this wrapper runs the same evaluation several times
with different answer-side seeds, keeps the harness untouched, and reports mean +/- std.

Trial 0 builds the memory store (the expensive part, cached to disk). Later trials reuse that
cache and only re-run retrieval + answering, which is where the sampling noise lives. This is
the same protocol the upstream k-sweep relies on.

Usage:
    python repro_runner.py --tag baseline --trials 3
    python repro_runner.py --tag noevo --trials 3 --no-evolution
"""

import argparse
import json
import os
import statistics
import time

import instrument

METRICS = ["f1", "bleu1"]
SPLITS = ["overall", "category_1", "category_2", "category_3", "category_4", "category_5"]
SPLIT_NAMES = {
    "overall": "Overall",
    "category_1": "Multi-hop",
    "category_2": "Temporal",
    "category_3": "Open-domain",
    "category_4": "Single-hop",
    "category_5": "Adversarial",
}


def parse_args():
    p = argparse.ArgumentParser(description="Run N trials of the A-MEM LoCoMo harness")
    p.add_argument("--tag", required=True, help="name of this arm, e.g. baseline / noevo")
    p.add_argument("--trials", type=int, default=1)
    p.add_argument("--model", default="deepseek-chat")
    p.add_argument("--backend", default="deepseek")
    p.add_argument("--ratio", type=float, default=0.1, help="fraction of LoCoMo conversations")
    p.add_argument("--retrieve-k", type=int, default=10)
    p.add_argument("--memory-scope", choices=["conversation", "pooled"], default="conversation")
    p.add_argument("--temperature-c5", type=float, default=0.5)
    p.add_argument("--legacy-c5", action="store_true",
                   help="score category 5 against the adversarial answer, as the paper did")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--dataset", default="data/locomo10.json")
    p.add_argument("--out-dir", default="results")
    return p.parse_args()


def summarise(runs):
    """Collapse per-trial aggregates into mean/std per metric and split."""
    table = {}
    for split in SPLITS:
        table[split] = {}
        for metric in METRICS:
            values = []
            for run in runs:
                cell = run["agg"].get(split, {}).get(metric)
                if cell is not None:
                    values.append(cell["mean"])
            if values:
                table[split][metric] = {
                    "mean": statistics.mean(values),
                    "std": statistics.stdev(values) if len(values) > 1 else 0.0,
                    "n_trials": len(values),
                    "per_trial": values,
                }
    return table


def render_markdown(table, meta):
    lines = []
    lines.append(f"### Arm: `{meta['tag']}`")
    lines.append("")
    lines.append(f"- model: `{meta['model']}` via `{meta['backend']}` | k={meta['retrieve_k']} | "
                 f"ratio={meta['ratio']} | legacy_c5={meta['legacy_c5']}")
    lines.append(f"- trials: {meta['trials']} (answer seeds {meta['seeds']})")
    lines.append("")
    lines.append("| Split | F1 | BLEU-1 |")
    lines.append("|---|---|---|")
    for split in SPLITS:
        cells = []
        for metric in METRICS:
            cell = table.get(split, {}).get(metric)
            cells.append(f"{cell['mean']*100:.2f} ± {cell['std']*100:.2f}" if cell else "—")
        lines.append(f"| {SPLIT_NAMES[split]} | {cells[0]} | {cells[1]} |")
    return "\n".join(lines)


def main():
    args = parse_args()
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), args.out_dir)
    os.makedirs(out_dir, exist_ok=True)

    instrument.install()
    from test_advanced_robust import evaluate_dataset

    dataset_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), args.dataset)
    runs = []

    for trial in range(args.trials):
        seed = args.seed + trial
        instrument.reset()
        out_path = os.path.join(out_dir, f"{args.tag}_trial{trial}.json")
        print(f"[{args.tag}] trial {trial + 1}/{args.trials} (seed={seed}) -> {out_path}", flush=True)
        started = time.time()
        result = evaluate_dataset(
            dataset_path, args.model, out_path, args.ratio,
            args.backend, args.temperature_c5, args.retrieve_k,
            "http://localhost", 30000, args.legacy_c5, seed,
            False, args.memory_scope,
        )
        wall = time.time() - started
        usage = instrument.snapshot()
        runs.append({
            "trial": trial,
            "seed": seed,
            "wall_s": wall,
            "agg": result["aggregate_metrics"],
            "usage": usage,
            "llm_failures": result.get("llm_failures"),
            "cached_samples": result.get("cached_samples"),
            "stale_cache_samples": result.get("stale_cache_samples"),
        })
        overall = result["aggregate_metrics"].get("overall", {})
        print(f"[{args.tag}] trial {trial + 1} done in {wall/60:.1f} min | "
              f"F1={overall.get('f1', {}).get('mean', 0)*100:.2f} "
              f"BLEU-1={overall.get('bleu1', {}).get('mean', 0)*100:.2f} | "
              f"calls={usage['llm_calls']} cost=${usage['est_cost_usd']:.3f}", flush=True)

    table = summarise(runs)
    meta = {
        "tag": args.tag,
        "model": args.model,
        "backend": args.backend,
        "ratio": args.ratio,
        "retrieve_k": args.retrieve_k,
        "temperature_c5": args.temperature_c5,
        "legacy_c5": args.legacy_c5,
        "memory_scope": args.memory_scope,
        "trials": args.trials,
        "seeds": [args.seed + t for t in range(args.trials)],
        "dataset": os.path.basename(dataset_path),
    }
    summary = {"meta": meta, "table": table, "runs": runs}
    summary_path = os.path.join(out_dir, f"{args.tag}_summary.json")
    with open(summary_path, "w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)

    markdown = render_markdown(table, meta)
    with open(os.path.join(out_dir, f"{args.tag}_summary.md"), "w", encoding="utf-8") as handle:
        handle.write(markdown + "\n")

    print("\n" + markdown)
    total_cost = sum(r["usage"]["est_cost_usd"] for r in runs)
    total_tokens = sum(r["usage"]["total_tokens"] for r in runs)
    print(f"\nTotal: {sum(r['usage']['llm_calls'] for r in runs)} LLM calls, "
          f"{total_tokens/1e6:.2f}M tokens, ${total_cost:.3f}, "
          f"{sum(r['wall_s'] for r in runs)/60:.1f} min wall clock")
    print(f"Summary written to {summary_path}")


if __name__ == "__main__":
    main()
