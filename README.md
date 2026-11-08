# A-MEM on LoCoMo — reproducibility study

A reproduction of **A-MEM: Agentic Memory for LLM Agents** (arXiv:2502.12110), Table 1, plus a
one-mechanism ablation, done for FTEC5660 *Agentic AI for Business and FinTech*.

Upstream experiment code: [`WujiangXu/AgenticMemory`](https://github.com/WujiangXu/AgenticMemory)
(kept unmodified as the first commit in this repository; see `UPSTREAM_README.md`).

| | |
|---|---|
| Target claim | A-MEM's per-category F1 / BLEU-1 on LoCoMo QA (paper Table 1) |
| Backbone | `deepseek-chat` — GPT-4o-mini is unavailable here, so the swap is treated as a controlled variable |
| Scope | conversation 0 of the released `data/locomo10.json` (419 turns, 199 questions), 3 trials per arm |
| Modification | `--no-evolution`: the memory-evolution step is skipped, everything else is held fixed |

## Headline result

Backbone `deepseek-chat`, k=10, three answer-seeded trials, category 5 scored as the paper scored it.
Full discussion and limitations: `report/report.md`.

| Category | F1 (ours) | BLEU-1 (ours) | F1 (paper, GPT-4o-mini) |
|---|---|---|---|
| Single-hop (n=70) | 44.00 ± 0.32 | 38.93 ± 0.51 | 27.02 |
| Multi-hop (n=32) | 27.39 ± 3.48 | 18.52 ± 2.53 | 45.85 |
| Temporal (n=37) | 20.17 ± 1.07 | 12.86 ± 0.56 | 12.14 |
| Open-domain (n=13) | 10.25 ± 0.64 | 7.26 ± 2.28 | 44.65 |
| Adversarial (n=47) | 25.76 ± 5.47 | 25.33 ± 5.40 | 50.03 |
| **Overall** | **30.39 ± 1.25** | **25.52 ± 1.65** | — |

Three findings that matter more than the table: the same predictions score **74.86** on adversarial
questions when scored by the task's actual rule ("not mentioned" is correct) instead of against the
trap answer; BLEU-1 is silently `0.00` on Python ≥ 3.12 with the repository's unpinned `nltk`; and
the memory cache path does not encode the memory configuration, so a naive ablation measures nothing.
All three are documented in `REPRODUCTION.md` and in §6 of the report.

A one-trial **k=40 sensitivity pass** on the same cached memories (k is the setting Table 5 of the
paper actually uses) recovers most of the overall gap — **39.46 vs 30.39 at k=10**, adversarial
41.81 vs 50.03 — but multi-hop and open-domain barely move (+2.5, +0.1). Retrieval depth explains
the headline gap; it does not explain the mechanism-sensitive categories. It also costs 4× the input
tokens per trial (9.60 M vs 2.37 M).

## Ablation: what the evolution step is worth on this backbone

`--no-evolution`, three trials per arm, everything else held fixed:

| Category | Full A-MEM | Without evolution | Δ | Paper Δ (w/o LG & ME) |
|---|---|---|---|---|
| Single-hop | 44.00 ± 0.32 | 42.55 ± 4.43 | −1.45 | — |
| Multi-hop | 27.39 ± 3.48 | 23.05 ± 0.71 | **−4.33** | **−21.30** |
| Temporal | 20.17 ± 1.07 | 23.98 ± 3.92 | +3.82 | — |
| Open-domain | 10.25 ± 0.64 | 11.77 ± 4.26 | +1.52 | — |
| Adversarial | 25.76 ± 5.47 | 24.16 ± 0.91 | −1.60 | — |
| **Overall** | **30.39 ± 1.25** | **29.61 ± 2.55** | −0.78 | — |

The direction matches the paper on the expected category, the magnitude is a fifth of it, and three
trials cannot separate a 4-point effect from noise at that variance (Welch t ≈ 2.1). The write path
costs 11× more with the mechanism enabled ($0.375 vs $0.033 per conversation build) — 1,311 vs 419
LLM calls for the same 419 turns.

## Install

Requires Python ≥ 3.10 (developed on 3.13) and a DeepSeek API key.

```bash
python -m venv .venv
source .venv/bin/activate           # Windows: .venv\Scripts\activate
pip install -r requirements.txt     # nltk is pinned: see "Known pitfalls" below

cp .env.example .env                # then put DEEPSEEK_API_KEY in it; .env is git-ignored
```

Two model assets must be present before the first run, because this environment has no access to
`huggingface.co` and `sentence-transformers` resolves revisions over the network at import time:

```bash
# embedding model used by the memory index (+ roberta-large if you want bert_f1)
HF_ENDPOINT=https://hf-mirror.com python -c "
from huggingface_hub import snapshot_download
snapshot_download('sentence-transformers/all-MiniLM-L6-v2')
snapshot_download('roberta-large')"
```

NLTK data (`punkt`, `punkt_tab`, `wordnet`) must be in `~/nltk_data`:

```bash
python - <<'EOF'
import os, urllib.request, zipfile, io
base = "https://cdn.jsdelivr.net/gh/nltk/nltk_data@gh-pages/packages"
for path, kind in [("tokenizers/punkt.zip", "tokenizers"),
                   ("tokenizers/punkt_tab.zip", "tokenizers"),
                   ("corpora/wordnet.zip", "corpora")]:
    dst = os.path.expanduser(f"~/nltk_data/{kind}")
    os.makedirs(dst, exist_ok=True)
    data = urllib.request.urlopen(f"{base}/{path}", timeout=60).read()
    zipfile.ZipFile(io.BytesIO(data)).extractall(dst)
    print("installed", path)
EOF
```

Check the environment before spending money on API calls — this takes two minutes and catches the
class of failure that otherwise surfaces after a 30-minute memory build:

```bash
python check_pipeline_smoke.py --turns 8 --skip-bert
```

## Run

```bash
bash run_repro.sh smoke       # 1 conversation, 1 trial: proves the chain end to end
bash run_repro.sh baseline    # paper arm: 3 trials, memory built once and cached
bash run_repro.sh noevo       # MODIFICATION arm: identical, evolution skipped
bash run_repro.sh k40         # optional: k=40 sensitivity pass (paper Table 5)
```

Or drive the harness directly:

```bash
python repro_runner.py --tag baseline --trials 3 --legacy-c5
python repro_runner.py --tag noevo --trials 3 --legacy-c5 --no-evolution
python analyze_results.py --arms baseline noevo    # -> results/report_tables.md
```

`--legacy-c5` matches the paper's category-5 scoring (against the adversarial answer). Drop it to
score category 5 the way the task is specified; `analyze_results.py` reports both from one run.

Cost on DeepSeek for the full scope: about CNY 5 for a memory build, CNY 4.7 per answering trial,
35 minutes and 6.6 minutes respectively on one laptop.

## Layout

| Path | What it is |
|---|---|
| `memory_layer_robust.py`, `utils.py`, `load_dataset.py`, `test_advanced_robust.py` | upstream harness (edits marked `MODIFICATION` in the diff) |
| `repro_runner.py` | multi-trial runner: mean ± std per category, cost accounting |
| `instrument.py` | intercepts `litellm.completion` for tokens, latency and cost |
| `analyze_results.py` | turns trial JSONs into report tables; re-scores category 5 strictly |
| `check_pipeline_smoke.py` | 2-minute environment preflight |
| `env_bootstrap.py` | loads `.env`, forces offline model loading before the first heavy import |
| `run_repro.sh` | the four phases above, in cost order |
| `REPRODUCTION.md` | working notes: target, protocol assumptions, debug diary |
| `report/report.md` | the written report |

## The modification

`--no-evolution` makes `add_note` skip `process_memory`, so a note keeps its LLM-extracted metadata
but never gains links, never strengthens its tags, and never rewrites its neighbours' context.
Retrieval, prompts, k, seeds and metrics are untouched.

This is the mechanism the paper credits for its largest gain (Table 2: multi-hop F1 45.85 → 31.24
without evolution → 24.55 without links and evolution), so the arm is directly comparable to the
paper's `w/o LG & ME` row. Memory caches are kept per arm, because the cache path does not otherwise
encode the memory configuration and the two arms would silently share notes.

## Known pitfalls (all hit during this work)

- `nltk` 3.8.1 + Python ≥ 3.12 → `Fraction(_normalize=...)` `TypeError` → BLEU silently 0.0. Pinned to 3.9.1.
- Importing `utils.py` downloads NLTK data; with the data host unreachable the process dies without a traceback.
- `sentence-transformers` resolves a model revision at import; set `HF_HUB_OFFLINE=1` (done in `env_bootstrap.py`).
- The memory cache path omits the memory-layer configuration; isolate caches per arm or the ablation is a no-op.
- The paper describes 7,512 QA pairs but the released file has 1,986, and Table 5 uses k=40/50 while the shipped driver uses 10 (the k=40 gap is measured in §4 of the report, not just declared).

## Citation

```bibtex
@inproceedings{xu2025amem,
  title={A-Mem: Agentic memory for llm agents},
  author={Xu, Wujiang and Liang, Zujie and Mei, Kai and Gao, Hang and Tan, Juntao and Zhang, Yongfeng},
  booktitle={Advances in Neural Information Processing Systems},
  year={2025}
}
```
