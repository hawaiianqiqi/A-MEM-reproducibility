"""Turn the raw trial files into the tables the report quotes.

Two jobs the harness itself cannot do:

1. Collapse several trials into mean +/- std per category and per arm.
2. Re-score category 5 under the *strict* convention ("Not mentioned in the conversation" is
   the correct answer) from the stored predictions. A run is scored under one convention only,
   but the predictions are kept, so the other convention can be derived without paying for a
   second run — which is what makes the category-5 discussion in the report possible at all.

    python analyze_results.py --arms baseline noevo
"""

import argparse
import glob
import json
import os
import statistics

SPLITS = ["category_4", "category_1", "category_2", "category_3", "category_5"]
NAMES = {
    "category_4": "Single-hop",
    "category_1": "Multi-hop",
    "category_2": "Temporal",
    "category_3": "Open-domain",
    "category_5": "Adversarial",
}
NOT_MENTIONED = "Not mentioned in the conversation"

# Table 1 of arXiv:2502.12110v1, A-Mem column, GPT-4o-mini backbone (F1 / BLEU-1, %)
PAPER = {
    "category_4": (27.02, 20.09, "Table 1, A-Mem, gpt-4o-mini"),
    "category_1": (45.85, 36.67, "Table 1, A-Mem, gpt-4o-mini"),
    "category_2": (12.14, 12.00, "Table 1, A-Mem, gpt-4o-mini"),
    "category_3": (44.65, 37.06, "Table 1, A-Mem, gpt-4o-mini"),
    "category_5": (50.03, 49.47, "Table 1, A-Mem, gpt-4o-mini"),
}
# Table 2, multi-hop F1 only
PAPER_ABLATION = {"full": 45.85, "w/o LG & ME": 24.55, "w/o ME": 31.24}


def simple_tokenize(text):
    """Same tokenisation as utils.simple_tokenize, duplicated to keep this script torch-free."""
    return str(text).lower().replace('.', ' ').replace(',', ' ').replace('!', ' ').replace('?', ' ').split()


def token_f1(prediction, reference):
    pred, ref = set(simple_tokenize(prediction)), set(simple_tokenize(reference))
    if not pred or not ref:
        return 0.0
    common = len(pred & ref)
    precision, recall = common / len(pred), common / len(ref)
    return 2 * precision * recall / (precision + recall) if precision + recall else 0.0


def strict_c5(trial_files):
    """Category-5 F1 recalculated against 'Not mentioned in the conversation'."""
    scores, declines = [], 0
    for path in trial_files:
        with open(path, encoding="utf-8") as handle:
            data = json.load(handle)
        for row in data.get("individual_results", []):
            if int(row.get("category", 0)) != 5:
                continue
            prediction = str(row.get("prediction", ""))
            scores.append(token_f1(prediction, NOT_MENTIONED))
            declines += int("not mentioned" in prediction.lower()
                            or "no information available" in prediction.lower())
    if not scores:
        return None
    return {"f1": statistics.mean(scores) * 100, "n": len(scores), "declines": declines}


def load_arm(tag, out_dir):
    summary_path = os.path.join(out_dir, f"{tag}_summary.json")
    if not os.path.exists(summary_path):
        return None
    with open(summary_path, encoding="utf-8") as handle:
        summary = json.load(handle)
    trials = sorted(glob.glob(os.path.join(out_dir, f"{tag}_trial*.json")))
    return summary, trials


