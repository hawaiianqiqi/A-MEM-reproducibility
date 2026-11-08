### Arm: `noevo`

- model: `deepseek-chat` via `deepseek` | k=10 | ratio=0.1 | no_evolution=True | legacy_c5=True
- trials: 3 (answer seeds [42, 43, 44])

| Split | F1 | BLEU-1 |
|---|---|---|
| Overall | 29.61 ± 2.55 | 25.51 ± 2.15 |
| Multi-hop | 23.05 ± 0.71 | 16.88 ± 0.83 |
| Temporal | 23.98 ± 3.92 | 17.61 ± 3.35 |
| Open-domain | 11.77 ± 4.26 | 11.34 ± 5.55 |
| Single-hop | 42.55 ± 4.43 | 37.49 ± 4.24 |
| Adversarial | 24.16 ± 0.91 | 23.68 ± 0.98 |
