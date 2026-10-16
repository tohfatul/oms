from app.services.llm_service import LLMService


class MockLLMService(LLMService):
    def chat(self, message: str) -> str:
        return (
            "Mock AI response. "
            f"You asked: {message}"
        )