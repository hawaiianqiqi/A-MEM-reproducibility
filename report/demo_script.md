# 15-minute demo recording — script

Recording tool: Zoom → *Share Screen* → local recording. Target 14–15 minutes. Numbers below are
the ones to say out loud; the tables live in `report/report.md` and `results/report_tables.md`.

Keep the terminal font large (16–18 pt) and have four windows ready: this repo in an editor,
`report/report.md`, a terminal, and the GitHub page of `WujiangXu/AgenticMemory`.

---

## 0:00–1:30 — What I reproduced, and why this repository

Say: the target claim was fixed before the first paid call — **Table 1 of A-MEM, the per-category F1
and BLEU-1 on LoCoMo, GPT-4o-mini column**.

Show: the two candidate repositories side by side.
- `agiresearch/A-mem` — the library. Its README says paper results live elsewhere, and it has no
  evaluation script, so nothing in it can be checked against a reported number.
- `WujiangXu/AgenticMemory` — the experiment repo. Ships the dataset, the harness and the prompts.

Say: scope is one of ten conversations (419 turns, 199 questions, all five categories), three trials
per arm, because the assignment allows one benchmark / one table row and a four-day budget.

## 1:30–3:30 — Environment, and the four failures that produced no error message

Say: the setup is the least interesting part of the report and the most expensive part of the work.
Four separate failures, each of which either killed the process with no traceback or produced a
number that looked plausible.

Show `REPRODUCTION.md` §5, rows 3–6, and read the symptom column aloud. Then run the preflight live:

```bash
python check_pipeline_smoke.py --turns 8 --skip-bert
```

Say: this takes two minutes and would have caught three of the four. It prints per-turn build latency,
retrieval context size, one answer per category, and the token/cost totals.

## 3:30–5:30 — The protocol decisions that change the numbers

Three things a reader cannot see from the paper:

1. **Category 5 is scored against the wrong answer.** Show `load_dataset.py:27` (`reference()`).
   The paper's evaluation scored adversarial questions against `adversarial_answer` — the trap. So
   "my model fell for the trap" reads as a good score. Every run uses `--legacy-c5` for like-for-like
   comparison, and the report also gives the strict number.
2. **k.** Show paper Table 5 (k=40/50 for GPT-4o-mini) versus `run_all_experiments.sh` (k=10). This
   run uses 10 and says so.
3. **Dataset size.** The paper describes 7,512 QA pairs; the released file has 1,986. The numbers in
   Table 1 were produced on something larger than what ships with the code.

Say: the backbone is the fourth variable — `deepseek-chat` instead of `gpt-4o-mini`, prompts and
temperatures byte-identical, which is the assignment's edge case A.

## 5:30–8:30 — Our numbers versus the paper's

Show the table in `report/report.md` §4 and walk the columns.

Say: single-hop **44.00 ± 0.32 versus 27.02** (+17.0) and temporal **20.17 versus 12.14** (+8.0) —
a stronger reader. Open-domain **10.25 versus 44.65** (−34.4) — DeepSeek declines to volunteer world
knowledge and answers "not mentioned", which category 3 punishes. Multi-hop **27.39 ± 3.48 versus
45.85** (−18.5) — the one category the paper's thesis rests on, and the one that did not transfer.

Then show the adversarial reversal: **25.76** scored the paper's way, **74.86** scored the task's way
(74% of 141 answers correctly decline). Same predictions, two labels. Say plainly: anyone reading a
leaderboard that puts adversarial F1 beside the other four categories is comparing a
similarity-to-a-wrong-answer metric with four similarity-to-a-right-answer metrics.

## 8:30–11:30 — The change: one mechanism, isolated

Show the diff: `git show 0334040 -- memory_layer_robust.py`.

```python
evo_label, note = (False, note) if self.no_evolution else self.process_memory(note)
```

Say: one line. Notes keep their LLM-extracted metadata; they never gain links, never strengthen tags,
never rewrite their neighbours' context. Retrieval, prompts, k, seeds, metrics are untouched.

Say why this mechanism: paper Table 2 says multi-hop F1 falls 45.85 → 31.24 without evolution → 24.55
without links and evolution, so the arm is the paper's `w/o LG & ME` row.

Show the trap that would have made the whole ablation meaningless (blocker 2 in `REPRODUCTION.md`):
the memory cache path does not encode the memory configuration, so without an arm suffix the
no-evolution run loads the baseline's notes from disk and reports a difference of exactly zero.
Show the commit that added the suffix.

Show the ablation table (`report/report.md` §5). Say:

- Overall 30.39 → 29.61, a difference of 0.78 against a pooled standard error of 1.6 — no overall effect.
- Multi-hop is the only category that moves the predicted way: **27.39 → 23.05, −4.33**. The paper
  reports −21.30 for the same removal. So the direction reproduces, the magnitude does not: a fifth.
- Temporal and open-domain move the *wrong* way (+3.82, +1.52), which is what three-trial noise looks like.
- Be explicit about power: Welch t ≈ 2.1; you need ~8–10 trials per arm to resolve a 4-point effect
  at 3.5-point variance. Say that you would rather report the interval than the point estimate.
- Then the variance finding, which is the one you did not predict: on multi-hop the full arm's std is
  **3.48** versus **0.71** without evolution. The mechanism rewrites neighbours in place, so a note's
  retrievability depends on what arrived after it — nondeterministic machinery feeding a deterministic metric.
- Then the price: the write path is 1,311 vs 419 LLM calls and $0.375 vs $0.033 per build — **11×** —
  for ~4 points on one of five categories.

Interpretation to offer, flagged as a hypothesis: the paper's 21-point gain may be an interaction with
GPT-4o-mini's weak multi-hop synthesis (its full-context baseline scores 18.41 there), not a general
property of linked notes. DeepSeek reaches 27.39 without the scaffolding.

## 11:30–13:30 — Cost, latency, and what the method actually costs to run

Show `results/report_tables.md` cost table.

Say: one conversation is **1,709 LLM calls to build memory** — 419 turns × (1 metadata call + up to
3 evolution calls), i.e. ~4.1 calls per conversational turn — and only 398 calls to answer all 199
questions. The paper reports inference tokens (2,520 per question) but never the construction cost.
Wall clock: 28 minutes to build, 6.6 minutes per answering trial. About CNY 5 to build and CNY 4.7
per trial on DeepSeek.

Say what this means for a practitioner: A-MEM's selling point is small *inference* prompts, but the
write path is where the money goes, and it is the part that scales with conversation length rather
than with question count.

## 13:30–15:00 — What I would tell the next person

Say the four things, in this order:

1. Write the target claim down before the first paid call. Mine was fixed at Table 1, column
   `gpt-4o-mini`, and the ablation was chosen the same hour.
2. Isolate the ablation cache before running anything. This is the failure that produces a clean,
   believable, completely fake "no difference".
3. Print the metric edges next to the first result. A swallowed exception turned BLEU into a column
   of zeros that reads like a low score, not like a bug.
4. Report distributions, not points — the variance is what exposed the BLEU bug (an exactly-zero
   column, not a low one).

Close with the honest limitation: the k=40/50 sensitivity pass was not run because the account held
CNY 22 at that point and each k=40 trial costs roughly four times a k=10 trial. The harness supports
it (`bash run_repro.sh k40`) and the memory caches are reusable.
