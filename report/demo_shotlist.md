# 录屏拍摄脚本（逐句 + 逐画面）

目标片长 14–15 分钟。每条 **【画面】** 给出窗口、文件、具体位置；紧随其后的「」里是**逐字念白**。
念白的语言按课程要求用英文；若你想用中文讲，同一批画面和数字照用，只要把句子翻过去。

所有路径以仓库根 `D:\qzh\2026-11-08-15-01-26\repro\A-mem-main` 为基准。
行号对应当前 HEAD（`86929d2`）。

---

## 开录前 10 分钟：必须准备的 6 个窗口

按这个顺序打开，录屏时用 `Alt+Tab` 循环，不要现场找文件。

| # | 窗口 | 打开到哪 | 用途 |
|---|---|---|---|
| 1 | VS Code（**可选**） | 打开整个仓库 | 只在你想跳转看上下文时才用；代码展示可以完全用窗口 2 的展板脚本代替 |
| 2 | VS Code 内置终端 | `cd` 到仓库根，字体调到 **18pt** | 跑命令、看日志 |
| 3 | Word / WPS | `report/FTEC5660_Reproducibility_Report.docx` | 展示报告表格 |
| 4 | 浏览器标签 A | 论文 HTML：`arxiv.org/html/2502.12110v1`，滚到 **Table 1** | 对照论文数字 |
| 5 | 浏览器标签 B | 你的 GitHub 仓库首页（推完才有） | 开场/收尾展示 |
| 6 | 文件管理器 | `results/` 目录 | 展示原始 JSON |

**开录前必做三件事**（否则会被扣分）：

1. 报告首页第 5 行还有占位符：`**Repository:** https://github.com/[your-account]/amem-loco-repro`
   → 换成你真实的 GitHub 地址。录屏时这个会入镜。
2. 同一行的 `**Demo recording:** [link]` 先留着，录完再填。
3. 关掉所有含 `.env` 的标签页；终端里**不要** `cat .env`。

**一条铁律：全程不现场调用付费 API。** 预检、实验都以"展示已保存的日志/结果"的方式呈现，
现场只跑零成本的 `git`、`grep`、`sed`、`python -c` 读文件。这样 NG 重录不花钱。

---

## 0:00–1:30｜要复现什么，为什么是这个仓库

**【画面 0-A】（0:00）**
浏览器标签 A → 论文 **Table 1**，用鼠标圈住 `A-MEM` 那一列（gpt-4o-mini 子表）。

念：
> "My target was fixed before the first paid call: the A-MEM column of Table 1 — the per-category
> F1 and BLEU-1 on LoCoMo, for the GPT-4o-mini backbone. One table row, not the whole paper."

**【画面 0-B】（0:30）**
浏览器开两个标签并排：`github.com/agiresearch/A-mem` 和 `github.com/WujiangXu/AgenticMemory`。
先在库版 README 里**选中第 18 行那句**（"the results … are in the other repository"），再切到实验仓库，
指一下根目录的 `test_advanced_robust.py`、`data/locomo10.json`。

念：
> "Two repositories share almost the same name, and choosing wrong would have cost me two days.
> The library the paper advertises has no evaluation script — nothing in it can be checked against a
> reported number. The numbers live in the experiment repository, which ships the dataset, the
> harness and the prompts. That is the one I reproduce."

**【画面 0-C】（1:05）**
Word 打开报告，停在第 1 节 **Scope** 那段（"One of the ten released conversations …"）。

念：
> "Scope: one of ten conversations — 419 turns, 199 questions, all five categories — and three
> trials per arm. The assignment allows one benchmark; one conversation still gives me a
> distribution instead of a single point."

---

## 1:30–3:30｜环境：四个不报错的失败

**【画面 1-A】（1:30）**
Word → **§6 Debug diary** 表格。鼠标依次停在 **第 5、7、9、10 行**（加粗的那几条）的
"Symptom" 列上，逐条读。

念：
> "The setup is the least interesting part of the report and the most expensive part of the work.
> Four failures here never printed a traceback. Importing the metrics module killed the interpreter
> with no output, twice, for two unrelated reasons: it downloaded NLTK data at import time, and
> sentence-transformers resolved a model revision over the network. Every entry point died before
> printing the reason."
>
> "The worst one is row five, and it is not an environment problem — it is an experimental-design
> problem. The memory cache path is `cached_memories_robust_{backend}_{model}`. It does not encode
> the memory configuration. So the ablation arm would have loaded the baseline's notes from disk and
> reported a difference of exactly zero — clean, believable and completely fake."

**【画面 1-B】（2:40）**
切终端，展示**已跑好的**预检日志（不要现场跑，2.5 分钟）：

