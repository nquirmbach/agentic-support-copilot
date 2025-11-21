from abc import ABC, abstractmethod
from typing import List, Dict, Any
import os
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()


class LlmProvider(ABC):
    """Abstract interface for LLM providers."""

    @abstractmethod
    async def embed(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts."""
        pass

    @abstractmethod
    async def chat(self, messages: List[Dict[str, str]], fast: bool = False) -> str:
        """Generate chat completion from messages.

        If fast=True, a lightweight deployment (e.g. gpt-4o-mini) may be used.
        """
        pass


class OpenAIProvider(LlmProvider):
    """OpenAI implementation of LLM provider."""

    def __init__(self):
        self.client = AsyncOpenAI(
            base_url=os.getenv("OPENAI_ENDPOINT"),
            api_key=os.getenv("OPENAI_API_KEY"),
        )
        self.chat_deployment = os.getenv(
            "OPENAI_DEPLOYMENT_NAME", "gpt-4o")
        self.fast_chat_deployment = os.getenv(
            "OPENAI_FAST_DEPLOYMENT_NAME", "gpt-4.1-mini")
        self.embedding_deployment = os.getenv(
            "OPENAI_EMBEDDING_DEPLOYMENT_NAME", "text-embedding-ada-002")

    async def embed(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using Azure OpenAI."""
        try:
            response = await self.client.embeddings.create(
                model=self.embedding_deployment,
                input=texts
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            raise Exception(f"Embedding generation failed: {str(e)}")

    async def chat(self, messages: List[Dict[str, str]], fast: bool = False) -> str:
        """Generate chat completion using Azure OpenAI.

        When fast=True, use the fast_chat_deployment (e.g. gpt-4o-mini) instead of
        the default chat_deployment.
        """
        model = self.fast_chat_deployment if fast else self.chat_deployment
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7,
                max_tokens=2000,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            raise Exception(f"Chat completion failed: {str(e)}")


def get_llm_provider() -> LlmProvider:
    """Factory function to get the configured LLM provider."""
    return OpenAIProvider()
