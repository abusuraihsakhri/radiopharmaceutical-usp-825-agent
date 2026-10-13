"""
Deterministic mock response provider; external model integrations are not implemented.
"""
from typing import Dict, Any, Optional
from .base import PHIGuard


class MockLLM:
    def __init__(self, system_name: str = "Radiopharmaceutical Usp 825 Agent"):
        self.system_name = system_name

    def invoke(self, prompt: str) -> str:
        PHIGuard.assert_no_phi(prompt)
        return f"[{self.system_name} mock response]: No scientific verification or regulatory assessment performed. Query: '{prompt[:60]}...'."


class LLMFactory:
    """Creates configured LLM client instances with zero-PHI protection."""

    @staticmethod
    def create(provider: str = "mock", system_name: str = "Radiopharmaceutical Usp 825 Agent"):
        prov = str(provider).lower()
        if prov in ["mock", "deterministic", "test"]:
            return MockLLM(system_name)
        raise ValueError(f"Model provider {provider!r} is not implemented; use MODEL_PROVIDER=mock.")
