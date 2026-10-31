import asyncio
from typing import TypedDict

from langgraph.graph import (
    StateGraph,
    START,
    END,
)

from app.models.order_draft import PendingOrderDraft
from app.services.llm_factory import create_llm_service
from app.services.llm_service import (
    ConversationMessage,
    ToolDecision,
    ToolResult,
)
from app.tools.definitions import (
    BASE_OMS_TOOLS,
    CONFIRM_ORDER_TOOL,
)
from app.tools.executor import execute_tool


class AgentState(TypedDict):
    message: str
    history: list[ConversationMessage]
    access_token: str
    response: str

    pending_order: PendingOrderDraft | None

    tool_decision: ToolDecision | None
    tool_results: list[ToolResult]

    sources: list[str]


llm_service = create_llm_service()


def get_available_tools(
    state: AgentState,
):
    tools = list(BASE_OMS_TOOLS)

    if state["pending_order"] is not None:
        tools.append(CONFIRM_ORDER_TOOL)

    return tools


async def assistant_node(
    state: AgentState,
) -> AgentState:
    if not llm_service.supports_tools:
        response = await asyncio.to_thread(
            llm_service.chat,
            state["message"],
            state["history"],
        )

        return {
            **state,
            "response": response,
        }

    tools = get_available_tools(state)

    decision = await asyncio.to_thread(
        llm_service.decide_with_tools,
        state["message"],
        tools,
        state["history"],
    )

    return {
        **state,
        "tool_decision": decision,
        "response": decision.text,
    }


def route_after_assistant(
    state: AgentState,
) -> str:
    decision = state["tool_decision"]

    if decision and decision.tool_calls:
        return "tools"

    return END


async def tools_node(
    state: AgentState,
) -> AgentState:
    decision = state["tool_decision"]

    if decision is None:
        return state

    tools = get_available_tools(state)

    results: list[ToolResult] = []

    pending_order = state["pending_order"]

    sources = list(
        state.get(
            "sources",
            [],
        )
    )

    for tool_call in decision.tool_calls:
        result = await execute_tool(
            tool_call=tool_call,
            access_token=state["access_token"],
            pending_order=pending_order,
        )

        results.append(result)

        output = result.output

        if not isinstance(output, dict):
            continue

        if (
            output.get("action")
            == "order_draft_prepared"
            and output.get("pending_order")
        ):
            pending_order = (
                PendingOrderDraft.model_validate(
                    output["pending_order"]
                )
            )

        if output.get("action") == "order_created":
            pending_order = None

        tool_sources = output.get("sources")

        if isinstance(tool_sources, list):
            for source in tool_sources:
                if (
                    isinstance(source, str)
                    and source not in sources
                ):
                    sources.append(source)

    response = await asyncio.to_thread(
        llm_service.complete_with_tool_results,
        decision,
        results,
        tools,
    )

    return {
        **state,
        "pending_order": pending_order,
        "tool_results": results,
        "response": response,
        "sources": sources,
    }


builder = StateGraph(AgentState)

builder.add_node(
    "assistant",
    assistant_node,
)

builder.add_node(
    "tools",
    tools_node,
)

builder.add_edge(
    START,
    "assistant",
)

builder.add_conditional_edges(
    "assistant",
    route_after_assistant,
    {
        "tools": "tools",
        END: END,
    },
)

builder.add_edge(
    "tools",
    END,
)

graph = builder.compile()