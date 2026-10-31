from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ConversationMessage:
    role: str
    content: str


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    description: str
    parameters: dict[str, Any]


@dataclass(frozen=True)
class ToolCall:
    call_id: str
    name: str
    arguments: dict[str, Any]


@dataclass(frozen=True)
class ToolDecision:
    response_id: str
    text: str
    tool_calls: list[ToolCall]


@dataclass(frozen=True)
class ToolResult:
    call_id: str
    output: Any


class LLMService(ABC):
    @abstractmethod
    def chat(
        self,
        message: str,
        history: list[ConversationMessage] | None = None,
    ) -> str:
        pass

    @property
    def supports_tools(self) -> bool:
        return False

    def decide_with_tools(
        self,
        message: str,
        tools: list[ToolDefinition],
        history: list[ConversationMessage] | None = None,
    ) -> ToolDecision:
        raise NotImplementedError(
            f"{type(self).__name__} does not support tool calling."
        )

    def complete_with_tool_results(
        self,
        decision: ToolDecision,
        results: list[ToolResult],
        tools: list[ToolDefinition],
    ) -> str:
        raise NotImplementedError(
            f"{type(self).__name__} does not support tool calling."
        )