"""Basic research example demonstrating the Research Agent."""

import asyncio

from agents.agent_factory import AgentFactory
from core.agent_types import AgentInput


async def run_basic_research_example() -> None:
    """Run a basic research example."""
    print("🔬 Starting Basic Research Agent Example")
    print("=" * 50)

    try:
        # Create a research agent
        research_agent = AgentFactory.create_research_agent(
            agent_id="demo_researcher", research_depth="medium", max_search_results=5
        )

        # Start the agent
        await research_agent.start()
        print(f"✅ Research agent '{research_agent.agent_id}' started")

        # Example research queries
        queries = [
            {
                "query": "What are the latest developments in artificial intelligence?",
                "type": "trend",
                "depth": "medium",
            },
            {
                "query": "How does machine learning differ from traditional programming?",
                "type": "comparative",
                "depth": "light",
            },
            {
                "query": "What are the applications of natural language processing?",
                "type": "general",
                "depth": "medium",
            },
        ]

        # Process each research query
        for i, query_data in enumerate(queries, 1):
            print(f"\n📊 Research Query {i}: {query_data['query']}")
            print("-" * 40)

            # Create input for the agent
            research_input = AgentInput(
                content=query_data,
                metadata={"example": "basic_research", "query_number": i},
            )

            # Submit the research task
            task_id = await research_agent.submit_task(research_input)
            print(f"📤 Submitted research task: {task_id}")

            # Get the results
            try:
                result = await research_agent.get_task_result(task_id, timeout=60.0)

                if result.confidence > 0.5:
                    print("✅ Research completed successfully!")
                    print(f"📈 Confidence: {result.confidence:.2f}")

                    # Display key findings
                    content = result.content
                    if isinstance(content, dict):
                        findings = content.get("findings", {})
                        key_findings = findings.get("key_findings", [])

                        if key_findings:
                            print("\n🔍 Key Findings:")
                            for j, finding in enumerate(key_findings[:3], 1):
                                print(f"  {j}. {finding}")

                        # Display analysis summary
                        analysis = content.get("analysis", {})
                        if analysis and analysis.get("summary"):
                            print(f"\n📋 Analysis Summary:")
                            summary = (
                                analysis["summary"][:200] + "..."
                                if len(analysis["summary"]) > 200
                                else analysis["summary"]
                            )
                            print(f"  {summary}")

                else:
                    print("⚠️ Research completed with low confidence")
                    print(f"📉 Confidence: {result.confidence:.2f}")

            except Exception as e:
                print(f"❌ Research failed: {e}")

            # Add delay between queries
            if i < len(queries):
                await asyncio.sleep(2)

        # Show research history
        print(f"\n📚 Research History:")
        print("-" * 40)
        history = await research_agent.get_research_history(limit=5)

        if history:
            for entry in history:
                content = entry.get("content", {})
                query = content.get("query", "Unknown query")
                timestamp = entry.get("timestamp", "Unknown time")
                print(f"  • {query} (at {timestamp})")
        else:
            print("  No research history found")

        # Suggest related research
        print(f"\n💡 Related Research Suggestions:")
        print("-" * 40)
        suggestions = await research_agent.suggest_related_research(
            "artificial intelligence applications"
        )

        if suggestions:
            for suggestion in suggestions:
                print(f"  • {suggestion}")
        else:
            print("  No suggestions generated")

        # Show agent metrics
        print(f"\n📊 Agent Performance Metrics:")
        print("-" * 40)
        metrics = research_agent.get_metrics()
        print(f"  Tasks Processed: {metrics.get('tasks_processed', 0)}")
        print(f"  Tasks Failed: {metrics.get('tasks_failed', 0)}")
        print(
            f"  Average Processing Time: {metrics.get('total_processing_time', 0) / max(metrics.get('tasks_processed', 1), 1):.2f}s"
        )

        # Stop the agent
        await research_agent.stop()
        print(f"\n🛑 Research agent stopped")

    except Exception as e:
        print(f"❌ Example failed: {e}")
        import traceback

        traceback.print_exc()

    print("\n🎉 Basic Research Example Complete!")


async def run_focused_research_example() -> None:
    """Run a focused research example on a specific topic."""
    print("🎯 Starting Focused Research Example")
    print("=" * 50)

    try:
        # Create a research agent with deep research configuration
        research_agent = AgentFactory.create_research_agent(
            agent_id="focused_researcher", research_depth="deep", max_search_results=10
        )

        await research_agent.start()

        # Focused research topic
        topic = "Large Language Models in Healthcare"

        print(f"🔬 Researching: {topic}")
        print("-" * 40)

        # Create comprehensive research input
        research_input = AgentInput(
            content={
                "query": topic,
                "type": "technical",
                "depth": "deep",
                "focus_areas": [
                    "Current applications",
                    "Challenges and limitations",
                    "Future potential",
                    "Ethical considerations",
                    "Regulatory aspects",
                ],
            },
            metadata={"example": "focused_research", "priority": 8},
        )

        # Submit and process the research
        task_id = await research_agent.submit_task(research_input)
        result = await research_agent.get_task_result(task_id, timeout=90.0)

        # Display comprehensive results
        if result.confidence > 0.6:
            print("✅ Comprehensive research completed!")
            print(f"📈 Confidence: {result.confidence:.2f}")

            content = result.content
            if isinstance(content, dict):
                # Show structured findings
                findings = content.get("findings", {})

                print(f"\n📋 Research Summary:")
                print(f"  Query: {content.get('query')}")
                print(f"  Type: {content.get('research_type')}")
                print(f"  Sources Found: {content.get('sources_found', 0)}")
                print(f"  Processing Time: {result.processing_time:.2f}s")

                # Show key findings
                key_findings = findings.get("key_findings", [])
                if key_findings:
                    print(f"\n🔍 Key Findings:")
                    for i, finding in enumerate(key_findings, 1):
                        print(f"  {i}. {finding}")

                # Show analysis
                analysis = content.get("analysis", {})
                if analysis:
                    print(f"\n📊 Analysis:")
                    if analysis.get("summary"):
                        print(f"  Summary: {analysis['summary'][:300]}...")
                    if analysis.get("key_insights"):
                        print(
                            f"  Insights: {len(analysis['key_insights'])} insights generated"
                        )

        await research_agent.stop()

    except Exception as e:
        print(f"❌ Focused research failed: {e}")

    print("\n🎉 Focused Research Example Complete!")


if __name__ == "__main__":
    # Run the examples
    asyncio.run(run_basic_research_example())
    print("\n" + "=" * 50 + "\n")
    asyncio.run(run_focused_research_example())
