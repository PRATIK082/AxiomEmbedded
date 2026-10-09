# SPDX-License-Identifier: Apache-2.0
"""Phase 3: research pipeline (planner, local backend, verifier, synthesizer)."""

import json
import subprocess
import sys

from packages import research


def test_plan_splits_and_caps():
    subs = research.plan("Compare OpenCode vs Claude Code; which fits embedded?", 2)
    assert 1 <= len(subs) <= 2
    assert research.plan("", 3) == []
    assert len(research.plan("safety standards for automotive mcu", 2)) == 2


def test_local_backend_finds_cited_skill_refs():
    result = research.search_local("ISO 26262 automotive safety mcu")
    assert result["status"] == "ok"
    refs = [f for f in result["findings"] if f.get("number") == "ISO 26262"]
    assert refs, "safety skill manifest carries ISO 26262 refs"
    assert all(f["source_url"] for f in refs)
    assert all(f["confidence"] == "high" for f in refs)
    assert all(f["paraphrase"] for f in result["findings"])


def test_local_backend_no_match_is_honest():
    result = research.search_local("zzzqqq nonexistent topic xyzzy")
    assert result["status"] == "ok"
    assert result["findings"] == []


def test_web_backends_unavailable_without_keys(monkeypatch):
    for backend, var in (("tavily", "TAVILY_API_KEY"), ("brave", "BRAVE_API_KEY"),
                         ("searxng", "SEARXNG_URL")):
        monkeypatch.delenv(var, raising=False)
        result = research.search_web("anything", backend)
        assert result["status"] == "unavailable"
        assert var in result["reason"]
        assert result["findings"] == []


def test_verify_drops_uncited_and_duplicates():
    cited = {"claim": "ISO 26262 2018", "source_url": "https://example.com",
             "confidence": "high"}
    uncited = {"claim": "trust me", "confidence": "low"}
    accepted, rejected = research.verify([cited, dict(cited), uncited])
    assert accepted == [cited]
    assert {r["reject_reason"] for r in rejected} == {"duplicate", "uncited claim (no source)"}


def test_synthesize_has_safety_notice_and_rejected():
    report = research.synthesize("q", [], [], [])
    assert research.SAFETY_NOTICE in report
    assert "No cited findings" in report


def test_run_local_end_to_end():
    envelope = research.run("ISO 26262 automotive safety", backend="local")
    assert envelope["status"] == "ok"
    assert envelope["findings"], "local backend should cite the safety skill"
    assert research.SAFETY_NOTICE in envelope["report"]
    assert envelope["backend"] == "local"


def test_run_report_stays_compact():
    envelope = research.run("ISO 26262 automotive safety", backend="local")
    assert len(envelope["report"]) < 20000
    assert not envelope["rejected"], "overlapping sub-questions must not spam rejects"


def test_run_empty_question_errors():
    assert research.run("", backend="local")["status"] == "error"


def test_run_unknown_backend_raises():
    try:
        research.run("q", backend="nope")
    except ValueError:
        pass
    else:  # pragma: no cover
        raise AssertionError("expected ValueError")


def test_run_auto_falls_back_to_local_without_binary(monkeypatch):
    monkeypatch.setattr("packages.launcher.find_opencode", lambda: None)
    envelope = research.run("ISO 26262 automotive safety", backend="auto")
    assert envelope["status"] == "ok"
    assert envelope["findings"]
    assert any("opencode unavailable" in str(m.get("note", ""))
               for m in envelope["methods"])
