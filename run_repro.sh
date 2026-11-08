#!/usr/bin/env bash
# End-to-end reproduction driver for the A-MEM / LoCoMo assignment.
#
# Phases are ordered cheapest-first so a failure never wastes a finished memory build:
#   1. smoke   — 1 conversation, 1 trial: proves the whole chain works before paying for more
#   2. baseline— paper arm (3 trials), memories built once and cached
#
# Usage:
#   cp .env.example .env   # then put the key in .env
#   bash run_repro.sh smoke
#   bash run_repro.sh baseline
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

case "${1:-all}" in
  smoke)    phase_smoke ;;
  baseline) phase_baseline ;;
  all)      phase_smoke; phase_baseline ;;
  *) echo "usage: bash run_repro.sh [smoke|baseline|all]" >&2; exit 2 ;;
esac
