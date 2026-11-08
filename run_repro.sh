#!/usr/bin/env bash
# End-to-end reproduction driver for the A-MEM / LoCoMo assignment.
#
# Phases are ordered cheapest-first so a failure never wastes a finished memory build:
#   1. smoke   — 1 conversation, 1 trial: proves the whole chain works before paying for more
#   2. baseline— paper arm (3 trials), memories built once and cached
#   3. noevo   — MODIFICATION arm: identical except the evolution step is skipped
#
# Usage:
#   cp .env.example .env   # then put the key in .env
#   bash run_repro.sh smoke
#   bash run_repro.sh baseline
#   bash run_repro.sh noevo
#   bash run_repro.sh all
set -euo pipefail

cd "$(dirname "$0")"

PY=".venv/Scripts/python.exe"
[ -x "$PY" ] || PY=".venv/bin/python"

# The harness loads no .env itself, so export it here.
if [ -f .env ]; then
  set -a
  # shellcheck disable=SC1091
  . ./.env
  set +a
fi

if [ -z "${DEEPSEEK_API_KEY:-}" ]; then
  echo "ERROR: DEEPSEEK_API_KEY is empty. Put it in .env (never commit it)." >&2
  exit 1
fi

COMMON="--model deepseek-chat --backend deepseek --ratio 0.1 --retrieve-k 10 --legacy-c5"

phase_smoke() {
  echo "=== Phase 1: smoke test (1 conversation, 1 trial) ==="
  $PY repro_runner.py --tag smoke --trials 1 $COMMON
}

phase_baseline() {
  echo "=== Phase 2: baseline arm, 3 trials ==="
  $PY repro_runner.py --tag baseline --trials 3 $COMMON
}

phase_noevo() {
  echo "=== Phase 3: ablation arm (no evolution), 3 trials ==="
  $PY repro_runner.py --tag noevo --trials 3 $COMMON --no-evolution
}

phase_k40() {
  # Sensitivity check: Table 5 lists k=40/50 for the GPT-4o-mini backbone, Table 1 was produced
  # with it, and the harness ships k=10. Reuses the memory caches, so only answering is re-run.
  echo "=== Phase 4: k=40 sensitivity, both arms, 1 trial each ==="
  $PY repro_runner.py --tag baseline_k40 --trials 1 --model deepseek-chat --backend deepseek \
      --ratio 0.1 --retrieve-k 40 --legacy-c5
  $PY repro_runner.py --tag noevo_k40 --trials 1 --model deepseek-chat --backend deepseek \
      --ratio 0.1 --retrieve-k 40 --legacy-c5 --no-evolution
}

case "${1:-all}" in
  smoke)    phase_smoke ;;
  baseline) phase_baseline ;;
  noevo)    phase_noevo ;;
  k40)      phase_k40 ;;
  all)      phase_smoke; phase_baseline; phase_noevo; phase_k40 ;;
  *) echo "usage: bash run_repro.sh [smoke|baseline|noevo|k40|all]" >&2; exit 2 ;;
esac