```bash
grep -v "Loading weights\|Could not reach" report/preflight_demo.log | tail -22
```

念（指着 `build: 23s total, 2.9s/turn, 8 notes` 和末尾 `calls=31 errors=0`）：
> "This is the preflight I wrote after those four failures. Eight turns of memory, then one question
> per category. It prints per-turn build latency, the retrieval context size, one answer per
> category, and the token and cost totals. Two and a half minutes, and it would have caught three of
> the four failures before any real money was spent."

**【画面 1-C】（3:10）**
放大光标停在同一份日志的第 5 行答案上：
`cat 5: … pred='Not mentioned in the conversation' | ref='self-care is important' | F1=0.000`

念：
> "Keep your eye on this line — category five, prediction 'not mentioned', reference is the trap
> answer, F1 zero. That zero is the scam I'll explain in ninety seconds."

---

## 3:30–5:30｜三个改变数字的协议决策

**【画面 2-A】（3:30）**
终端执行（不用编辑器，带行号打印）：

```bash
bash report/show_exhibit.sh 1
```

念：
> "Category five asks about something never mentioned, and the correct answer is 'not mentioned'.
> But the evaluation behind the paper's numbers scored those questions against
> `adversarial_answer` — the trap itself. So falling for the trap reads as a high score. Four
> hundred and forty-four of the four hundred and forty-six have no gold answer at all. Every run of
> mine reports both numbers: `--legacy-c5` for like-for-like comparison, and the strict one."

**【画面 2-B】（4:15）**
Word → 报告 **§4** 里那句加粗的 "The adversarial column is a measurement artefact"。
指 **25.76 → 74.86**。

念：
> "Same predictions, two labels. Scored the paper's way, adversarial F1 is 25.76. Scored the task's
> way, it is 74.86 — seventy-four percent of those answers correctly decline to answer. Anyone
> reading a leaderboard that puts adversarial F1 next to the other four is comparing
> similarity-to-a-wrong-answer with similarity-to-a-right-answer."

**【画面 2-C】（4:45）**
终端执行 `bash report/show_exhibit.sh 5`（显示 `--retrieve_k` 默认 10 那三行），
旁边用浏览器标签 A 切到论文 **Table 5** 对照 k=40/50。两个窗口并排，不要来回切。

念：
> "Second setting: retrieval depth. Table 5 of the paper lists k equals forty and fifty for this
> backbone. The driver that ships with the repository defaults to ten. I ran ten as the baseline and
> then added one trial at forty on the identical cached memories — so I could measure the gap
> instead of just declaring it."

**【画面 2-D】（5:10）**
终端执行（零成本，只读数据集）：

```bash
.venv/Scripts/python.exe -c "import json;d=json.load(open('data/locomo10.json',encoding='utf-8'));print('questions in released file:',sum(len(s['qa']) for s in d))"
```

念（指着输出的 `1986`）：
> "Third: the paper describes 7,512 QA pairs. The released file has 1,986. Table 1 was produced on
> something larger than what ships with the code — which alone makes an exact match impossible."

**【画面 2-E】（5:25）**
Word → 报告 **§2** 结尾一句（backbone substitution）。

念：
> "And the fourth variable is mine, not theirs: deepseek-chat instead of gpt-4o-mini. Prompts,
> temperatures and max tokens are byte-identical — the assignment's edge case A, a controlled swap,
> not a free choice."

---

## 5:30–8:30｜我们的数字 vs 论文

**【画面 3-A】（5:30）**
Word → 报告 **§4 主表**（Single-hop 44.00 ± 0.32 那张）。整表入镜，鼠标沿第一列往下走。

念：
> "Three trials, mean and standard deviation, same 199 questions. Overall 30.39 ± 1.25 against the
> paper's per-category numbers — the paper does not report an overall column, which is itself worth
> noticing, because the average hides the disagreement."

**【画面 3-B】（6:10）**
鼠标停在 **Single-hop** 和 **Temporal** 两行。

念：
> "Single-hop, 44.00 against 27.02 — seventeen points stronger. Temporal, 20.17 against 12.14 —
> eight points stronger. On questions answerable from one retrieved note, DeepSeek is simply the
> better reader. So the reproduction is not uniformly worse; it is differently shaped."

**【画面 3-C】（6:45）**
鼠标停在 **Open-domain** 行（10.25 vs 44.65）。

念：
> "Open-domain collapses: 10.25 against 44.65. DeepSeek refuses to volunteer world knowledge — it
> answers 'not mentioned in the conversation', and category three punishes exactly that. This is a
> backbone behaviour, not a memory failure."

