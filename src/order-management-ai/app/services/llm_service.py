from abc import ABC, abstractmethod


class LLMService(ABC):
    @abstractmethod
    def chat(self, message: str) -> str:
        pass