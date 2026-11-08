# Reproduction log — A-MEM on LoCoMo

Working notes for FTEC5660 Reproducibility Work. This file is the raw material for the
report's *debug diary*; it is not the report itself.

---

## 1. Target

| Item | Value |
|---|---|
| Upstream repo | `WujiangXu/AgenticMemory` (the paper's experiment repo, not the `agiresearch/A-mem` library) |
| Paper | A-MEM: Agentic Memory for LLM Agents (arXiv 2502.12110), Table 1 |
| Target claim | LoCoMo QA quality of A-MEM with a small GPT-class backbone: F1 and BLEU-1 per category |
| Paper row used as reference | A-MEM, GPT-4o-mini: Single-hop 27.02/20.09, Multi-hop 45.85/36.67, Temporal 12.14/12.00, Open-domain 44.65/37.06, Adversarial 50.03/49.47 |
| Scope | One dataset split only: the released `data/locomo10.json`, first conversation (`--ratio 0.1`) |

Why this repo and not the library: the library README says outright that paper results live in
`WujiangXu/AgenticMemory`. The library has no evaluation script, so it cannot be reproduced
against a reported number.

## 2. Controlled variable: the backbone model

The paper's backbone is GPT-4o-mini, which is not available here. Per the assignment's edge case A,
the backbone is swapped for DeepSeek and treated as a controlled variable.

| Knob | Paper | This run |
|---|---|---|
| Provider | OpenAI | DeepSeek |
| Model | `gpt-4o-mini` | `deepseek-chat` |
| Base URL | `api.openai.com/v1` | `https://api.deepseek.com` |
| Temperature (answer, cat 1/3/4) | 0.7 (hard-coded) | 0.7 (unchanged) |
| Temperature (answer, cat 5) | 0.5 (default) | 0.5 (unchanged) |
| Temperature (metadata/evolution) | 0.7 (hard-coded) | 0.7 (unchanged) |
| max_tokens | 1000 | 1000 (unchanged) |
| Prompt templates | — | unchanged |

Consequence to state in the report: results are **not directly comparable** to the paper because
the backbone LLM differs. What is comparable is the *protocol* (same tasks, same metrics, same
scoring script) and the *internal contrast* between the two arms.

## 3. Protocol decisions and the assumptions they hide

1. **Category-5 scoring.** `--legacy_c5_reference` must be set to match the paper. Reading the code:
   category-5 questions are adversarial (the answer is not in the conversation), and the released
   default scores the prediction against `"Not mentioned in the conversation"`. The paper instead
   scored against `adversarial_answer`, i.e. the *wrong* option. The README says as much. Every
   run here therefore uses `--legacy-c5`, and the default is reported as a divergence.
2. **Retrieval k.** `run_all_experiments.sh` uses the default k=10, but `run_k_sweep.sh` exists
   because the repo says optimal k is model-specific. The paper does not state which k produced
   Table 1. Here: k=10, stated as an assumption rather than a reproduction of an unknown.
3. **Dataset size.** The paper describes 7,512 QA pairs; the released `locomo10.json` holds 1,986
   across 10 conversations (199 in conversation 0, the split used here). The reported numbers are
   on a different (larger) instance of the benchmark than the file shipped with the code.
4. **Memory cache reuse.** Trials share a memory cache: trial 0 pays for memory construction,
   trials 1..n only re-run retrieval and answering. Variance therefore measures the *answering*
   stage, not memory construction. Stated as a limitation; rebuilding memory per trial would cost
   ~3x the budget for a quantity the paper never reports.

## 4. Modification

Ablation: disable the evolution step (`--no-evolution`). One flag, one code path.

- Code: `RobustAgenticMemorySystem.add_note` skips `process_memory`.
- What disappears: links between notes, strengthened tags, neighbour context updates.
- What stays identical: LLM metadata extraction per note, the embedding index, retrieval, prompts,
  metrics, seeds, k.
- Why this one: it isolates the mechanism the paper credits for its largest gain (multi-hop F1
  45.85 vs 18.41 for full-context LoCoMo). It is measurable on the same scale and it also removes
  2 of the 3 LLM calls per note, so cost per question moves — both effects are reportable.

## 5. Debug diary

| # | Blocker | Symptom | Resolution |
|---|---|---|---|
| 1 | Two repos, one folder | `agiresearch/A-mem` and `WujiangXu/AgenticMemory` both extract to `A-mem-main`; files silently overwrote each other | Compared the two file lists, kept only the experiment repo, committed it as a pristine snapshot before touching anything |
| 2 | `git clone` stalls | `--depth 1` clone hung past 180 s at ~30 KB/s | Fetched the codeload zip over `curl` instead |
| 3 | pip 403 against TUNA mirror | `pip` printed `from versions: none` while `curl` and `urllib` got 200 on the same URL | Verbose pip log showed HTTP 403 for `/simple/numpy/`; switched to aliyun mirror after testing four mirrors |
| 4 | Mirror intermittently empty | `python-dotenv`, `requests` randomly reported "no matching distribution" | Wrapped installs in a retry loop; transient, not a config problem |
| 5 | **Cache-dir collision (would have invalidated the whole experiment)** | The memory cache path is `cached_memories_robust_{backend}_{model}`, which does not encode the memory-layer configuration. The ablation arm would have silently loaded the baseline's notes and produced a fake "no difference" result | Added an arm suffix (`_noevo`) to the cache path; also sanitised `/` in the model name, which would otherwise create nested directories |
| 6 | Windows path from model name | `deepseek/deepseek-chat` contains `/`, so the log filename split into directories | Replaced `/` and `:` in log and cache names |

## 6. Commands

```bash
cp .env.example .env          # put DEEPSEEK_API_KEY in
bash run_repro.sh smoke       # 1 conversation, 1 trial
bash run_repro.sh baseline    # paper arm, 3 trials
bash run_repro.sh noevo       # ablation arm, 3 trials
```

## 7. Open items

- [ ] Baseline arm, 3 trials
- [ ] Ablation arm, 3 trials
- [ ] Cost / latency per solved question (instrument.py)
- [ ] README for submission, report, slides
