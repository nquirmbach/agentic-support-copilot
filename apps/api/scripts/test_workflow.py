#!/usr/bin/env python3
"""Test the complete AgentWorkflow in isolation."""

import asyncio
from src.agents.workflow import AgentWorkflow


async def test_workflow() -> bool:
    """Test AgentWorkflow in isolation."""
    print("🔄 Testing AgentWorkflow in isolation...")

    try:
        print("🏗️ Creating AgentWorkflow instance...")
        workflow = AgentWorkflow()
        print("✅ Workflow created successfully")

        print("🚀 Testing process_request...")
        result = await workflow.process_request("I need help with my password")
        print("✅ Workflow completed!")

        print(f"📊 Result: {result}")
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"   Type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_workflow())
    raise SystemExit(0 if success else 1)
