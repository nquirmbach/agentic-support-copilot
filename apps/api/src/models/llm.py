from abc import ABC, abstractmethod
from typing import List, Dict, Any
import os
from openai import AsyncAzureOpenAI
from dotenv import load_dotenv

load_dotenv()


class LlmProvider(ABC):
    """Abstract interface for LLM providers."""

    @abstractmethod
    async def embed(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts."""
        pass

    @abstractmethod
    async def chat(self, messages: List[Dict[str, str]]) -> str:
        """Generate chat completion from messages."""
        pass


class AzureOpenAIProvider(LlmProvider):
    """Azure OpenAI implementation of LLM provider."""

    def __init__(self):
        self.client = AsyncAzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv(
                "AZURE_OPENAI_API_VERSION", "2023-12-01-preview"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        )
        self.chat_deployment = os.getenv(
            "AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4")
        self.embedding_deployment = os.getenv(
            "AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME", "text-embedding-ada-002")

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

    async def chat(self, messages: List[Dict[str, str]]) -> str:
        """Generate chat completion using Azure OpenAI."""
        try:
            response = await self.client.chat.completions.create(
                model=self.chat_deployment,
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            raise Exception(f"Chat completion failed: {str(e)}")


def get_llm_provider() -> LlmProvider:
    """Factory function to get the configured LLM provider."""
    return AzureOpenAIProvider()
