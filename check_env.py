"""Environment preflight: prove the chain works before spending money on LLM calls.

Checks imports, the dataset, the metric code path, and the DeepSeek backend wiring.
Prints a version table that goes straight into the report's setup section.

    python check_env.py
"""

import os
import sys

OK = "OK  "
BAD = "FAIL"


def main():
    failures = []

    print("== versions ==")
    for name in ["numpy", "pandas", "torch", "transformers", "sentence_transformers",
                 "openai", "litellm", "nltk", "rouge_score", "bert_score", "sklearn"]:
        try:
            module = __import__(name)
            print(f"  {OK}{name:24s}{getattr(module, '__version__', '?')}")
        except Exception as exc:
            failures.append(f"import {name}: {exc}")
            print(f"  {BAD}{name:24s}{exc}")

    print("\n== nltk tokenizer ==")
    import nltk
    try:
        tokens = nltk.word_tokenize("I met Dr. Smith on 3 May. We talked.")
        print(f"  {OK}word_tokenize -> {tokens[:6]}...")
    except Exception as exc:
        failures.append(f"word_tokenize: {exc}")
        print(f"  {BAD}word_tokenize: {exc}")

    print("\n== dataset ==")
    try:
        from load_dataset import load_locomo_dataset
        samples = load_locomo_dataset(os.path.join(os.path.dirname(__file__),
                                                   "data/locomo10.json"))
        qa_total = sum(len(s.qa) for s in samples)
        cats = {}
        for qa in samples[0].qa:
            cats[qa.category] = cats.get(qa.category, 0) + 1
        print(f"  {OK}conversations={len(samples)} qa_total={qa_total} "
              f"conv0_qa={len(samples[0].qa)} conv0_categories={dict(sorted(cats.items()))}")
    except Exception as exc:
        failures.append(f"dataset: {exc}")
        print(f"  {BAD}dataset: {exc}")

    print("\n== metrics ==")
    try:
        from utils import calculate_metrics
        m = calculate_metrics("Paris", "Paris")
        print(f"  {OK}f1={m['f1']:.3f} bleu1={m['bleu1']:.3f} rougeL={m['rougeL_f']:.3f} "
              f"meteor={m['meteor']:.3f} keys={sorted(m)}")
    except Exception as exc:
        failures.append(f"metrics: {exc}")
        print(f"  {BAD}metrics: {exc}")

    print("\n== controller wiring ==")
    try:
        from memory_layer_robust import RobustLLMController
        has_key = bool(os.getenv("DEEPSEEK_API_KEY"))
        print(f"  {'OK  ' if has_key else 'WARN'}DEEPSEEK_API_KEY "
              f"{'set' if has_key else 'NOT set — .env not loaded?'}")
        if has_key:
            controller = RobustLLMController("deepseek", "deepseek-chat")
            print(f"  {OK}backend=deepseek base={os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com')}")
            reply = controller.llm.get_completion("Reply with exactly one word: READY", temperature=0.0)
            print(f"  {OK}live call returned: {reply.strip()[:40]!r}")
        else:
            print("  (skipping live call)")
    except Exception as exc:
        failures.append(f"controller: {exc}")
        print(f"  {BAD}controller: {exc}")

    print("\n== result ==")
    if failures:
        print(f"  {len(failures)} problem(s):")
        for f in failures:
            print(f"   - {f}")
        return 1
    print("  all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
