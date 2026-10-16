from openai import OpenAI

from app.core.config import settings
from app.services.llm_service import LLMService


class OpenAIService(LLMService):
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.openai_api_key
        )

    def chat(self, message: str) -> str:
        response = self.client.responses.create(
            model=settings.openai_model,
            input=message,
        )

        return response.output_text