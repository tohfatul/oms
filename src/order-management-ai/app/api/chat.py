from fastapi import APIRouter

from app.agents.graph import graph
from app.models.chat import ChatRequest, ChatResponse


router = APIRouter(
    prefix="/ai/chat",
    tags=["chat"],
)


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest):
    result = graph.invoke({
        "message": request.message,
        "response": "",
    })

    return ChatResponse(
        message=result["response"]
    )