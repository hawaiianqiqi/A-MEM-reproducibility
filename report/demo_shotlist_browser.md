# 录屏脚本（浏览器版 · 全程不碰终端、不需要网络）

目标片长 14–15 分钟。这份脚本与 `demo_shotlist.md` 的镜头编号一一对应，区别只有一点：
**所有原本需要终端的地方，改成点两个本地网页的导航条。** 代码、提交、日志、论文数字
都已经在页面里了，录屏时按 `Alt+Tab` 在四个窗口之间循环即可。

页面由脚本从仓库真实内容生成，不是手抄的：

```bash
python report/make_exhibits.py    # -> report/code_exhibits.html   （5 个代码展板）
python report/make_snapshot.py    # -> report/repo_snapshot.html   （提交历史、预检、证据文件）
```

---

## 开录前 5 分钟：四个窗口，全部在本地

按顺序打开，别在录屏时现场找文件。

| # | 窗口 | 怎么打开 | 用途 |
|---|---|---|---|
| A | 浏览器标签 A | 双击 `report/code_exhibits.html` | 5 个代码展板，顶部有导航条 |
| B | 浏览器标签 B | 双击 `report/repo_snapshot.html` | 提交历史、预检日志、论文对照表、证据文件 |
| C | Word / WPS | 双击 `report/FTEC5660_Reproducibility_Report.docx` | 报告里的四张表 |
| D | 文件管理器（可选） | 打开 `results/` | 只在画面 6-C 想展示原始 JSON 时用；不用的话窗口 B 的第 6 节已列出 |

两个页面顶部的导航条是 **sticky** 的（滚动时一直贴在窗口上方），点一下直接跳到对应小节：

- 窗口 A：`1 · category 5 scoring` / `2 · the one-line change` / `3 · the cache trap` /
  `4 · the swallowed exception` / `5 · retrieval depth`
- 窗口 B：`History` / `The ablation commit` / `What the release contains` / `Paper targets` /
  `Saved preflight` / `Evidence files` / `Hygiene`

**开录前必做**

1. 浏览器按 `Ctrl` + `+` 两下（约 125%），再按 `Ctrl+Shift+B` 收起书签栏，画面更干净。
2. 确认报告第 5 行仓库地址已是 `https://github.com/hawaiianqiqi/A-MEM-reproducibility`
   （已改好，不用动）；第 6 行 `**Demo recording:** [link]` 先留着，录完再填。
3. 关掉 Word 的临时锁文件所在目录里打开的旧窗口，确保录屏时 docx 是最新导出版。
4. **不要**在镜头里打开 `.env`、也不要打开任何含密钥的标签页。

**一条铁律：全程不现场调用付费 API。** 所有实验都以"读已保存的文件"的方式呈现，
重录一次不花一分钱。

---

## 0:00–1:30｜要复现什么，为什么是这个仓库

**【画面 0-A】（0:00）**
窗口 B → 点导航 `Paper targets` → 鼠标圈住第一张表 `TABLE 1, GPT-4O-MINI ROW` 的五行。

> "My target was fixed before the first paid call: the A-MEM column of Table 1 — the per-category
> F1 and BLEU-1 on LoCoMo, for the GPT-4o-mini backbone. One table row, not the whole paper."

**【画面 0-B】（0:30）**
窗口 B → 点导航 `History` → 滚到最底部，指第一条提交
`5dfe737 chore: pristine snapshot of WujiangXu/AgenticMemory (A-MEM LoCoMo harness)`。

> "Two repositories share almost the same name, and choosing wrong would have cost me two days.
> The library the paper advertises has no evaluation script — nothing in it can be checked against a
> reported number. The numbers live in the experiment repository, which ships the dataset, the
> harness and the prompts. That is the one I reproduce."

（这个仓库的根目录里就有 `data/locomo10.json`、`test_advanced_robust.py` 和全部 prompt 模板，
所以我把"实验仓库"这一层的证据压成一条提交记录，避免录屏时依赖网络去开 GitHub。）