def cell(table, split, metric):
    entry = table.get(split, {}).get(metric)
    if not entry:
        return None
    return entry["mean"] * 100, entry["std"] * 100, entry["n_trials"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", nargs="+", default=["baseline", "noevo"])
    ap.add_argument("--out-dir", default="results")
    ap.add_argument("--out", default="results/report_tables.md")
    args = ap.parse_args()

    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), args.out_dir)
    blocks, loaded = [], {}

    for tag in args.arms:
        loaded[tag] = load_arm(tag, out_dir)

    # ---- table 1: per-arm results, paper side by side ----
    for tag in args.arms:
        if not loaded[tag]:
            blocks.append(f"### `{tag}`\n\n_no results yet_\n")
            continue
        summary, trials = loaded[tag]
        meta, table = summary["meta"], summary["table"]
        lines = [f"### Arm `{tag}`", ""]
        lines.append(f"model `{meta['model']}` / backend `{meta['backend']}` / k={meta['retrieve_k']} "
                     f"/ ratio={meta['ratio']} / legacy_c5={meta['legacy_c5']} "
                     f"/ trials={meta['trials']} (seeds {meta['seeds']})")
        lines.append("")
        lines.append("| Category | F1 (ours) | BLEU-1 (ours) | F1 (paper) | Δ F1 |")
        lines.append("|---|---|---|---|---|")
        for split in SPLITS:
            f1, b1 = cell(table, split, "f1"), cell(table, split, "bleu1")
            paper = PAPER[split][0]
            ours = f"{f1[0]:.2f} ± {f1[1]:.2f}" if f1 else "—"
            bleu = f"{b1[0]:.2f} ± {b1[1]:.2f}" if b1 else "—"
            delta = f"{f1[0] - paper:+.2f}" if f1 else "—"
            lines.append(f"| {NAMES[split]} | {ours} | {bleu} | {paper:.2f} | {delta} |")
        strict = strict_c5(trials)
        if strict:
            lines.append("")
            lines.append(f"Category 5 re-scored strictly (prediction vs \"{NOT_MENTIONED}\"): "
                         f"F1 = {strict['f1']:.2f} over {strict['n']} questions, "
                         f"{strict['declines'] / strict['n'] * 100:.0f}% of answers declined. "
                         f"The scored run used legacy_c5={meta['legacy_c5']}.")
        blocks.append("\n".join(lines) + "\n")

    # ---- table 2: ablation delta ----
    if loaded.get("baseline") and loaded.get("noevo"):
        lines = ["### Ablation: full A-MEM vs no evolution", ""]
        lines.append("| Category | Full F1 | No-evolution F1 | Δ | Paper full | Paper w/o LG & ME |")
        lines.append("|---|---|---|---|---|---|")
        for split in SPLITS:
            full = cell(loaded["baseline"][0]["table"], split, "f1")
            off = cell(loaded["noevo"][0]["table"], split, "f1")
            if not (full and off):
                continue
            paper = PAPER[split][0]
            paper_off = PAPER_ABLATION["w/o LG & ME"] if split == "category_1" else None
            lines.append(f"| {NAMES[split]} | {full[0]:.2f} ± {full[1]:.2f} | "
                         f"{off[0]:.2f} ± {off[1]:.2f} | {off[0] - full[0]:+.2f} | "
                         f"{paper:.2f} | {paper_off if paper_off else '—'} |")
        blocks.append("\n".join(lines) + "\n")

    # ---- cost ----
    lines = ["### Cost and latency", "",
             "| Arm | Trials | LLM calls | Tokens | Est. cost (USD) | Wall clock (min) |",
             "|---|---|---|---|---|---|"]
    for tag in args.arms:
        if not loaded[tag]:
            continue
        runs = loaded[tag][0]["runs"]
        calls = sum(r["usage"]["llm_calls"] for r in runs)
        tokens = sum(r["usage"]["total_tokens"] for r in runs)
        cost = sum(r["usage"]["est_cost_usd"] for r in runs)
        wall = sum(r["wall_s"] for r in runs) / 60
        lines.append(f"| {tag} | {len(runs)} | {calls} | {tokens/1e6:.2f}M | {cost:.3f} | {wall:.1f} |")
    blocks.append("\n".join(lines) + "\n")

    markdown = "\n".join(blocks)
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), args.out)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(markdown)
    print(markdown)
    print(f"\nwritten to {path}")


if __name__ == "__main__":
    main()
