from typing import Literal

from pydantic import BaseModel, Field

from app.models.order_draft import PendingOrderDraft


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(
        min_length=1,
        max_length=8000,
    )


class ChatRequest(BaseModel):
    message: str = Field(
        min_length=1,
        max_length=4000,
    )

    history: list[ChatMessage] = Field(
        default_factory=list,
        max_length=20,
    )

    pending_order: PendingOrderDraft | None = None


class ChatResponse(BaseModel):
    message: str
    pending_order: PendingOrderDraft | None = None
    sources: list[str] = Field(
        default_factory=list
    )