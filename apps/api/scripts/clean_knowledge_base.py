#!/usr/bin/env python3
"""
Clean script for Supabase knowledge base.

This script removes all documents from the knowledge base.
"""

import os
import sys
from supabase import create_client, Client

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def create_supabase_client() -> Client:
    """Create Supabase client from environment variables."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")

    if not url or not key:
        raise ValueError(
            "SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in environment variables")

    return create_client(url, key)


def clean_knowledge_base(supabase: Client) -> None:
    """Remove all documents from the knowledge base."""
    print("🧹 Cleaning knowledge base...")

    try:
        # Get count before cleaning
        count_result = supabase.table("documents").select(
            "id", count="exact").execute()
        initial_count = count_result.count

        if initial_count == 0:
            print("📋 Knowledge base is already empty")
            return

        print(f"📊 Found {initial_count} documents to remove")

        # Delete all documents
        result = supabase.table("documents").delete().execute()

        # Verify cleanup
        count_result = supabase.table("documents").select(
            "id", count="exact").execute()
        final_count = count_result.count

        if final_count == 0:
            print(f"✅ Successfully removed {initial_count} documents")
        else:
            print(
                f"⚠️  Removed {initial_count - final_count} documents, {final_count} remaining")

    except Exception as e:
        print(f"❌ Error cleaning knowledge base: {e}")
        raise


def main():
    """Main clean function."""
    print("🧹 Cleaning Supabase Knowledge Base...")

    try:
        # Initialize client
        supabase = create_supabase_client()

        # Clean knowledge base
        clean_knowledge_base(supabase)

        print("✅ Knowledge base cleaned successfully!")

    except Exception as e:
        print(f"❌ Cleanup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