**【画面 0-C】（1:05）**
窗口 C（Word）→ 第 1 节 **Scope** 那段，停在 "One of the ten released conversations …"。

> "Scope: one of ten conversations — 419 turns, 199 questions, all five categories — and three
> trials per arm. The assignment allows one benchmark; one conversation still gives me a
> distribution instead of a single point."

---

## 1:30–3:30｜环境：四个不报错的失败

**【画面 1-A】（1:30）**
窗口 C → **§6 Debug diary** 表格。鼠标依次停在 **第 5、7、9、10 行**（加粗那几条）的
"Symptom" 列上，逐条读。

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
窗口 B → 点导航 `Saved preflight` → 滚到最底部，先指 `build: 23s total, 2.9s/turn, 8 notes`，
再指最后一行 `calls=31 errors=0 in=22312 out=1096 cost=$0.0067`（这两行有黄色高亮）。

> "This is the preflight I wrote after those four failures. Eight turns of memory, then one question
> per category. It prints per-turn build latency, the retrieval context size, one answer per
> category, and the token and cost totals. Two and a half minutes, and it would have caught three of
> the four failures before any real money was spent."

**【画面 1-C】（3:10）**
同一区块，鼠标停在那行 `cat 5: … pred='Not mentioned in the conversation' | ref='self-care is
important' | F1=0.000`（也有黄色高亮）。

> "Keep your eye on this line — category five, prediction 'not mentioned', reference is the trap
> answer, F1 zero. That zero is the scam I'll explain in ninety seconds."

---

## 3:30–5:30｜三个改变数字的协议决策

**【画面 2-A】（3:30）**
窗口 A → 点导航 `1 · category 5 scoring`。鼠标停在第 33 行（高亮那行）
`return self.adversarial_answer if legacy_c5 else NOT_MENTIONED`。

> "Category five asks about something never mentioned, and the correct answer is 'not mentioned'.
> But the evaluation behind the paper's numbers scored those questions against
> `adversarial_answer` — the trap itself. So falling for the trap reads as a high score. Four
> hundred and forty-four of the four hundred and forty-six have no gold answer at all. Every run of
> mine reports both numbers: `--legacy-c5` for like-for-like comparison, and the strict one."

**【画面 2-B】（4:15）**
窗口 C → **§4** 里加粗那句 "The adversarial column is a measurement artefact"，指 **25.76 → 74.86**。

> "Same predictions, two labels. Scored the paper's way, adversarial F1 is 25.76. Scored the task's
> way, it is 74.86 — seventy-four percent of those answers correctly decline to answer. Anyone
> reading a leaderboard that puts adversarial F1 next to the other four is comparing
> similarity-to-a-wrong-answer with similarity-to-a-right-answer."

**【画面 2-C】（4:45）**
窗口 A → 点导航 `5 · retrieval depth`（第 419 行高亮，`default=10`）；
然后 `Alt+Tab` 到窗口 B → 点导航 `Paper targets` → 滚到第三张小表
`TABLE 5, RETRIEVAL DEPTH FOR THIS BACKBONE`（`10` vs `40, 50`）。两张表别来回切，说完再切。

> "Second setting: retrieval depth. Table 5 of the paper lists k equals forty and fifty for this
> backbone. The driver that ships with the repository defaults to ten. I ran ten as the baseline and
> then added one trial at forty on the identical cached memories — so I could measure the gap
> instead of just declaring it."

**【画面 2-D】（5:10）**
窗口 B → 点导航 `What the release contains` → 指第二行 `QA pairs in the released file 1,986`
和第三行 `QA pairs the paper describes 7,512`。

> "Third: the paper describes 7,512 QA pairs. The released file has 1,986. Table 1 was produced on
> something larger than what ships with the code — which alone makes an exact match impossible."

