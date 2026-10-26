"""CI/CD pipeline template generation (GitHub Actions, GitLab CI)."""
from __future__ import annotations

from pathlib import Path


GITHUB_ACTIONS = """name: axiom-ci
on: [push, pull_request]
jobs:
  build-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: python -m pip install -e ".[test]"
      - run: python -m compileall -q axiom_cli packages scripts
      - run: python -m pytest -q
      - run: python -m axiom_cli doctor --skip-tests
      - run: python scripts/skill_pipeline.py --check
      - run: python -m axiom_cli security scan .
"""


GITLAB_CI = """stages: [build, test]
build:
  stage: build
  image: python:3.11
  script:
    - pip install -e ".[test]"
    - python -m compileall -q axiom_cli packages scripts
test:
  stage: test
  image: python:3.11
  script:
    - python -m pytest -q
    - python -m axiom_cli doctor --skip-tests
"""


def generate_cicd(kind: str, output: str | Path) -> Path:
    kind = (kind or "").lower()
    if kind in ("github", "gh", "github-actions"):
        content = GITHUB_ACTIONS
        path = Path(output) / ".github" / "workflows" / "axiom-ci.yml"
    elif kind in ("gitlab", "gitlab-ci"):
        content = GITLAB_CI
        path = Path(output) / ".gitlab-ci.yml"
    else:
        raise ValueError(f"unknown cicd kind: {kind}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path
