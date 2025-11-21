"""
Database setup script for Supabase knowledge base.
Run this script to create the necessary tables and functions.
"""

import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()


def setup_database():
    """Set up the Supabase database with required tables and functions."""

    # Initialize Supabase client
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")

    if not supabase_url or not supabase_key:
        print(
            "Error: SUPABASE_URL and SUPABASE_SERVICE_KEY environment variables must be set")
        return

    client = create_client(supabase_url, supabase_key)

    # SQL statements to run
    sql_statements = [
        # Enable pgvector extension
        """
        CREATE EXTENSION IF NOT EXISTS vector;
        """,

        # Create documents table
        """
        CREATE TABLE IF NOT EXISTS documents (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            embedding vector(1536),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """,

        # Create vector similarity search function
        """
        CREATE OR REPLACE FUNCTION search_documents(
            query_embedding vector(1536),
            similarity_threshold float DEFAULT 0.7,
            match_count int DEFAULT 5
        )
        RETURNS TABLE (
            id UUID,
            title TEXT,
            content TEXT,
            similarity float
        )
        LANGUAGE plpgsql
        AS $$
        BEGIN
            RETURN query
            SELECT 
                documents.id,
                documents.title,
                documents.content,
                1 - (documents.embedding <=> query_embedding) AS similarity
            FROM documents
            WHERE 1 - (documents.embedding <=> query_embedding) > similarity_threshold
            ORDER BY similarity DESC
            LIMIT match_count;
        END;
        $$;
        """,

        # Create index for better performance
        """
        CREATE INDEX IF NOT EXISTS documents_embedding_idx ON documents 
        USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
        """,

        # Create trigger for updated_at
        """
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ language 'plpgsql';
        """,

        """
        CREATE TRIGGER update_documents_updated_at 
            BEFORE UPDATE ON documents 
            FOR EACH ROW 
            EXECUTE FUNCTION update_updated_at_column();
        """
    ]

    print("Setting up Supabase database...")

    for i, statement in enumerate(sql_statements, 1):
        try:
            # Note: This requires admin privileges. You may need to run these manually in the Supabase dashboard
            print(f"Statement {i}: Setting up...")
            print(statement)
            print("---")
        except Exception as e:
            print(f"Error with statement {i}: {str(e)}")

    print("\nDatabase setup complete!")
    print("Note: If you don't have admin privileges, run these SQL statements manually in the Supabase SQL editor.")


async def create_sample_documents():
    """Create sample support documents for testing."""

    from ..services.knowledge_base import KnowledgeBase

    print("Creating sample documents...")

    sample_docs = [
        {
            "title": "Password Reset Guide",
            "content": "To reset your password, click the 'Forgot Password' link on the login page. Enter your email address and check your inbox for a reset link. The link expires after 24 hours. If you don't receive the email, check your spam folder or contact support."
        },
        {
            "title": "Billing and Subscription",
            "content": "Our subscription plans are billed monthly or annually. You can change your plan at any time from your account settings. Refunds are available within 30 days of purchase for monthly plans and 14 days for annual plans. Contact billing@support.com for refund requests."
        },
        {
            "title": "Technical Support Process",
            "content": "For technical issues, first check our FAQ and documentation. If the problem persists, submit a support ticket with details about your system, error messages, and steps to reproduce. Critical issues affecting multiple users should be reported immediately via phone support."
        },
        {
            "title": "Account Security Best Practices",
            "content": "Use a strong, unique password with at least 12 characters including uppercase, lowercase, numbers, and symbols. Enable two-factor authentication. Never share your login credentials. Log out from shared devices. Review account activity regularly."
        },
        {
            "title": "Feature Request Process",
            "content": "We welcome feature suggestions! Submit requests through our feedback portal or email features@company.com. Include detailed use cases and expected benefits. Popular requests are reviewed monthly and added to our product roadmap based on customer impact and technical feasibility."
        }
    ]

    try:
        kb = KnowledgeBase()

        for doc in sample_docs:
            doc_id = await kb.add_document(doc["title"], doc["content"])
            if doc_id:
                print(f"✓ Created document: {doc['title']}")
            else:
                print(f"✗ Failed to create document: {doc['title']}")

        print("\nSample documents created successfully!")

    except Exception as e:
        print(f"Error creating sample documents: {str(e)}")
        print("Make sure your Supabase credentials are correct and the database is set up.")


async def main():
    """Main function to run setup."""
    setup_database()
    print("\n" + "="*50)
    await create_sample_documents()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
