### Arm: `baseline_k40`

- model: `deepseek-chat` via `deepseek` | k=40 | ratio=0.1 | no_evolution=False | legacy_c5=True
- trials: 1 (answer seeds [42])

| Split | F1 | BLEU-1 |
|---|---|---|
| Overall | 39.46 ± 0.00 | 34.62 ± 0.00 |
| Multi-hop | 29.90 ± 0.00 | 20.37 ± 0.00 |
| Temporal | 25.42 ± 0.00 | 18.51 ± 0.00 |
| Open-domain | 10.32 ± 0.00 | 10.43 ± 0.00 |
| Single-hop | 55.08 ± 0.00 | 49.54 ± 0.00 |
| Adversarial | 41.81 ± 0.00 | 41.46 ± 0.00 |
