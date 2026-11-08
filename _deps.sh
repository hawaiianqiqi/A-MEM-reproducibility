#!/usr/bin/env bash
cd "$(dirname "$0")"
PY=".venv/Scripts/python.exe"
M="https://mirrors.aliyun.com/pypi/simple"
for p in requests python-dotenv rank-bm25 rouge-score scikit-learn litellm transformers bert-score sentence-transformers torch; do
  ok=0
  for attempt in 1 2 3 4; do
    echo "--- $p attempt $attempt ---"
    if timeout 900 $PY -m pip install --no-cache-dir --retries 5 --timeout 90 -i "$M" "$p" >> deps.log 2>&1; then
      echo "OK $p"; ok=1; break
    fi
    sleep 3
  done
  [ $ok -eq 0 ] && echo "GAVE_UP $p"
done
echo "ALL_DONE"
