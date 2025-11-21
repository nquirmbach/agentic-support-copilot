#!/usr/bin/env python3
"""
Test script for Supabase vector search functionality.

This script tests the knowledge base setup and vector search capabilities:
1. Tests database connection
2. Verifies document count
3. Tests vector similarity search
4. Validates search results
"""

import os
import sys
from typing import List, Dict
from supabase import create_client, Client
from openai import OpenAI
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables from the apps/api/.env file
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
load_dotenv(env_path)


def create_supabase_client() -> Client:
    """Create Supabase client from environment variables."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")

    if not url or not key:
        raise ValueError(
            "SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in environment variables")

    return create_client(url, key)


def create_openai_client() -> OpenAI:
    """Create Azure OpenAI client from environment variables."""
    return OpenAI(
        base_url=os.getenv("OPENAI_ENDPOINT"),
        api_key=os.getenv("OPENAI_API_KEY")
    )


def test_database_connection(supabase: Client) -> bool:
    """Test basic database connection."""
    print("🔗 Testing database connection...")

    try:
        result = supabase.table("documents").select(
            "id", count="exact").execute()
        print(f"✅ Connected successfully. Found {result.count} documents")
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False


def test_vector_search(supabase: Client, openai: OpenAI) -> bool:
    """Test vector similarity search functionality."""
    print("🔍 Testing vector search...")

    # Test query
    test_query = "I forgot my password and need to reset it"

    try:
        # Generate embedding for test query
        response = openai.embeddings.create(
            model=os.getenv("OPENAI_EMBEDDING_DEPLOYMENT_NAME"),
            input=test_query
        )
        query_embedding = response.data[0].embedding

        print(f"📝 Query: '{test_query}'")
        print(f"🧠 Generated embedding with {len(query_embedding)} dimensions")

        # Perform vector search
        result = supabase.rpc(
            "match_documents",
            {"query_embedding": query_embedding, "match_threshold": 0.7}
        ).execute()

        if not result.data:
            print("⚠️  No results found with threshold 0.7, trying 0.5...")
            result = supabase.rpc(
                "match_documents",
                {"query_embedding": query_embedding, "match_threshold": 0.5}
            ).execute()

        if result.data:
            print(f"✅ Found {len(result.data)} similar documents:")
            for i, doc in enumerate(result.data[:3]):  # Show top 3
                print(f"   {i+1}. {doc['title']}")
                print(f"      Similarity: {doc['similarity']:.3f}")
                print(f"      Content: {doc['content'][:100]}...")
                print()
        else:
            print("❌ No search results found")
            return False

        return True

    except Exception as e:
        print(f"❌ Vector search failed: {e}")
        return False


def test_document_retrieval(supabase: Client) -> bool:
    """Test basic document retrieval."""
    print("📚 Testing document retrieval...")

    try:
        # Get all documents
        result = supabase.table("documents").select(
            "title, content").limit(5).execute()

        if result.data:
            print(f"✅ Retrieved {len(result.data)} documents:")
            for i, doc in enumerate(result.data):
                print(f"   {i+1}. {doc['title']}")
                print(
                    f"      Content length: {len(doc['content'])} characters")
        else:
            print("❌ No documents found")
            return False

        return True

    except Exception as e:
        print(f"❌ Document retrieval failed: {e}")
        return False


def main():
    """Main test function."""
    print("🧪 Testing Supabase Knowledge Base...")
    print("=" * 50)

    try:
        # Initialize clients
        supabase = create_supabase_client()
        openai = create_openai_client()

        # Run tests
        tests = [
            ("Database Connection", lambda: test_database_connection(supabase)),
            ("Document Retrieval", lambda: test_document_retrieval(supabase)),
            ("Vector Search", lambda: test_vector_search(supabase, openai)),
        ]

        passed = 0
        total = len(tests)

        for test_name, test_func in tests:
            print(f"\n--- {test_name} ---")
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} failed")

        print("\n" + "=" * 50)
        print(f"📊 Test Results: {passed}/{total} tests passed")

        if passed == total:
            print("🎉 All tests passed! Knowledge base is ready.")
        else:
            print("⚠️  Some tests failed. Check the errors above.")
            sys.exit(1)

    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
