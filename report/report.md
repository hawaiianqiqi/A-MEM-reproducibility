# Reproducing A-MEM on LoCoMo: what transfers, what does not

**Course:** FTEC5660 Agentic AI for Business and FinTech — Reproducibility Work
**Name:** Zi Han QIU **Student ID:** 1155268166
**Repository:** https://github.com/hawaiianqiqi/A-MEM-reproducibility
**Demo recording:** https://drive.google.com/file/d/1gQRp74yl6oZx7h6sAq0tHTcVZAK8Wac_/view?usp=sharing

---

## 1. Project summary and what I set out to reproduce

A-MEM (*Agentic Memory for LLM Agents*, arXiv:2502.12110) proposes that an agent's memory should be
organised the way a Zettelkasten is: each conversational turn becomes a structured note, notes are
linked to their nearest neighbours, and adding a note *evolves* the notes around it — their context,
keywords and tags are rewritten in light of the new arrival. The paper's evidence is LoCoMo, a
long-conversation QA benchmark, where A-MEM is reported to roughly double the multi-hop F1 of a
full-context baseline (45.85 vs 18.41) while reading an order of magnitude fewer tokens (2,520 vs
16,910 per question).

**Target claim (fixed before any run):** reproduce the A-MEM column of Table 1 for the GPT-4o-mini
backbone — per-category F1 and BLEU-1 on LoCoMo — using the authors' experiment repository
`WujiangXu/AgenticMemory`.

Table 1 of the paper is the right target because it is the paper's headline quantitative claim and
because every ingredient needed to check it ships with the code: the LoCoMo file, the evaluation
script, the memory implementation and the prompt templates. I deliberately did **not** use
`agiresearch/A-mem`, the library the paper points practitioners to: its README states that paper
results live in the other repository, and it contains no evaluation script, so nothing in it can be
checked against a reported number.

**Scope.** One of the ten released conversations (conversation 0: 419 turns, 199 questions, all five
categories present), three trials per arm. The assignment permits reproducing one benchmark or one
table row; a single conversation keeps the cost inside a CNY 20 budget while still producing a
distribution rather than a single point.

## 2. Environment setup

