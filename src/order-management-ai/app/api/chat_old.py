from fastapi import APIRouter, HTTPException

from app.models.chat import ChatRequest, ChatResponse
from app.services.llm_factory import create_llm_service


router = APIRouter(
    prefix="/ai/chat",
    tags=["chat"],
)

llm_service = create_llm_service()


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        response = llm_service.chat(request.message)

        return ChatResponse(
            message=response
        )

    except RuntimeError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc