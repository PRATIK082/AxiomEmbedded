"""Parallel subagent execution (B8): run independent callables concurrently."""
from __future__ import annotations

import concurrent.futures
from typing import Callable, Iterable


def run_parallel(tasks: Iterable[Callable], max_workers: int = 4) -> list:
    """Run callables in parallel; returns list of results (or exceptions)."""
    tasks = list(tasks)
    results = [None] * len(tasks)
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as ex:
        future_to_idx = {ex.submit(t): i for i, t in enumerate(tasks)}
        for fut in concurrent.futures.as_completed(future_to_idx):
            idx = future_to_idx[fut]
            try:
                results[idx] = fut.result()
            except Exception as exc:  # noqa: BLE001
                results[idx] = {"status": "error", "error": str(exc)}
    return results


def map_parallel(fn, items, max_workers: int = 4) -> list:
    """Apply fn to each item in parallel."""
    return run_parallel([lambda x=item: fn(x) for item in items], max_workers=max_workers)
