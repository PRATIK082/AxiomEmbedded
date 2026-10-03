from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Any

@dataclass(frozen=True)
class AgentTask:
    id: str
    agent: str
    request: str

class AgentRuntime:
    def __init__(self) -> None:
        self.handlers: dict[str, Callable[[AgentTask], Any]] = {}

    def register(self, agent: str, handler: Callable[[AgentTask], Any]) -> None:
        self.handlers[agent] = handler

    def execute(self, task: AgentTask) -> Any:
        if task.agent not in self.handlers:
            raise KeyError(f"agent not registered: {task.agent}")
        return self.handlers[task.agent](task)
