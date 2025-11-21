import os
import asyncio
from typing import List, Dict, Any, Optional
from supabase import create_client, Client
from ..models.llm import get_llm_provider


class KnowledgeBase:
    """Service for interacting with the Supabase knowledge base."""

    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
        self.llm = get_llm_provider()

        # Initialize Supabase client
        if not self.supabase_url or not self.supabase_key:
            raise ValueError(
                "Supabase credentials (SUPABASE_URL, SUPABASE_SERVICE_KEY) must be configured")

        try:
            self.client: Client = create_client(
                self.supabase_url, self.supabase_key)
        except Exception as e:
            raise ValueError(f"Failed to initialize Supabase client: {e}")

    async def search_similar(self, query: str, limit: int = 5, threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Search for similar documents using vector similarity."""
        print("📚 KB: search_similar() called...")

        try:
            print("📚 KB: Generating embedding...")
            # Generate embedding for query
            embeddings = await self.llm.embed([query])
            query_embedding = embeddings[0]
            print("📚 KB: Embedding generated successfully!")

            # Run synchronous Supabase call in thread pool to avoid blocking
            def _search():
                return self.client.rpc(
                    'match_documents',
                    {
                        'query_embedding': query_embedding,
                        'match_threshold': threshold
                    }
                ).execute()

            response = await asyncio.to_thread(_search)

            if response.data:
                return response.data
            else:
                return []

        except Exception as e:
            print(f"Knowledge base search failed: {str(e)}")
            return []

    async def add_document(self, title: str, content: str) -> Optional[str]:
        """Add a new document to the knowledge base."""
        if self.demo_mode:
            print(f"Demo mode: Would add document '{title}' to knowledge base")
            return f"demo-{hash(title) % 10000}"

        try:
            # Generate embedding for content
            embeddings = await self.llm.embed([content])
            content_embedding = embeddings[0]

            # Run synchronous Supabase call in thread pool to avoid blocking
            def _insert():
                return self.client.table('documents').insert({
                    'title': title,
                    'content': content,
                    'embedding': content_embedding
                }).execute()

            response = await asyncio.to_thread(_insert)

            if response.data:
                return response.data[0]['id']
            else:
                return None

        except Exception as e:
            print(f"Failed to add document: {str(e)}")
            return None

    def get_all_documents(self) -> List[Dict[str, Any]]:
        """Get all documents from the knowledge base."""
        if self.demo_mode:
            return [
                {
                    "id": "demo-1",
                    "title": "Password Reset Guide",
                    "content": "To reset your password, click the 'Forgot Password' link on the login page. Enter your email address and check your inbox for a reset link. The link expires after 24 hours. If you don't receive the email, check your spam folder or contact support."
                },
                {
                    "id": "demo-2",
                    "title": "Billing and Subscription",
                    "content": "Our subscription plans are billed monthly or annually. You can change your plan at any time from your account settings. Refunds are available within 30 days of purchase for monthly plans and 14 days for annual plans. Contact billing@support.com for refund requests."
                }
            ]

        try:
            response = self.client.table('documents').select('*').execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Failed to get documents: {str(e)}")
            return []