**【画面 3-D】（7:15）**
鼠标停在 **Multi-hop** 行（27.39 ± 3.48 vs 45.85），并指一下那个 **± 3.48**。

念：
> "And multi-hop — the one category the paper's whole thesis rests on — 27.39 against 45.85. That is
> the number that did not transfer. Note also the standard deviation: 3.48, ten times the spread of
> single-hop. Something in this pipeline is nondeterministic in a way that matters, and I come back
> to it in five minutes."

**【画面 3-E】（7:55）**
切到 k=40 表（报告 §4 第二张表）。鼠标停在 **Overall 30.39 → 39.46** 和
**Adversarial 25.76 → 41.81** 两行。

念：
> "This is the most instructive comparison in the whole study, and it cost nineteen yuan. Raising k
> from ten to forty moves overall F1 from 30.39 to 39.46, and adversarial from a twenty-four-point
> deficit to almost matching the paper. So most of the headline gap was my setting, not the model —
> a single-k reproduction would have blamed the backbone for all of it."

**【画面 3-F】（8:20）**
鼠标停在 **Multi-hop +2.5** 和 **Open-domain +0.1**。

念：
> "But the two categories the thesis rests on barely move: multi-hop plus 2.5, open-domain plus 0.1.
> Retrieval depth explains the overall gap; it does not explain the mechanism-sensitive categories.
> That decomposition only exists because I ran the pass."

---

## 8:30–11:30｜改动：一个机制，被隔离出来

**【画面 4-A】（8:30）**
终端执行（零成本）：

```bash
git show 0334040 --stat && git show 0334040 -- memory_layer_robust.py | grep -n "no_evolution"
```

念：
> "One flag, one code path, one commit. The commit also changes cache handling — I'll come to why
> that is part of the change, not an afterthought."

**【画面 4-B】（9:00）**
终端执行（带行号，第 417 行就是全部改动）：

```bash
bash report/show_exhibit.sh 2
```

念：
> "This is it. With the flag on, a note keeps its LLM-extracted metadata — title, keywords, tags,
> summary — but it never gains links, never strengthens its tags, never rewrites the context of its
> neighbours. Retrieval, prompts, k, seeds and metrics are untouched. So the two arms differ in one
> mechanism only."

**【画面 4-C】（9:30）**
浏览器标签 A 切到论文 **Table 2**，圈 `w/o LG & ME` 行的 multi-hop 值 **24.55**，再圈 full 的 **45.85**。

念：
> "That mechanism is chosen because the paper already prices it. Table 2: removing link generation
> and memory evolution drops multi-hop F1 from 45.85 to 24.55 — a 21-point loss. My arm is exactly
> that row, re-run on a different backbone."

**【画面 4-D】（10:00）**
终端执行（`arm_tag` 那五行，第 241 行是关键）：

```bash
bash report/show_exhibit.sh 3
```

念：
> "And this is the trap I mentioned. The cache path encodes backend and model — not the memory
> configuration. Without an arm suffix, both arms share one cache directory, the ablation silently
> reloads the baseline's notes, and the experiment reports a difference of zero. A perfectly
> plausible null result produced by a directory name. I fixed it before the first run, which is why
> you are seeing an actual difference."

**【画面 4-E】（10:35）**
Word → 报告 **§5 消融表**。鼠标停在 **Overall** 行和 **Multi-hop** 行。

念：
> "Three trials per arm, same questions, same seeds, same prompts. Overall: 30.39 to 29.61 — a
> difference of 0.78 against a pooled standard error of 1.6, which is no overall effect. Multi-hop
> is the only category that moves the predicted way: 27.39 to 23.05, minus 4.33. The paper reports
> minus 21.3 for the same removal. The direction reproduces; the magnitude is a fifth."

**【画面 4-F】（11:05）**
鼠标停在 Temporal **+3.82** 和 Open-domain **+1.52** 两行。

念：
> "Temporal and open-domain move the wrong way — plus 3.8, plus 1.5 — which is what three-trial
> noise looks like. Welch's t is about 2.1; you would need eight to ten trials per arm to resolve a
> four-point effect at this variance. So I report an interval and a direction, not a point estimate.
> Calling this a refutation would be overclaiming in the other direction."

**【画面 4-G】（11:25）**
回到消融表的 **± 3.48** 与 **± 0.71** 两个数（Multi-hop 列的 Full 与 Without evolution）。

念：
> "One thing I did not predict: on multi-hop, the full arm's spread is 3.48 and without evolution it
> is 0.71. The mechanism rewrites neighbours in place, so a note's retrievability depends on what
> arrived after it — nondeterministic machinery feeding a deterministic metric."

---

## 11:30–13:30｜成本：这个方法真正贵在哪

