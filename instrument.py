"""Token / latency / cost accounting for the reproduction runs.

The upstream harness discards ``response.usage``, so a run cannot say what it cost.
This module patches ``litellm.completion`` (which the DeepSeek controller binds at
construction time) and accumulates per-call statistics. Prices are read from the
environment so the report can state the exact assumption used.

    PRICE_IN_PER_MTOK   USD per 1M prompt tokens      (default 0.28)
    PRICE_OUT_PER_MTOK  USD per 1M completion tokens  (default 0.42)
"""

import threading
import time
import os

_lock = threading.Lock()
_STATE = {
    "calls": 0,
    "errors": 0,
    "prompt_tokens": 0,
    "completion_tokens": 0,
    "latency_s": [],
}
_INSTALLED = False


def reset():
    with _lock:
        _STATE.update(calls=0, errors=0, prompt_tokens=0, completion_tokens=0, latency_s=[])


def install():
    """Patch litellm.completion once, before any controller is constructed."""
    global _INSTALLED
    if _INSTALLED:
        return
    import litellm

    original = litellm.completion

    def counted(*args, **kwargs):
        start = time.perf_counter()
        try:
            response = original(*args, **kwargs)
        except Exception:
            with _lock:
                _STATE["calls"] += 1
                _STATE["errors"] += 1
            raise
        elapsed = time.perf_counter() - start
        usage = getattr(response, "usage", None)
        with _lock:
            _STATE["calls"] += 1
            _STATE["latency_s"].append(elapsed)
            if usage is not None:
                _STATE["prompt_tokens"] += getattr(usage, "prompt_tokens", 0) or 0
                _STATE["completion_tokens"] += getattr(usage, "completion_tokens", 0) or 0
        return response

    litellm.completion = counted
    _INSTALLED = True


def snapshot():
    """Return the accumulated statistics as a plain dict, with derived cost."""
    with _lock:
        calls = _STATE["calls"]
        latencies = list(_STATE["latency_s"])
        prompt_tokens = _STATE["prompt_tokens"]
        completion_tokens = _STATE["completion_tokens"]
        errors = _STATE["errors"]

    price_in = float(os.getenv("PRICE_IN_PER_MTOK", "0.28"))
    price_out = float(os.getenv("PRICE_OUT_PER_MTOK", "0.42"))
    cost = prompt_tokens / 1e6 * price_in + completion_tokens / 1e6 * price_out

    return {
        "llm_calls": calls,
        "llm_errors": errors,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": prompt_tokens + completion_tokens,
        "mean_latency_s": (sum(latencies) / len(latencies)) if latencies else 0.0,
        "total_llm_time_s": sum(latencies),
        "est_cost_usd": cost,
        "price_assumption": {"in_per_mtok": price_in, "out_per_mtok": price_out},
    }
