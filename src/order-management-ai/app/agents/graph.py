from typing import TypedDict
from langgraph.graph import StateGraph, START, END

from app.services.llm_factory import create_llm_service


class AgentState(TypedDict):
    message: str
    response: str


llm_service = create_llm_service()


def assistant_node(state: AgentState) -> AgentState:
    response = llm_service.chat(state["message"])

    return {
        "message": state["message"],
        "response": response,
    }


builder = StateGraph(AgentState)

builder.add_node("assistant", assistant_node)

builder.add_edge(START, "assistant")
builder.add_edge("assistant", END)

graph = builder.compile()