**【画面 2-E】（5:25）**
窗口 C → **§2** 结尾那句（backbone substitution）。

> "And the fourth variable is mine, not theirs: deepseek-chat instead of gpt-4o-mini. Prompts,
> temperatures and max tokens are byte-identical — the assignment's edge case A, a controlled swap,
> not a free choice."

---

## 5:30–8:30｜我们的数字 vs 论文

**【画面 3-A】（5:30）**
窗口 C → **§4 主表**（Single-hop 44.00 ± 0.32 那张）。整表入镜，鼠标沿第一列往下走。

> "Three trials, mean and standard deviation, same 199 questions. Overall 30.39 ± 1.25 against the
> paper's per-category numbers — the paper does not report an overall column, which is itself worth
> noticing, because the average hides the disagreement."

**【画面 3-B】（6:10）**
鼠标停在 **Single-hop** 和 **Temporal** 两行。

> "Single-hop, 44.00 against 27.02 — seventeen points stronger. Temporal, 20.17 against 12.14 —
> eight points stronger. On questions answerable from one retrieved note, DeepSeek is simply the
> better reader. So the reproduction is not uniformly worse; it is differently shaped."

**【画面 3-C】（6:45）**
鼠标停在 **Open-domain** 行（10.25 vs 44.65）。

> "Open-domain collapses: 10.25 against 44.65. DeepSeek refuses to volunteer world knowledge — it
> answers 'not mentioned in the conversation', and category three punishes exactly that. This is a
> backbone behaviour, not a memory failure."

**【画面 3-D】（7:15）**
鼠标停在 **Multi-hop** 行（27.39 ± 3.48 vs 45.85），并指一下那个 **± 3.48**。

> "And multi-hop — the one category the paper's whole thesis rests on — 27.39 against 45.85. That is
> the number that did not transfer. Note also the standard deviation: 3.48, ten times the spread of
> single-hop. Something in this pipeline is nondeterministic in a way that matters, and I come back
> to it in five minutes."

**【画面 3-E】（7:55）**
切到 k=40 表（**§4 第二张表**）。鼠标停在 **Overall 30.39 → 39.46** 和
**Adversarial 25.76 → 41.81** 两行。

> "This is the most instructive comparison in the whole study, and it cost nineteen yuan. Raising k
> from ten to forty moves overall F1 from 30.39 to 39.46, and adversarial from a twenty-four-point
> deficit to almost matching the paper. So most of the headline gap was my setting, not the model —
> a single-k reproduction would have blamed the backbone for all of it."

**【画面 3-F】（8:20）**
鼠标停在 **Multi-hop +2.5** 和 **Open-domain +0.1**。

> "But the two categories the thesis rests on barely move: multi-hop plus 2.5, open-domain plus 0.1.
> Retrieval depth explains the overall gap; it does not explain the mechanism-sensitive categories.
> That decomposition only exists because I ran the pass."

---

## 8:30–11:30｜改动：一个机制，被隔离出来

**【画面 4-A】（8:30）**
窗口 B → 点导航 `History` → 指高亮的 `0334040 exp(ablation): --no-evolution switch, isolated
cache per arm`；接着点导航 `The ablation commit`，让 diffstat 整块入镜
（`5 files changed, 60 insertions(+), 12 deletions(-)`，两行黄色高亮是记忆层和评测试验器）。

> "One flag, one code path, one commit. The commit also changes cache handling — I'll come to why
> that is part of the change, not an afterthought."

**【画面 4-B】（9:00）**
窗口 A → 点导航 `2 · the one-line change`。指第 417 行（高亮）：
`evo_label, note = (False, note) if self.no_evolution else self.process_memory(note)`。

> "This is it. With the flag on, a note keeps its LLM-extracted metadata — title, keywords, tags,
> summary — but it never gains links, never strengthens its tags, never rewrites the context of its
> neighbours. Retrieval, prompts, k, seeds and metrics are untouched. So the two arms differ in one
> mechanism only."

