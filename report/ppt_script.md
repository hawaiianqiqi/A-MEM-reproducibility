# FTEC5660 复现录屏 · 逐页讲稿（配合 PPT）

> 对应 `FTEC5660_Reproducibility_Recording.pptx`（16 页）。每页念白即 PPT 里的演讲者备注，
> 英文、第一人称、按 150 词/分钟设计，全程约 14–15 分钟。念完一页翻一页即可，不需要再切换窗口。

---

**P1 · 封面**
I set the target before I spent a single yuan: reproduce the A-MEM column of Table 1 in the paper, on LoCoMo, for the GPT-4o-mini backbone — the per-category F1 and BLEU-1. I reproduce one table row, not the whole paper, on one conversation, three trials per arm. The backbone is swapped to DeepSeek under the assignment's edge case A, with prompts, temperatures and max tokens held byte-identical.

**P2 · The target: one table row**
My target was fixed before the first paid call: the A-MEM column of Table 1 — the per-category F1 and BLEU-1 on LoCoMo, for the GPT-4o-mini backbone. One table row, not the whole paper.

**P3 · Which repository**
Two repositories share almost the same name, and choosing wrong would have cost me two days. The library the paper advertises has no evaluation script — nothing in it can be checked against a reported number. The numbers live in the experiment repository, which ships the dataset, the harness and the prompts. That is the one I reproduce.

**P4 · Scope and the controlled swap**
Scope: one of ten conversations — 419 turns, 199 questions, all five categories — and three trials per arm. The assignment allows one benchmark; one conversation still gives me a distribution instead of a single point. The backbone is swapped to deepseek-chat, with prompts, temperatures and max tokens byte-identical — a controlled swap, not a free choice.

**P5 · Four failures that never printed a traceback**
The setup is the least interesting part of the report and the most expensive part of the work. Four failures never printed a traceback. Importing the metrics module killed the interpreter with no output, twice, for two unrelated reasons: it downloaded NLTK data at import time, and sentence-transformers resolved a model revision over the network. Every entry point died before printing the reason. The worst one is the cache trap — it is not an environment problem, it is an experimental-design problem: the memory cache path does not encode the memory configuration, so the ablation arm would have loaded the baseline's notes from disk and reported a difference of exactly zero — clean, believable, and completely fake.

**P6 · The preflight**
This is the preflight I wrote after those four failures. Eight turns of memory, then one question per category. It prints per-turn build latency, the retrieval context size, one answer per category, and the token and cost totals. Two and a half minutes, and it would have caught three of the four failures before any real money was spent. Keep your eye on the category-five line — prediction 'not mentioned', reference is the trap answer, F1 zero. That zero is the scam I will explain in ninety seconds.

**P7 · Category 5 is scored against the trap**
Category five asks about something never mentioned, and the correct answer is 'not mentioned'. But the evaluation behind the paper's numbers scored those questions against adversarial_answer — the trap itself — so falling for the trap reads as a high score. Four hundred and forty-four of the four hundred and forty-six have no gold answer at all. Same predictions, two labels: scored the paper's way, adversarial F1 is 25.76; scored the task's way, it is 74.86. Anyone putting adversarial F1 next to the other four is comparing similarity-to-a-wrong-answer with similarity-to-a-right-answer.

**P8 · Retrieval depth k**
Second setting: retrieval depth. Table 5 of the paper lists k equals forty and fifty for this backbone. The driver that ships with the repository defaults to ten. I ran ten as the baseline and then added one trial at forty on the identical cached memories — so I could measure the gap instead of just declaring it.

**P9 · Two more gaps: the dataset and the model**
Third: the paper describes 7,512 QA pairs. The released file has 1,986. Table 1 was produced on something larger than what ships with the code — which alone makes an exact match impossible. And the fourth variable is mine, not theirs: deepseek-chat instead of gpt-4o-mini. Prompts, temperatures and max tokens are byte-identical — the assignment's edge case A, a controlled swap, not a free choice.

**P10 · Results vs the paper (k=10)**
Three trials, mean and standard deviation, the same 199 questions. Overall 30.39 plus or minus 1.25 against the paper's per-category numbers — the paper does not report an overall column, which is itself worth noticing, because the average hides the disagreement. Single-hop is 44.00 against 27.02, seventeen points stronger; temporal 20.17 against 12.14. DeepSeek is simply the better reader there. Open-domain collapses to 10.25 against 44.65 — DeepSeek answers 'not mentioned' and category three punishes exactly that. And multi-hop, the category the whole thesis rests on, is 27.39 against 45.85 — that number did not transfer. Note the standard deviation: 3.48, ten times the spread of single-hop.

