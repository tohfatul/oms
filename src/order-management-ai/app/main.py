from fastapi import FastAPI

from app.api.chat import router as chat_router


app = FastAPI(
    title="OMS AI Service",
    version="1.0.0",
)


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }

@app.get("/ai/health")
def ai_health():
    return {"status": "healthy"}


app.include_router(chat_router)