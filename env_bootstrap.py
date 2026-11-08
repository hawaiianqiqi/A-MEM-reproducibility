"""Environment bootstrap: must be imported before anything that touches transformers.

Two things have to happen before the first heavy import, not after:

1. ``.env`` is loaded, so the backend and pricing assumptions are visible to every module.
2. Offline mode is forced. This machine cannot reach huggingface.co, and sentence-transformers
   resolves the model revision over the network at import time. That request fails and takes the
   process down with it, so the weights already in the local cache must be used without asking.
"""

import os

from dotenv import load_dotenv

load_dotenv()

# The weights are cached; asking the hub for them is both unnecessary and fatal here.
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
os.environ.setdefault("HF_ENDPOINT", os.getenv("HF_ENDPOINT", "https://hf-mirror.com"))