**P11 · k=40: the gap was the setting**
This is the most instructive comparison in the whole study, and it cost nineteen yuan. Raising k from ten to forty moves overall F1 from 30.39 to 39.46, and adversarial from a twenty-four-point deficit to almost matching the paper. So most of the headline gap was my setting, not the model — a single-k reproduction would have blamed the backbone for all of it. But the two categories the thesis rests on barely move: multi-hop plus 2.5, open-domain plus 0.1. Retrieval depth explains the overall gap; it does not explain the mechanism-sensitive categories. That decomposition only exists because I ran the pass.

**P12 · The modification: one line, one flag**
One flag, one code path, one commit. With the flag on, a note keeps its LLM-extracted metadata — title, keywords, tags, summary — but it never gains links, never strengthens its tags, never rewrites its neighbours. Retrieval, prompts, k, seeds and metrics are untouched, so the two arms differ in one mechanism only. And the cache trap: the cache path encodes backend and model, not the memory configuration. Without an arm suffix, both arms share one directory, the ablation silently reloads the baseline's notes, and the experiment reports a difference of zero — a perfectly plausible null result produced by a directory name. I fixed it before the first run.

**P13 · Ablation: direction yes, magnitude no**
Three trials per arm, same questions, same seeds, same prompts. Overall: 30.39 to 29.61, a difference of 0.78 against a pooled standard error of 1.6 — no overall effect. Multi-hop is the only category that moves the predicted way: 27.39 to 23.05, minus 4.33. The paper reports minus 21.3 for the same removal. The direction reproduces; the magnitude is a fifth. Temporal and open-domain move the wrong way, which is what three-trial noise looks like. And one thing I did not predict: on multi-hop, the full arm's spread is 3.48 and without evolution it is 0.71 — the mechanism rewrites neighbours in place, so a note's retrievability depends on what arrived after it.

**P14 · What the mechanism costs**
Every number here comes from intercepting each completion call, so it is measured, not projected. Building memory for one conversation takes 1,311 calls — 419 metadata extractions plus up to three evolution calls each, about 3.1 calls per turn — against 398 calls to answer all 199 questions. Remove the mechanism and the write path drops from 1,311 calls to 419, and from thirty-eight cents to three cents — eleven times cheaper, four times faster. And the cost is not confined to writing: with links in place, the ten retrieved notes drag their neighbours into the prompt, so one question consumes 11,910 input tokens against 1,508 without evolution — eight times. Total spend for the whole study, read from the provider's balance endpoint: fourteen point eight yuan, about two dollars, for roughly 6,300 calls.

**P15 · Advice — and the number that matters**
Four things I would tell whoever does this next. One: write the target claim down before the first paid call. Two: isolate the ablation cache before running anything — this is the failure that produces a clean, believable, completely fake null result. Three: print the metric edges next to the first result — a swallowed exception turned BLEU into a column of zeros that reads like a low score, not a bug. Four: report distributions, not points. And I close on the k=40 pass, because it is the single most instructive number here: nine points of overall gap were my setting; sixteen to thirty-four points on multi-hop and open-domain were not. A reproduction that measures only one setting cannot tell those two apart — and that distinction is the actual deliverable.

**P16 · Thank you**
Everything is in the repository: the pristine snapshot, the backend swap, the evaluation infrastructure, the ablation, each environment fix, and the docs — the preflight, the raw trial JSONs so every number can be recomputed without paying for a run, and no API key anywhere in the history. Thank you.

---

## 录制要点

- **时长**：念白按 150 词/分钟，全程 14–15 分钟。超时先砍 P10 的 open-domain 句和 P14 的 read-path 句；**不要砍 P12（缓存陷阱）和 P15（k 分解）**。
- **Zoom**：Share Screen → 单窗口（或直接共享 PowerPoint 放映窗口）→ Record on this Computer。
- **口误**：数字说错就地重说一遍，别整段重录。
- **备注**：这份讲稿与 PPT 每页的演讲者备注逐字一致，放映时在 PowerPoint 里开"演示者视图"也能看到同样的稿子。
