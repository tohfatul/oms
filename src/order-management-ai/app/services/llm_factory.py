from app.core.config import settings
from app.services.bedrock_service import BedrockService
from app.services.llm_service import LLMService
from app.services.mock_llm_service import MockLLMService


def create_llm_service() -> LLMService:
    provider = settings.llm_provider.lower()

    if provider == "bedrock":
        return BedrockService()

    if provider == "mock":
        return MockLLMService()

    raise ValueError(
        f"Unsupported LLM provider: {settings.llm_provider}"
    )