**【画面 4-C】（9:30）**
窗口 B → 点导航 `Paper targets` → 第二张表 `TABLE 2, MULTI-HOP ONLY`，先指 `full model 45.85`，
再指高亮的 `w/o link generation & memory evolution 24.55`。

> "That mechanism is chosen because the paper already prices it. Table 2: removing link generation
> and memory evolution drops multi-hop F1 from 45.85 to 24.55 — a 21-point loss. My arm is exactly
> that row, re-run on a different backbone."

**【画面 4-D】（10:00）**
窗口 A → 点导航 `3 · the cache trap`。指第 241 行（高亮）：
`arm_tag = "_noevo" if no_evolution else ""`，再指第 244–245 行的目录名拼接。

> "And this is the trap I mentioned. The cache path encodes backend and model — not the memory
> configuration. Without an arm suffix, both arms share one cache directory, the ablation silently
> reloads the baseline's notes, and the experiment reports a difference of zero. A perfectly
> plausible null result produced by a directory name. I fixed it before the first run, which is why
> you are seeing an actual difference."

**【画面 4-E】（10:35）**
窗口 C → **§5 消融表**。鼠标停在 **Overall** 行和 **Multi-hop** 行。

> "Three trials per arm, same questions, same seeds, same prompts. Overall: 30.39 to 29.61 — a
> difference of 0.78 against a pooled standard error of 1.6, which is no overall effect. Multi-hop
> is the only category that moves the predicted way: 27.39 to 23.05, minus 4.33. The paper reports
> minus 21.3 for the same removal. The direction reproduces; the magnitude is a fifth."

**【画面 4-F】（11:05）**
鼠标停在 Temporal **+3.82** 和 Open-domain **+1.52** 两行。

> "Temporal and open-domain move the wrong way — plus 3.8, plus 1.5 — which is what three-trial
> noise looks like. Welch's t is about 2.1; you would need eight to ten trials per arm to resolve a
> four-point effect at this variance. So I report an interval and a direction, not a point estimate.
> Calling this a refutation would be overclaiming in the other direction."

**【画面 4-G】（11:25）**
回到消融表的 **± 3.48** 与 **± 0.71** 两个数（Multi-hop 列的 Full 与 Without evolution）。

> "One thing I did not predict: on multi-hop, the full arm's spread is 3.48 and without evolution it
> is 0.71. The mechanism rewrites neighbours in place, so a note's retrievability depends on what
> arrived after it — nondeterministic machinery feeding a deterministic metric."

---

## 11:30–13:30｜成本：这个方法真正贵在哪

**【画面 5-A】（11:30）**
窗口 C → **§4 成本表**（`Phase | Calls | Input tokens | Est. cost | Wall clock`）。整表入镜。

> "Every number here comes from intercepting each completion call, so it is measured, not projected.
> Building memory for one conversation takes 1,311 calls: 419 turns times one metadata call plus up
> to three evolution calls — about four calls per conversational turn, and 2 million input tokens.
> Answering all 199 questions takes 398 calls."

**【画面 5-B】（12:05）**
鼠标停在 **No-evolution: memory build | 419 | 0.34 M | $0.033 | 7 min** 行。

> "Remove the mechanism and the write path drops from 1,311 calls to 419 and from thirty-eight cents
> to three cents — eleven times cheaper, four times faster. That is the price of roughly four points
> on one of five categories."

**【画面 5-C】（12:35）**
切到 **§4 的 "the evolution step inflates the read path too"** 那段（`10 retrieved notes drag
their…`）。

> "And the cost is not confined to writing. With links in place, the ten retrieved notes drag their
> neighbours into the prompt: 11,910 input tokens per question against 1,508 without evolution —
> eight times. So the mechanism taxes the read path too, which is not what the paper's framing
> suggests."

