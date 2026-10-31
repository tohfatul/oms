from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.chat import router as chat_router


app = FastAPI(
    title="OrderFlow AI Service",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://app.digizerones.com",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "order-management-ai",
    }


@app.get("/ai/health")
def ai_health():
    return {
        "status": "healthy",
        "service": "order-management-ai",
    }