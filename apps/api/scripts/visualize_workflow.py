#!/usr/bin/env python3
"""
Script to visualize the Agentic Support Copilot workflow.
Generates a Mermaid diagram showing the agent pipeline flow.
"""

from src.agents.workflow import AgentWorkflow


def main():
    """Generate and display the workflow visualization."""
    print("🎨 Generating Agentic Support Copilot Workflow Visualization")
    print("=" * 60)

    # Create workflow instance
    workflow = AgentWorkflow()

    # Generate visualization
    print("📊 Workflow Diagram (Mermaid format):")
    print("-" * 40)

    diagram = workflow.visualize_workflow()
    print(diagram)

    # Save to file
    filename = workflow.save_workflow_diagram("docs/workflow_diagram.md")
    print(f"\n💾 Diagram saved to: {filename}")

    print("\n🔍 Workflow Flow:")
    print("1. Request Text → Classifier Agent (intent, sentiment, urgency)")
    print("2. Classifier → Retriever Agent (knowledge search)")
    print("3. Retriever → Writer Agent (response generation)")
    print("4. Writer → Guard Agent (safety validation)")
    print("5. Guard → Logger Agent (metrics & logging)")
    print("6. Logger → Final Response")

    print(f"\n⏱️  Estimated processing time: 8-15 seconds per request")
    print(f"🤖 Framework: LangGraph with 5 sequential agents")


if __name__ == "__main__":
    main()