| Component | Choice | Why |
|---|---|---|
| OS / Python | Windows 11, Python 3.13.12 (venv) | the only interpreter available |
| Repo | `WujiangXu/AgenticMemory` @ `main`, committed as a pristine snapshot before any edit | see §6, blocker 1 |
| Backbone | `deepseek-chat` via `https://api.deepseek.com` | GPT-4o-mini is not reachable from this machine; see §3 |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` (unchanged) | the repo's default |
| Metrics | `nltk` 3.9.1, `rouge-score`, `bert-score` | pinned; see §6, blocker 12 |
| Data | `data/locomo10.json` as released (1,986 QA pairs) | no download needed |

Setup is reproducible with `pip install -r requirements.txt`; the reproduction-specific steps
(model prefetch, NLTK data, offline flags) are documented in the repository README and automated in
`env_bootstrap.py`, because four of them fail silently or fatally if done in the wrong order.

**The backbone substitution is a controlled variable, not a free choice.** Per the assignment's edge
case A, everything except the model identifier is held fixed:

| Knob | Paper | This reproduction |
|---|---|---|
| Provider / base URL | OpenAI / `api.openai.com` | DeepSeek / `api.deepseek.com` |
| Model | `gpt-4o-mini` | `deepseek-chat` |
| Prompts (note construction, evolution, retrieval, answering) | — | byte-identical |
| Temperature (metadata, evolution, answering) | 0.7 | 0.7 |
| Temperature (category 5) | 0.5 | 0.5 |
| `max_tokens` | 1000 | 1000 |
| Retrieval k | 40/50 (Table 5) | 10 (harness default) |
| Metrics code | repo's `utils.py` | same file, one diagnostics-only edit |

The consequence is stated once and applies to every number below: **these results are not directly
comparable with the paper's, because the backbone LLM differs.** What is comparable is the protocol
(same tasks, same metrics, same scoring code) and the internal contrast between the two arms.

## 3. Target, metrics, and the measurement decisions that hide inside them

**Target.** For each of the five LoCoMo categories and for the run as a whole: token-level F1 and
BLEU-1 between the predicted answer and the gold answer, in percent.

- **F1** is the harmonic mean of precision and recall over the *set* of lowercased tokens, after
  replacing `. , ! ?` with spaces (`utils.simple_tokenize`). It rewards content overlap and ignores
  word order.
- **BLEU-1** is unigram precision with a brevity penalty, computed by `nltk.sentence_bleu` with
  `weights=(1,0,0,0)`. It rewards producing the reference's words and punishes padding.

Both are reported as mean ± standard deviation over three trials, where the trials differ only in
the answering seed (42/43/44). Memory construction runs once and is cached; later trials re-run
retrieval and answering. Variance therefore measures the answering stage, which is where the
sampling temperature lives — not memory construction, which the paper never reports. This is a
stated limitation, not an oversight: rebuilding the memory three times would triple the cost to
estimate a quantity nobody quotes.

Three measurement decisions materially change the numbers, and the report would be dishonest without
them:

1. **Category 5 (adversarial) is scored against the wrong answer by default.** Category-5 questions
   have no answer in the conversation — the correct response is "not mentioned". The released
   harness scores them against `"Not mentioned in the conversation"`, which is right, but the
   evaluation that produced the paper's Table 1 scored them against `adversarial_answer`, i.e. the
   *trap*. The repository says so in `load_dataset.py`, and its flag is named `legacy_c5`. Every run
   here uses `--legacy-c5` so that the comparison is like-for-like; §4 also reports the strict
   scoring, recomputed from the stored predictions, because the difference is large enough to be a
   finding in itself.
2. **k.** Table 5 of the paper lists k=40 (single-hop, multi-hop, adversarial) and k=50 (temporal,
   open-domain) for GPT-4o-mini, while the body text says "we primarily employ k=10" and the shipped
   driver uses 10. This reproduction runs k=10 for all trials and adds a one-trial k=40 sensitivity
   pass on the same cached memories (§4), so the sensitivity the paper leaves implicit is measured
   rather than assumed. The k=50 rows and a multi-trial k=40 arm remain unrun for budget reasons.
3. **Dataset size.** The paper describes 7,512 QA pairs; the released `locomo10.json` contains 1,986.
   The reported numbers were therefore produced on a different, larger instance of the benchmark than
   the file that ships with the code. Nothing in the repository can close that gap.

## 4. What I measured versus what the paper reports

Backbone: `deepseek-chat`; conversation 0 only (199 questions); k=10; three answer-seeded trials;
category 5 scored as the paper scored it.

| Category | F1 (ours, mean ± std) | BLEU-1 (ours) | F1 (paper, GPT-4o-mini) | Δ F1 |
|---|---|---|---|---|
| Single-hop (n=70) | 44.00 ± 0.32 | 38.93 ± 0.51 | 27.02 | **+16.98** |
| Multi-hop (n=32) | 27.39 ± 3.48 | 18.52 ± 2.53 | 45.85 | **−18.46** |
| Temporal (n=37) | 20.17 ± 1.07 | 12.86 ± 0.56 | 12.14 | +8.03 |
| Open-domain (n=13) | 10.25 ± 0.64 | 7.26 ± 2.28 | 44.65 | **−34.40** |
| Adversarial (n=47) | 25.76 ± 5.47 | 25.33 ± 5.40 | 50.03 | −24.27 |

Two categories reproduce in the loose sense (same order of magnitude; the paper's ranking across
categories is *not* preserved), two do not, and one — open-domain — is off by a factor of four.

One caveat on precision: the standard deviations above are across answer seeds, not across questions.
With 13 open-domain questions in this conversation, the sampling error on that category is on the
order of ±20 F1 points, so its deviation should be read as "clearly lower", not as a point estimate.
The overall figure (30.39) is dominated by single-hop, which contributes 70 of the 199 questions.

**Why the gaps are where they are.** Single-hop, temporal and open-domain are answered from a single
retrieved note; they measure whether the retrieval found the right turn, which is a property of the
embedding index rather than of the agentic organisation. DeepSeek is simply a stronger reader than
GPT-4o-mini on the single-hop and temporal slices (+17.0, +8.0), and a much more conservative one on
open-domain (−34.4): it tends to answer "not mentioned in the conversation" instead of volunteering
world knowledge, which is exactly what category 3 punishes. Multi-hop is the one category the paper's
thesis actually rests on, and it is the one that did not transfer (−18.5). That is the result worth
following up, and §5 follows it up.

**The adversarial column is a measurement artefact, in both directions.** Scored the paper's way
(against the trap answer), A-MEM gets 25.76 here versus 50.03 in the paper. Scored the way the task
is actually specified — the correct reply is "not mentioned", so a declining answer is a *correct*
answer — the same predictions score **74.86**, with 74% of the 141 answers declining correctly. The
paper's 50.03 and this 74.86 describe the same behaviour under two labels. Any leaderboard that puts
adversarial F1 next to the other four categories is comparing a similarity-to-a-wrong-answer metric
with four similarity-to-a-right-answer metrics.

**Retrieval depth is the single largest setting gap, and it is now measured.** One extra trial at
k=40 — the value Table 5 lists for this backbone — reuses the identical cached memories and differs
only in how many notes are retrieved:

| Category | k=10 (3 trials) | k=40 (1 trial) | Δ | Paper |
|---|---|---|---|---|
| Single-hop | 44.00 ± 0.32 | **55.08** | +11.1 | 27.02 |
| Multi-hop | 27.39 ± 3.48 | **29.90** | +2.5 | 45.85 |
| Temporal | 20.17 ± 1.07 | **25.42** | +5.3 | 12.14 |
| Open-domain | 10.25 ± 0.64 | 10.32 | +0.1 | 44.65 |
| Adversarial | 25.76 ± 5.47 | **41.81** | +16.1 | 50.03 |
| **Overall** | **30.39 ± 1.25** | **39.46** | **+9.07** | — |

Two conclusions follow. First, the overall 9-point gap between the arms of this table is mostly
*setting*, not model: deepening retrieval closes most of the distance to the paper on adversarial
(41.81 vs 50.03, from a 24-point deficit) and helps every category except open-domain. A single-run
reproduction that only reports k=10 would have attributed all of that to the backbone swap. Second,
and more telling, **the two categories the paper's thesis rests on barely move**: multi-hop gains
2.5 points and open-domain 0.1, leaving 16–34 point deficits that retrieval depth cannot explain.
The mechanism-sensitive categories are exactly the ones that do not respond to k — which is
consistent with §5's reading that what differs on multi-hop is the backbone's ability to use
pre-computed links, not how much raw context it receives. The k=40 trial also prices the setting:
9.60 M input tokens against 2.37 M at k=10, $2.69 against $0.67 per trial.

**Cost and latency** (measured by intercepting every `litellm.completion` call; `instrument.py`):

| Phase | Calls | Input tokens | Est. cost | Wall clock |
|---|---|---|---|---|
| Baseline: memory build (419 turns) | 1,311 | 2.0 M | $0.375 | 28 min |
| Baseline: answering (199 questions) | 398 per trial | 2.37 M per trial | $0.67 per trial | 6.6 min |
| No-evolution: memory build | 419 | 0.34 M | $0.033 | 7 min |
| No-evolution: answering | 398 per trial | 0.30 M per trial | $0.084 per trial | 6.1 min |
| Baseline at k=40: answering | 398 per trial | 9.60 M per trial | $2.69 per trial | 11.5 min |

Two numbers here are not visible in the paper. First, **the write path is 3.1 LLM calls per
conversational turn** (419 metadata extractions + 892 evolution calls), against 2 calls per question
on the read path — building memory costs more calls than answering every question about it. Second,
**the evolution step inflates the read path too**: with links in place, 10 retrieved notes drag their
neighbours into the prompt, so one question consumes 11,910 input tokens against 1,508 without
evolution — 7.9× — for the same k. A-MEM's selling point is small inference prompts relative to a
16,910-token full-context baseline; at k=10 with neighbour expansion that advantage is 1.4×, not 6.7×,
and the mechanism that is supposed to buy it is the one inflating it.

Mean latency is 0.87–0.93 s per call on DeepSeek, so wall clock is dominated by call count, not by
model speed. Total spend for the study, read from the provider's balance endpoint rather than from
the token estimate: **CNY 14.8 (~$2.1)** for roughly 6,300 calls, including one discarded build (the
run whose BLEU column was broken) and the preflight runs.

## 5. The change, and what happened to the numbers

**The change: disable memory evolution** (`--no-evolution`, one flag, one code path). With the flag
set, `add_note` stores each note with its LLM-extracted metadata but never runs `process_memory`, so
notes never gain links, never strengthen their tags, and never rewrite their neighbours' context.
Retrieval, prompts, k, seeds, metrics and the embedding index are untouched. The two arms differ in
exactly one mechanism.

This is the right mechanism to isolate because it is the one the paper credits for its largest gain:
Table 2 reports multi-hop F1 falling from 45.85 (full) to 31.24 (without memory evolution) to 24.55
(without link generation and evolution). Skipping `process_memory` removes both, so the arm
corresponds to the paper's `w/o LG & ME` row and predicts a multi-hop drop of roughly 21 F1 points.

| Category | Full A-MEM | Without evolution | Δ (ours) | Paper: full → w/o LG & ME | Paper Δ |
|---|---|---|---|---|---|
| Single-hop | 44.00 ± 0.32 | 42.55 ± 4.43 | −1.45 | 27.02 → — | — |
| Multi-hop | 27.39 ± 3.48 | 23.05 ± 0.71 | **−4.33** | 45.85 → 24.55 | **−21.30** |
| Temporal | 20.17 ± 1.07 | 23.98 ± 3.92 | +3.82 | 12.14 → — | — |
| Open-domain | 10.25 ± 0.64 | 11.77 ± 4.26 | +1.52 | 44.65 → — | — |
| Adversarial | 25.76 ± 5.47 | 24.16 ± 0.91 | −1.60 | 50.03 → — | — |
| **Overall** | **30.39 ± 1.25** | **29.61 ± 2.55** | **−0.78** | — | — |

Three trials per arm, same questions, same seeds, same prompts; the only difference is whether
`process_memory` runs.

**Only one of the five categories moves the way the paper says it should, and it moves a fifth as
far.** Multi-hop falls from 27.39 to 23.05 (−4.33) where the paper reports −21.30 for the same
mechanism removed. The other four categories change by between −1.60 and +3.82, in both directions,
which is what noise looks like: over the full question set the arms differ by 0.78 F1 points, against
a pooled standard error of 1.6.

**This is not a clean refutation, and it should not be read as one.** The effect is in the predicted
direction on the predicted category, but three trials cannot resolve a 4-point difference when the
full arm's own standard deviation on that category is 3.5 points (Welch t ≈ 2.1). A properly powered
test of a 4-point effect at that variance needs roughly 8–10 trials per arm, which the remaining
budget did not cover. What the data does support is a claim about *magnitude*: whatever the evolution
step contributes here, it is not the 21-point contribution the paper reports.

**Why the gap is plausible rather than surprising.** The paper's multi-hop gain is measured against
a backbone whose full-context baseline collapses on multi-hop questions (LoCoMo 18.41 F1), which
suggests GPT-4o-mini struggles to synthesise across retrieved passages on its own. Pre-computing the
links — which is what the evolution step does — hands it structure it cannot build. DeepSeek is a
stronger multi-hop reader: it reaches 27.39 *without* that scaffolding, and the same scaffolding then
adds very little. If that reading is right, A-MEM's headline number describes an interaction between
the mechanism and a specific backbone's weakness, not a property of agentic memory in general.

**The mechanism also injects variance.** On multi-hop, the full arm's standard deviation is 3.48
against 0.71 without evolution. The evolution step rewrites neighbours' context and tags in place, so
a note's retrievability depends on what arrived after it — a nondeterministic process feeding a
deterministic metric. That is a cost the paper's single-run reporting cannot show.

**What the mechanism costs.** Removing it cuts the write path from 1,311 LLM calls to 419 for the
same 419 turns — 3.1 calls per turn down to 1.0 — and the build from $0.375 to $0.033, an **11×
reduction**: the evolution prompts carry five neighbour notes each, so they are both more numerous and
longer. Read against the ablation table, the trade is roughly 11× the cost of the entire write path
for ~4 F1 points on one of five categories. A practitioner deciding whether to enable evolution should
see that ratio before the paper's multi-hop headline.

## 6. Debug diary

The blockers below are ordered by how much time they cost, and each one is a case where the code
kept running and told me nothing.

| # | Symptom | Root cause | Fix |
|---|---|---|---|
| 1 | `git clone` hung past 180 s; two different repositories silently unpacked into the same `A-mem-main` directory | GitHub throughput ~30 KB/s here; both archives share a top-level name, so the library overwrote the experiment repo file by file | Fetched both as zips, compared file lists, kept only `WujiangXu/AgenticMemory`, committed it as a pristine snapshot before editing |
| 2 | **The ablation would have reported "no difference"** | The memory cache path is `cached_memories_robust_{backend}_{model}` — it does not encode the memory-layer configuration. The no-evolution arm would have loaded the *baseline's* notes from disk and measured nothing | Added an arm suffix to the cache path, and sanitised `/` in the model name, which would otherwise have created nested directories on Windows |
| 3 | `import utils` exited with SIGTERM and zero output, four times | `utils.py` calls `nltk.download('punkt')` and `('wordnet')` at import time; the NLTK data host is unreachable here and the failed fetch takes the interpreter down before anything can print | Look resources up on disk first; fetch only with `NLTK_ALLOW_DOWNLOAD=1` |
| 4 | Next import failed with `BadZipFile` | The interrupted download had left a 1 MB fragment of the 10.7 MB `wordnet.zip` behind, and `nltk.data.find` crashed reading it | Catch unreadable resources and say so; re-fetched `wordnet` from a jsDelivr mirror of `nltk/nltk_data` |
| 5 | Next import died silently, log ending at `Could not resolve the revision ... (502 Bad Gateway)` | `sentence-transformers` resolves a model revision over the network at import time; the request fails and kills the process | `env_bootstrap.py` sets `HF_HUB_OFFLINE=1` / `TRANSFORMERS_OFFLINE=1` before the first heavy import, so the cached weights load without asking |
| 6 | **Every BLEU-1 cell was 0.00, with no error** | `nltk` 3.8.1 calls `Fraction(n, d, _normalize=False)`; that keyword was removed in Python 3.12. `calculate_bleu_scores` catches the `TypeError` and returns 0.0 | Pinned `nltk==3.9.1`; added a one-time loud warning so the same breakage cannot hide again; discarded the affected run |
| 7 | pip 403 against the TUNA mirror while `curl` got 200 | The mirror rejects pip's TLS fingerprint | Switched to the aliyun mirror after testing four |
| 8 | `bert_score` demanded a 1.4 GB `roberta-large` with no env override | default model is hard-coded to `roberta-large`; the failure path would have been swallowed by the same bare `except` that hid blocker 6 | Pre-fetched from the HF mirror and verified end to end (all 14 metric fields populated, `bert_f1 = 0.858` on a hand-checked pair); still not used as evidence, since the paper does not report it |

An environment preflight (`check_pipeline_smoke.py`) was written after blocker 5 and turns this class
of failure from a two-hour loss into a two-minute report: eight turns of memory plus one question per
category, printing per-stage latency, tokens and cost.

## 7. Conclusion

**What reproduced.** The protocol reproduced end to end: a clean checkout plus a key produces
per-category F1 and BLEU-1 on the released data, with the same metric definitions and the same
scoring code the paper used, in about 35 minutes on one consumer laptop and one conversation.
Within-run variance is small (std 0.3–5.5 F1 points across categories, largest on multi-hop and
adversarial), so the harness is stable enough to support an ablation.

**What did not reproduce.** The absolute numbers, for reasons the assignment explicitly allows and
which I have tried to make legible rather than excuse: a different backbone, a smaller evaluation
instance than the paper describes (1,986 vs 7,512 questions), and a category-5 scoring convention
that inflates the paper's adversarial column. Retrieval depth — the other obvious setting gap — was
measured, not excused: at k=40 it recovers 9 of the missing points overall and most of the
adversarial gap, but leaves multi-hop and open-domain essentially unmoved, so the model and dataset
remain the best explanations for those two. More substantively, the paper's structural claim — that
removing link generation and memory evolution costs about 21 multi-hop F1 points — does not hold at
that magnitude here: the same removal costs 4.33 points, in the predicted direction, on the predicted
category, but only a fifth of the size, and not separable from noise at three trials. On this
backbone the mechanism is real but small, and it is priced at 11× the cost of the write path it
modifies.

**The honest summary of the ablation is therefore that it is inconclusive in the direction the
assignment cares about.** It is not a failed reproduction: the direction matched, the cost effect was
large and clean, and the variance effect (3.48 vs 0.71 on multi-hop) was not something I expected.
But a 3-trial test of a 4-point effect at that variance cannot support a claim either way, and I
would rather report the confidence interval than the point estimate.

**What is worth reporting even if it "failed".** Three of the findings here are not about A-MEM at
all; they are about the practice of reproducing agentic systems. A cache path that omits the
configuration silently turns an ablation into a no-op. A swallowed exception turns a broken metric
into a table of zeros that reads like a low score. A scoring convention that scores against the wrong
answer turns a failure mode into a headline number. Each of these would have been invisible in a
single-run report, and each was found only because the numbers were reported as a distribution and
checked against a second convention.

**Remaining unfinished items.** The k=40 sensitivity pass is one trial, so its per-category cells
carry no variance estimate (the k=10 baseline's own std bounds suggest the adversarial and temporal
gains are real, but the multi-hop +2.5 is within noise). The k=50 rows, the ablation arm at k=40,
and a multi-trial k=40 would each cost another answering trial at roughly four times the k=10 rate;
the harness supports all three (`bash run_repro.sh k40`), and the memory caches are reusable, so
they are a 30-minute job each for anyone with the budget. Reporting one k at one trial per
sensitivity cell is a limitation of this submission, not a property of the method.

**Advice to the next person.** Run the environment preflight before anything else; freeze the target
claim in writing before the first paid call; isolate the ablation cache on day one; and print the
metric definition's edge cases (empty prediction, category-5 reference, int vs str answers) next to
the first result, because every one of those was silently wrong here before it was caught.
