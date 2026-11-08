### Arm `baseline`

model `deepseek-chat` / backend `deepseek` / k=10 / ratio=0.1 / legacy_c5=True / trials=3 (seeds [42, 43, 44])

| Category | F1 (ours) | BLEU-1 (ours) | F1 (paper) | Δ F1 |
|---|---|---|---|---|
| Single-hop | 44.00 ± 0.32 | 38.93 ± 0.51 | 27.02 | +16.98 |
| Multi-hop | 27.39 ± 3.48 | 18.52 ± 2.53 | 45.85 | -18.46 |
| Temporal | 20.17 ± 1.07 | 12.86 ± 0.56 | 12.14 | +8.03 |
| Open-domain | 10.25 ± 0.64 | 7.26 ± 2.28 | 44.65 | -34.40 |
| Adversarial | 25.76 ± 5.47 | 25.33 ± 5.40 | 50.03 | -24.27 |

Category 5 re-scored strictly (prediction vs "Not mentioned in the conversation"): F1 = 74.86 over 141 questions, 74% of answers declined. The scored run used legacy_c5=True.

### Arm `noevo`

model `deepseek-chat` / backend `deepseek` / k=10 / ratio=0.1 / legacy_c5=True / trials=3 (seeds [42, 43, 44])

| Category | F1 (ours) | BLEU-1 (ours) | F1 (paper) | Δ F1 |
|---|---|---|---|---|
| Single-hop | 42.55 ± 4.43 | 37.49 ± 4.24 | 27.02 | +15.53 |
| Multi-hop | 23.05 ± 0.71 | 16.88 ± 0.83 | 45.85 | -22.80 |
| Temporal | 23.98 ± 3.92 | 17.61 ± 3.35 | 12.14 | +11.84 |
| Open-domain | 11.77 ± 4.26 | 11.34 ± 5.55 | 44.65 | -32.88 |
| Adversarial | 24.16 ± 0.91 | 23.68 ± 0.98 | 50.03 | -25.87 |

Category 5 re-scored strictly (prediction vs "Not mentioned in the conversation"): F1 = 78.59 over 141 questions, 77% of answers declined. The scored run used legacy_c5=True.

### Ablation: full A-MEM vs no evolution

| Category | Full F1 | No-evolution F1 | Δ | Paper full | Paper w/o LG & ME |
|---|---|---|---|---|---|
| Single-hop | 44.00 ± 0.32 | 42.55 ± 4.43 | -1.45 | 27.02 | — |
| Multi-hop | 27.39 ± 3.48 | 23.05 ± 0.71 | -4.33 | 45.85 | 24.55 |
| Temporal | 20.17 ± 1.07 | 23.98 ± 3.92 | +3.82 | 12.14 | — |
| Open-domain | 10.25 ± 0.64 | 11.77 ± 4.26 | +1.52 | 44.65 | — |
| Adversarial | 25.76 ± 5.47 | 24.16 ± 0.91 | -1.60 | 50.03 | — |

### Cost and latency

| Arm | Trials | LLM calls | Tokens | Est. cost (USD) | Wall clock (min) |
|---|---|---|---|---|---|
| baseline | 3 | 1194 | 7.14M | 2.002 | 19.7 |
| noevo | 3 | 1613 | 1.00M | 0.286 | 26.0 |
