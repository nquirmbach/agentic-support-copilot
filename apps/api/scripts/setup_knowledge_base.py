#!/usr/bin/env python3
"""
Supabase Knowledge Base Setup Script

This script sets up the vector knowledge base for the Agentic Support Copilot:
1. Creates documents table with pgvector support
2. Sets up vector similarity search functions
3. Seeds sample support articles
4. Generates embeddings using Azure OpenAI
"""

import os
import sys
import json
from typing import List, Dict
from supabase import create_client, Client
from openai import AzureOpenAI
import numpy as np
from dotenv import load_dotenv

# Load environment variables from .env file (in parent directory)
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(env_path)

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


def create_azure_client() -> AzureOpenAI:
    """Create Azure OpenAI client from environment variables."""
    return AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
    )


def check_database_schema(supabase: Client) -> None:
    """Check if the database schema is properly set up."""
    print("🔧 Checking database schema...")

    try:
        # Check if documents table exists
        result = supabase.table("documents").select(
            "id", count="exact").execute()
        print("✅ Database schema is ready")
        return True
    except Exception as e:
        print(f"❌ Database schema not found: {e}")
        print("📋 Please run the SQL migration first:")
        print("   1. Open your Supabase dashboard")
        print("   2. Go to SQL Editor")
        print(
            "   3. Run the migration from: infra/supabase/migrations/001_setup_schema.sql")
        return False


def get_sample_articles() -> List[Dict[str, str]]:
    """Get sample support articles for seeding."""
    return [
        {
            "title": "How to Reset Your Password",
            "content": "To reset your password, click the 'Forgot Password' link on the login page. Enter your email address and check your inbox for a password reset link. Click the link and create a new password. Make sure your new password is at least 8 characters long and includes a mix of letters, numbers, and symbols. If you don't receive the email within 5 minutes, check your spam folder."
        },
        {
            "title": "Troubleshooting Login Issues",
            "content": "If you're having trouble logging in, first verify you're using the correct email and password. Ensure Caps Lock is off and check for typos. Clear your browser cache and cookies, then try again. If using a password manager, ensure it's autofilling the correct credentials. For persistent issues, try resetting your password or contact support if you continue to experience problems."
        },
        {
            "title": "Setting Up Two-Factor Authentication",
            "content": "Two-factor authentication adds an extra layer of security to your account. Go to Settings > Security > Two-Factor Authentication. Choose your preferred method: SMS text messages or authenticator app. For SMS, enter your phone number and verify it with the code sent. For authenticator apps, scan the QR code with apps like Google Authenticator or Authy, then enter the 6-digit code to complete setup."
        },
        {
            "title": "Managing Account Notifications",
            "content": "Customize your notification preferences in Settings > Notifications. You can choose to receive emails for account activity, security alerts, product updates, and marketing communications. Toggle each category on or off based on your preferences. You can also set the frequency of digest emails (immediate, daily, or weekly). Changes take effect immediately, and you can update preferences anytime."
        },
        {
            "title": "Understanding Your Billing Statement",
            "content": "Your billing statement shows all charges and credits for the billing period. It includes your subscription fee, any add-on services, taxes, and payments received. You can access statements from Billing > Payment History > View Statements. Each statement shows the billing period, due date, and itemized charges. Download statements as PDFs for your records. Contact billing support if you have questions about specific charges."
        },
        {
            "title": "How to Cancel Your Subscription",
            "content": "To cancel your subscription, go to Settings > Subscription > Cancel Subscription. You'll be asked to provide a reason for cancellation (optional but helpful). Your access continues until the end of your current billing period. You can reactivate anytime before the cancellation takes effect. After cancellation, export your data as it will be permanently deleted after 30 days. Refunds are prorated based on your remaining subscription time."
        },
        {
            "title": "Data Privacy and Security Settings",
            "content": "Protect your privacy with comprehensive security settings. Enable two-factor authentication, review connected apps and remove unauthorized access, and set up login alerts. Control data sharing preferences in Privacy Settings. You can request a copy of your data or delete your account entirely. We use industry-standard encryption and comply with GDPR, CCPA, and other privacy regulations. Review our privacy policy for detailed information."
        },
        {
            "title": "Troubleshooting Mobile App Issues",
            "content": "For mobile app problems, first ensure you have the latest version installed. Force close and restart the app, then check your internet connection. Clear the app cache from your device settings. If issues persist, try uninstalling and reinstalling the app (your data is saved in the cloud). For iOS users, check if the app has necessary permissions in Settings. Android users should clear the app cache and data from Application Settings."
        },
        {
            "title": "API Integration and Webhooks",
            "content": "Integrate with our API to automate workflows. Generate API keys from Developer Settings > API Keys. Use our RESTful endpoints for CRUD operations, and set up webhooks to receive real-time notifications for events like new signups or payments. Rate limits apply: 1000 requests per hour for standard plans. Review API documentation for authentication methods, endpoint specifications, and code examples in multiple programming languages."
        },
        {
            "title": "Exporting and Importing Data",
            "content": "Export your data from Settings > Data Management > Export. Choose export format (CSV, JSON, or XML) and select data types to include. Large exports are processed asynchronously and emailed when ready. To import data, use the same section and upload files in supported formats. Validate data format before importing to avoid errors. Import history shows status and any error details. Contact support for assistance with large data migrations."
        }
    ]


def generate_embeddings(azure_client: AzureOpenAI, texts: List[str]) -> List[List[float]]:
    """Generate embeddings for a list of texts using Azure OpenAI."""
    print("🧠 Generating embeddings...")
    embeddings = []

    for i, text in enumerate(texts):
        try:
            response = azure_client.embeddings.create(
                model=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME"),
                input=text
            )
            embedding = response.data[0].embedding
            embeddings.append(embedding)
            print(f"  Generated embedding {i+1}/{len(texts)}")
        except Exception as e:
            print(f"❌ Error generating embedding for text {i+1}: {e}")
            raise

    return embeddings


def seed_knowledge_base(supabase: Client, azure_client: AzureOpenAI) -> None:
    """Seed the knowledge base with sample articles and embeddings."""
    print("📚 Seeding knowledge base...")

    # Check if articles already exist
    existing_count = supabase.table("documents").select(
        "id", count="exact").execute()
    if existing_count.count > 0:
        print(
            f"📋 Found {existing_count.count} existing articles. Skipping seeding.")
        return

    articles = get_sample_articles()
    texts = [article["content"] for article in articles]

    # Generate embeddings
    embeddings = generate_embeddings(azure_client, texts)

    # Insert articles with embeddings
    for i, article in enumerate(articles):
        try:
            data = {
                "title": article["title"],
                "content": article["content"],
                "embedding": embeddings[i]
            }

            result = supabase.table("documents").insert(data).execute()
            print(f"  Inserted article: {article['title']}")

        except Exception as e:
            print(f"❌ Error inserting article {i+1}: {e}")
            raise

    print(f"✅ Successfully seeded {len(articles)} articles")


def main():
    """Main setup function."""
    print("🚀 Setting up Supabase Knowledge Base...")

    try:
        # Initialize clients
        supabase = create_supabase_client()
        azure_client = create_azure_client()

        # Check database schema
        if not check_database_schema(supabase):
            print("❌ Setup failed: Database schema not ready")
            sys.exit(1)

        # Seed knowledge base
        seed_knowledge_base(supabase, azure_client)

        print("✅ Knowledge base setup completed successfully!")
        print("🎯 You can now use the vector search functionality.")

    except Exception as e:
        print(f"❌ Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
