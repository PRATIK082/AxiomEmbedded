from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol

@dataclass(frozen=True)
class GenerationRequest:
    system: str
    user: str
    model: str | None = None

class LLMProvider(Protocol):
    def generate(self, request: GenerationRequest) -> str: ...

class UnconfiguredProvider:
    """Safe default: makes provider absence explicit instead of silently using a vendor."""
    def generate(self, request: GenerationRequest) -> str:
        raise RuntimeError("No LLM provider configured. Use an explicit provider adapter.")
