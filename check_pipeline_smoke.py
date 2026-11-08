"""End-to-end preflight: does the whole chain work before spending hours of API time?

Builds memory for the first few turns of one LoCoMo conversation, answers one question per
category, and prints per-stage latency plus token/cost totals. It answers the questions a
long run cannot answer cheaply: is the backend reachable, does retrieval return context,
does the answer parse, does the scorer produce the metrics the report needs, and how many
seconds does one turn of memory construction actually cost on this machine.

    python check_pipeline_smoke.py --turns 12
"""

import argparse
import os
import random
import time

import env_bootstrap  # noqa: F401  (loads .env and forces offline model loading first)

import instrument  # noqa: E402  (must be imported before the controller binds litellm.completion)

from load_dataset import load_locomo_dataset  # noqa: E402
from utils import calculate_metrics  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--turns", type=int, default=12)
    ap.add_argument("--model", default="deepseek-chat")
    ap.add_argument("--backend", default="deepseek")
    ap.add_argument("--retrieve-k", type=int, default=10)
    ap.add_argument("--dataset", default="data/locomo10.json")
    ap.add_argument("--no-evolution", action="store_true")
    ap.add_argument("--skip-bert", action="store_true",
                    help="skip BERTScore, whose weights may still be downloading")
    args = ap.parse_args()

    if args.skip_bert:
        import utils
        utils.calculate_bert_scores = lambda p, r: {
            "bert_precision": 0.0, "bert_recall": 0.0, "bert_f1": 0.0}

    instrument.install()
    from test_advanced_robust import RobustAdvancedMemAgent

    sample = load_locomo_dataset(args.dataset)[0]
    print(f"conversation 0: {len(sample.qa)} questions", flush=True)

    agent = RobustAdvancedMemAgent(args.model, args.backend, args.retrieve_k, 0.5)
    agent.memory_system.no_evolution = args.no_evolution

    turns = []
    for _, session in sample.conversation.sessions.items():
        for turn in session.turns:
            turns.append((f"Speaker {turn.speaker}says : {turn.text}", session.date_time))
    turns = turns[: args.turns]

    print(f"\n--- building memory over {len(turns)} turns ---", flush=True)
    started = time.perf_counter()
    for i, (text, when) in enumerate(turns, 1):
        t0 = time.perf_counter()
        agent.add_memory(text, time=when)
        print(f"  turn {i:2d}: {time.perf_counter() - t0:5.1f}s  {text[:70]!r}", flush=True)
    build_s = time.perf_counter() - started
    per_turn = build_s / max(1, len(turns))
    print(f"build: {build_s:.0f}s total, {per_turn:.1f}s/turn, "
          f"{len(agent.memory_system.memories)} notes", flush=True)

    # one question per category the dataset actually has at this point
    seen = {}
    for qa in sample.qa:
        if int(qa.category) not in seen:
            seen[int(qa.category)] = qa
    chosen = [seen[c] for c in sorted(seen)]

    print(f"\n--- answering {len(chosen)} questions (one per category) ---", flush=True)
    for qa in chosen:
        rng = random.Random(f"42:0:{sample.qa.index(qa)}")
        t0 = time.perf_counter()
        prediction, prompt, context = agent.answer_question(
            qa.question, qa.category, qa.final_answer, rng)
        dt = time.perf_counter() - t0
        from test_advanced_robust import parse_plain_text_answer
        prediction = parse_plain_text_answer(prediction)
        metrics = calculate_metrics(prediction, str(qa.final_answer))
        print(f"  cat {qa.category}: {dt:5.1f}s | context {len(context)} chars | "
              f"pred={prediction[:60]!r} | ref={str(qa.final_answer)[:40]!r} | "
              f"F1={metrics['f1']:.3f}", flush=True)

    stats = instrument.snapshot()
    print(f"\ncalls={stats['llm_calls']} errors={stats['llm_errors']} "
          f"in={stats['prompt_tokens']} out={stats['completion_tokens']} "
          f"cost=${stats['est_cost_usd']:.4f}")
    if stats["llm_calls"]:
        print(f"mean latency {stats['mean_latency_s']:.1f}s/call")
    projected = per_turn * 419 + 199 * 2 * stats["mean_latency_s"]
    print(f"projected full-conversation wall clock: {projected/3600:.1f} h "
          f"({per_turn:.1f}s/turn x 419 turns + 199 questions x 2 calls)")


if __name__ == "__main__":
    main()