**【画面 5-D】（13:00）**
鼠标停在成本表最后一行 **Baseline at k=40 | 398 per trial | 9.60 M | $2.69 | 11.5 min**。

> "The k=40 trial prices the setting as well: 9.6 million input tokens against 2.4, and two dollars
> sixty-nine against sixty-seven cents per trial. Retrieval depth is not free either."
>
> "Total spend for the whole study, read from the provider's balance endpoint rather than from my
> token estimate: fourteen point eight yuan, about two dollars, for roughly 6,300 calls — including
> one discarded build."

---

## 13:30–15:00｜给下一个人

**【画面 6-A】（13:30）**
窗口 C → **§7 Conclusion**，先停在 "Advice to the next person" 的四条上，一条一条指。
说到第三条（BLEU 全零）时，可顺手 `Alt+Tab` 到窗口 A → 点导航 `4 · the swallowed exception`
展示第 86–96 行那段 `except Exception` 和下面的告警——**时间紧就跳过，只用嘴讲**。

> "Four things I would tell whoever does this next. One: write the target claim down before the
> first paid call — mine was fixed at Table 1, column gpt-4o-mini, and the ablation was chosen the
> same hour. Two: isolate the ablation cache before running anything; this is the failure that
> produces a clean, believable, completely fake null result. Three: print the metric edges next to
> the first result — a swallowed exception turned BLEU into a column of zeros that reads like a low
> score, not a bug. Four: report distributions, not points. The exactly-zero BLEU column is only
> visible because I looked at three trials."

**【画面 6-B】（14:15）**
窗口 C → 切回 k=40 表，鼠标停在 Overall 与 Multi-hop / Open-domain 之间来回一次。

> "And I'll close on the k=40 pass, because it is the single most instructive number here. Nine
> points of overall gap were my setting. Sixteen to thirty-four points on multi-hop and open-domain
> were not. A reproduction that measures only one setting cannot tell those two apart — and that
> distinction is the actual deliverable, more than any cell in the table."

**【画面 6-C】（14:40）**
窗口 B → 点导航 `History`，鼠标从上往下划过提交列表；再点 `Evidence files`
（7 份 trial JSON、3 组 summary（json+md）、1 份 `report_tables.md`，共 14 个文件）。

> "Everything is in the repository: the pristine snapshot, backend swap, evaluation infrastructure,
> the ablation, each environment fix, and the docs — the preflight, the raw trial JSONs so every
> number can be recomputed without paying for a run, and no API key anywhere in the history.
> Thank you."

（如果此刻网络正常，可以再切到 GitHub 仓库首页补一个镜头；网络不好就跳过，
窗口 B 的 `Hygiene` 一节已经写明 `.env` 从未进入历史。）

---

## 录制现场备忘

- **时长**：念白语速按 150 词/分钟设计。超时就先砍 **画面 3-C**（open-domain 解释）和
  **画面 5-D**，它们不影响主线；绝对不要砍 **画面 4-D**（缓存陷阱）和 **画面 6-B**（k 分解）。
- **静态帧留白**：每切一次窗口停 1 秒再开口，否则观众来不及看清。
- **口误**：数字说错了就地重说一遍，不要停下重录整段；评委更在意你是否知道自己说错了。
- **Zoom**：`Share Screen` → 选**单窗口**（不是全屏，避免弹通知）→ `Record` →
  `Record on this Computer`。录完文件在 `~/Documents/Zoom/`。
- **窗口共享顺序**：Zoom 共享的是单窗口，所以每换一个窗口都要重新点一次 `Share`；
  建议先在 Zoom 里把 A、B、C 三个窗口都加入共享白板（`Share Screen` 面板里多选），
  录制中就能用 `Alt+Tab` 直接切换，不用反复点共享。
- **上传**：OneDrive / Google Drive / YouTube 都行，**分享权限必须改成"任何有链接的人可查看"**，
  然后把链接填进报告第 6 行 `**Demo recording:** [link]`，重导出 docx 再提交。
