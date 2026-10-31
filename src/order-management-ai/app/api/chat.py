from fastapi import (
    APIRouter,
    Header,
    HTTPException,
    status,
)

from app.agents.graph import graph
from app.models.chat import (
    ChatRequest,
    ChatResponse,
)
from app.security.entra_token_validator import (
    EntraTokenValidationError,
    validate_entra_access_token,
)
from app.services.llm_service import ConversationMessage


router = APIRouter(
    prefix="/ai/chat",
    tags=["chat"],
)


@router.post(
    "",
    response_model=ChatResponse,
)
async def chat(
    request: ChatRequest,
    authorization: str | None = Header(
        default=None
    ),
):
    access_token = get_bearer_token(
        authorization
    )

    try:
        validate_entra_access_token(
            access_token
        )
    except EntraTokenValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={
                "WWW-Authenticate": "Bearer",
            },
        ) from exc

    history = [
        ConversationMessage(
            role=item.role,
            content=item.content,
        )
        for item in request.history
    ]

    result = await graph.ainvoke({
        "message": request.message,
        "history": history,
        "access_token": access_token,
        "response": "",
        "pending_order": request.pending_order,
        "tool_decision": None,
        "tool_results": [],
        "sources": [],
    })

    return ChatResponse(
        message=result["response"],
        pending_order=result["pending_order"],
        sources=result.get("sources", []),
    )


def get_bearer_token(
    authorization: str | None,
) -> str:
    if not authorization:
        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail=(
                "Authorization header is required."
            ),
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    scheme, _, token = authorization.partition(" ")

    if (
        scheme.lower() != "bearer"
        or not token.strip()
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail=(
                "A valid Bearer token is required."
            ),
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    return token.strip()