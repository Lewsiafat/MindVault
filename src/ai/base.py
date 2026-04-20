from abc import ABC, abstractmethod


class AIProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, *, temperature: float = 0.2) -> str:
        """Return raw text. Caller handles JSON parsing / code-fence stripping."""
        ...
