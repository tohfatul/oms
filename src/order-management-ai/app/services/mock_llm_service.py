from app.services.llm_service import LLMService


class MockLLMService(LLMService):
    def chat(
        self,
        message: str,
        history=None,
    ) -> str:
        return f"Mock response: {message}"