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

### Cost and latency

| Arm | Trials | LLM calls | Tokens | Est. cost (USD) | Wall clock (min) |
|---|---|---|---|---|---|
| baseline | 3 | 1194 | 7.14M | 2.002 | 19.7 |
