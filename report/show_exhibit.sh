#!/usr/bin/env bash
# Terminal code exhibits for the demo recording — no editor needed.
#
#   bash report/show_exhibit.sh          # list the exhibits
#   bash report/show_exhibit.sh 3        # print exhibit 3, with line numbers
#
# Each exhibit prints a file path banner, then the snippet with real line numbers,
# so the viewer can follow "line 417" without an editor window.

cd "$(dirname "$0")/.." || exit 1

show() {  # show <label> <file> <start> <end>
  local label="$1" file="$2" start="$3" end="$4"
  printf '\n'
  printf '  %s\n' "$label"
  printf '  %s  (lines %s-%s)\n' "$file" "$start" "$end"
  printf '  %s\n\n' "$(printf '%*s' 66 '' | tr ' ' '-')"
  awk -v s="$start" -v e="$end" 'NR>=s && NR<=e {printf "%5d | %s\n", NR, $0}' "$file"
  printf '\n'
}

case "${1:-list}" in
  1)
    show "EXHIBIT 1 - category 5 is scored against the trap answer" \
         "load_dataset.py" 27 34
    ;;
  2)
    show "EXHIBIT 2 - the whole modification is this one line" \
         "memory_layer_robust.py" 414 419
    ;;
  3)
    show "EXHIBIT 3 - the ablation cache trap (would have faked a null result)" \
         "test_advanced_robust.py" 239 247
    ;;
  4)
    show "EXHIBIT 4 - swallowed exception: BLEU-1 was silently 0.0 for every question" \
         "utils.py" 84 96
    ;;
  5)
    show "EXHIBIT 5 - retrieval depth: the driver defaults to k=10, paper Table 5 says 40/50" \
         "test_advanced_robust.py" 419 421
    ;;
  list)
    cat <<'EOF'

  Terminal code exhibits — run: bash report/show_exhibit.sh <n>

    1   load_dataset.py:27-34          category-5 reference (the trap answer)
    2   memory_layer_robust.py:414-419 the --no-evolution one-liner (the modification)
    3   test_advanced_robust.py:239-247 the cache-directory trap
    4   utils.py:84-96                 the swallowed BLEU exception
    5   test_advanced_robust.py:419-421  k default = 10

EOF
    ;;
  *)
    echo "unknown exhibit: $1" >&2; exit 2 ;;
esac
