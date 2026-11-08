### Arm: `baseline`

- model: `deepseek-chat` via `deepseek` | k=10 | ratio=0.1 | no_evolution=False | legacy_c5=True
- trials: 3 (answer seeds [42, 43, 44])

| Split | F1 | BLEU-1 |
|---|---|---|
| Overall | 30.39 ± 1.25 | 25.52 ± 1.65 |
| Multi-hop | 27.39 ± 3.48 | 18.52 ± 2.53 |
| Temporal | 20.17 ± 1.07 | 12.86 ± 0.56 |
| Open-domain | 10.25 ± 0.64 | 7.26 ± 2.28 |
| Single-hop | 44.00 ± 0.32 | 38.93 ± 0.51 |
| Adversarial | 25.76 ± 5.47 | 25.33 ± 5.40 |