**【画面 5-A】（11:30）**
Word → 报告 **§4 成本表**（`Phase | Calls | Input tokens | Est. cost | Wall clock`）。整表入镜。

念：
> "Every number here comes from intercepting each completion call, so it is measured, not projected.
> Building memory for one conversation takes 1,311 calls: 419 turns times one metadata call plus up
> to three evolution calls — about four calls per conversational turn, and 2 million input tokens.
> Answering all 199 questions takes 398 calls."

**【画面 5-B】（12:05）**
鼠标停在 **No-evolution: memory build | 419 | 0.34 M | $0.033 | 7 min** 行。

念：
> "Remove the mechanism and the write path drops from 1,311 calls to 419 and from thirty-eight cents
> to three cents — eleven times cheaper, four times faster. That is the price of roughly four points
> on one of five categories."

**【画面 5-C】（12:35）**
切到 **§4 的 the evolution step inflates the read path too** 那段（`10 retrieved notes drag their…`）。

念：
> "And the cost is not confined to writing. With links in place, the ten retrieved notes drag their
> neighbours into the prompt: 11,910 input tokens per question against 1,508 without evolution —
> eight times. So the mechanism taxes the read path too, which is not what the paper's framing
> suggests."

**【画面 5-D】（13:00）**
鼠标停在成本表最后一行 **Baseline at k=40 | 398 per trial | 9.60 M | $2.69 | 11.5 min**。

念：
> "The k=40 trial prices the setting as well: 9.6 million input tokens against 2.4, and two dollars
> sixty-nine against sixty-seven cents per trial. Retrieval depth is not free either."
>
> "Total spend for the whole study, read from the provider's balance endpoint rather than from my
> token estimate: fourteen point eight yuan, about two dollars, for roughly 6,300 calls — including
> one discarded build."

---

## 13:30–15:00｜给下一个人

**【画面 6-A】（13:30）**
Word → 报告 **§7 Conclusion**，先停在 "Advice to the next person" 的四条上，一条一条指。
说到第三条（BLEU 全零）时，可顺手切终端跑 `bash report/show_exhibit.sh 4` 展示那个
`except Exception` 和下面的告警——**如果时间紧就跳过，只用嘴讲**。

念：
> "Four things I would tell whoever does this next. One: write the target claim down before the
> first paid call — mine was fixed at Table 1, column gpt-4o-mini, and the ablation was chosen the
> same hour. Two: isolate the ablation cache before running anything; this is the failure that
> produces a clean, believable, completely fake null result. Three: print the metric edges next to
> the first result — a swallowed exception turned BLEU into a column of zeros that reads like a low
> score, not a bug. Four: report distributions, not points. The exactly-zero BLEU column is only
> visible because I looked at three trials."

**【画面 6-B】（14:15）**
切到 k=40 表，鼠标停在 Overall 与 Multi-hop/Open-domain 之间来回一次。

念：
> "And I'll close on the k=40 pass, because it is the single most instructive number here. Nine
> points of overall gap were my setting. Sixteen to thirty-four points on multi-hop and open-domain
> were not. A reproduction that measures only one setting cannot tell those two apart — and that
> distinction is the actual deliverable, more than any cell in the table."

**【画面 6-C】（14:40）**
浏览器标签 B：你的 GitHub 仓库首页，鼠标划过 commit 列表。

念：
> "Everything is in the repository: thirteen commits — pristine snapshot, backend swap, evaluation
> infrastructure, the ablation, each environment fix, and the docs — the preflight, the raw trial
> JSONs so every number can be recomputed without paying for a run, and no API key anywhere in the
> history. Thank you."

---

## 录制现场备忘

- **时长**：念白语速按 150 词/分钟设计。如果某段超时，最先砍 **画面 3-C**（open-domain 解释）和
  **画面 5-D**，它们不影响主线；绝对不要砍 **画面 4-D**（缓存陷阱）和 **画面 6-B**（k 分解）。
- **静态帧留白**：每切一次窗口，停 1 秒再开口，否则观众来不及看清。
- **口误**：数字说错了就地重说一遍，不要停下重录整段；评委更在意你是否知道自己说错了。
- **Zoom**：`Share Screen` → 选 **单窗口**而不是全屏（避免弹通知）→ `Record` → `Record on this
  Computer`。录完检查文件在 `~/Documents/Zoom/`。
- **上传**：OneDrive / Google Drive / YouTube 未列出。**必须把分享权限改成"任何有链接的人可查看"**，
  并在报告首页 `**Demo recording:** [link]` 处填上。
- **最后一步**：报告首页的 GitHub 地址与录屏链接填完后，重新导出一次 docx 再提交，否则老师点开
  看到的是 `[your-account]`。
