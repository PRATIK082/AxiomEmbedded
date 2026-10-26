"""Parallel subagent execution tests."""
from packages.parallel import run_parallel, map_parallel


def test_run_parallel_returns_in_order():
    results = run_parallel([lambda: 1, lambda: 2, lambda: 3])
    assert results == [1, 2, 3]


def test_map_parallel():
    out = map_parallel(lambda x: x * 2, [1, 2, 3, 4])
    assert out == [2, 4, 6, 8]


def test_run_parallel_captures_exceptions():
    def boom():
        raise ValueError("boom")
    results = run_parallel([lambda: 1, boom])
    assert results[0] == 1
    assert results[1]["status"] == "error"