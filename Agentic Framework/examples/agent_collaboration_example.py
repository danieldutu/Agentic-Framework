"""Agent collaboration example demonstrating Research and Synthesis agents working together."""

import asyncio

from agents.agent_factory import AgentFactory
from core.agent_types import AgentInput, AgentMessage
from communication.communication_handler import CommunicationHandler


async def run_collaboration_example() -> None:
    """Run a collaboration example between research and synthesis agents."""
    print("🤝 Starting Agent Collaboration Example")
    print("=" * 60)

    try:
        # Initialize communication handler
        comm_handler = CommunicationHandler()
        await comm_handler.initialize()

        # Create agent pair
        research_agent, synthesis_agent = AgentFactory.create_agent_pair(
            base_id="collab_demo",
            research_config={"research_depth": "medium", "max_search_results": 8},
            synthesis_config={"synthesis_style": "comprehensive", "max_sources": 15},
        )

        # Set communication handlers
        research_agent.set_communication_handler(comm_handler)
        synthesis_agent.set_communication_handler(comm_handler)

        # Register agents with communication handler
        await comm_handler.register_agent(
            research_agent.agent_id,
            lambda msg: asyncio.create_task(
                handle_research_message(research_agent, msg)
            ),
        )
        await comm_handler.register_agent(
            synthesis_agent.agent_id,
            lambda msg: asyncio.create_task(
                handle_synthesis_message(synthesis_agent, msg)
            ),
        )

        # Start both agents
        await research_agent.start()
        await synthesis_agent.start()

        print(f"✅ Started research agent: {research_agent.agent_id}")
        print(f"✅ Started synthesis agent: {synthesis_agent.agent_id}")

        # Define collaboration scenarios
        scenarios = [
            {
                "topic": "Sustainable AI Development",
                "research_queries": [
                    "What are current sustainable AI practices?",
                    "How can AI reduce environmental impact?",
                    "What are the challenges in green AI development?",
                ],
                "synthesis_focus": "comprehensive_analysis",
            },
            {
                "topic": "AI Ethics in Healthcare",
                "research_queries": [
                    "What are AI ethics principles in healthcare?",
                    "How is patient privacy protected in AI systems?",
                    "What are the regulatory requirements for healthcare AI?",
                ],
                "synthesis_focus": "policy_recommendations",
            },
        ]

        # Execute collaboration scenarios
        for i, scenario in enumerate(scenarios, 1):
            print(f"\n🎯 Collaboration Scenario {i}: {scenario['topic']}")
            print("=" * 50)

            await run_collaboration_scenario(
                research_agent, synthesis_agent, comm_handler, scenario
            )

            # Brief pause between scenarios
            if i < len(scenarios):
                await asyncio.sleep(3)

        # Show collaboration statistics
        print(f"\n📊 Collaboration Statistics:")
        print("-" * 40)

        research_metrics = research_agent.get_metrics()
        synthesis_metrics = synthesis_agent.get_metrics()

        print(f"Research Agent:")
        print(f"  Tasks Completed: {research_metrics.get('tasks_processed', 0)}")
        print(
            f"  Average Time: {research_metrics.get('total_processing_time', 0) / max(research_metrics.get('tasks_processed', 1), 1):.2f}s"
        )

        print(f"Synthesis Agent:")
        print(f"  Tasks Completed: {synthesis_metrics.get('tasks_processed', 0)}")
        print(
            f"  Average Time: {synthesis_metrics.get('total_processing_time', 0) / max(synthesis_metrics.get('tasks_processed', 1), 1):.2f}s"
        )

        # Show message history
        message_history = await comm_handler.get_message_history(limit=10)
        print(f"\nMessage Exchange History: {len(message_history)} messages")

        # Cleanup
        await research_agent.stop()
        await synthesis_agent.stop()
        await comm_handler.shutdown()

        print(f"\n🛑 Agents stopped and communication handler shutdown")

    except Exception as e:
        print(f"❌ Collaboration example failed: {e}")
        import traceback

        traceback.print_exc()

    print("\n🎉 Agent Collaboration Example Complete!")


async def run_collaboration_scenario(
    research_agent, synthesis_agent, comm_handler, scenario
) -> None:
    """Run a single collaboration scenario.

    Args:
        research_agent: Research agent instance
        synthesis_agent: Synthesis agent instance
        comm_handler: Communication handler
        scenario: Scenario configuration
    """
    topic = scenario["topic"]
    queries = scenario["research_queries"]

    print(f"🔬 Phase 1: Research on '{topic}'")
    print("-" * 30)

    # Collect research results
    research_results = []

    for j, query in enumerate(queries, 1):
        print(f"  📝 Query {j}: {query}")

        # Submit research task
        research_input = AgentInput(
            content={"query": query, "type": "technical", "depth": "medium"},
            metadata={"scenario": topic, "query_index": j, "collaboration": True},
        )

        try:
            task_id = await research_agent.submit_task(research_input)
            result = await research_agent.get_task_result(task_id, timeout=45.0)

            if result.confidence > 0.5:
                research_results.append(
                    {
                        "query": query,
                        "result": result.content,
                        "confidence": result.confidence,
                    }
                )
                print(f"    ✅ Research completed (confidence: {result.confidence:.2f})")
            else:
                print(
                    f"    ⚠️ Low confidence result (confidence: {result.confidence:.2f})"
                )

        except Exception as e:
            print(f"    ❌ Research failed: {e}")

    print(f"\n🧠 Phase 2: Synthesis of Research Findings")
    print("-" * 30)

    if research_results:
        # Prepare synthesis input
        synthesis_input = AgentInput(
            content={
                "topic": topic,
                "sources": research_results,
                "type": "integration",
                "style": scenario.get("synthesis_focus", "comprehensive"),
            },
            metadata={
                "scenario": topic,
                "source_count": len(research_results),
                "collaboration": True,
            },
        )

        try:
            # Submit synthesis task
            task_id = await synthesis_agent.submit_task(synthesis_input)
            synthesis_result = await synthesis_agent.get_task_result(
                task_id, timeout=60.0
            )

            if synthesis_result.confidence > 0.6:
                print(f"✅ Synthesis completed successfully!")
                print(f"📈 Confidence: {synthesis_result.confidence:.2f}")

                # Display synthesis summary
                content = synthesis_result.content
                if isinstance(content, dict):
                    synthesis = content.get("synthesis", {})

                    if synthesis.get("executive_summary"):
                        summary = (
                            synthesis["executive_summary"][:200] + "..."
                            if len(synthesis["executive_summary"]) > 200
                            else synthesis["executive_summary"]
                        )
                        print(f"📋 Executive Summary: {summary}")

                    if synthesis.get("key_findings"):
                        key_findings = (
                            synthesis["key_findings"][:150] + "..."
                            if len(synthesis["key_findings"]) > 150
                            else synthesis["key_findings"]
                        )
                        print(f"🔍 Key Findings: {key_findings}")

                    insights = content.get("insights", {})
                    if insights.get("deep_insights"):
                        deep_insights = (
                            insights["deep_insights"][:150] + "..."
                            if len(insights["deep_insights"]) > 150
                            else insights["deep_insights"]
                        )
                        print(f"💡 Deep Insights: {deep_insights}")

            else:
                print(
                    f"⚠️ Synthesis completed with low confidence: {synthesis_result.confidence:.2f}"
                )

        except Exception as e:
            print(f"❌ Synthesis failed: {e}")

    else:
        print("⚠️ No research results available for synthesis")


async def handle_research_message(agent, message: AgentMessage) -> None:
    """Handle incoming messages for research agent.

    Args:
        agent: Research agent instance
        message: Incoming message
    """
    try:
        # Process requests from other agents
        if message.message_type == "request":
            payload = message.payload
            if isinstance(payload, dict) and "research_request" in payload:
                # Handle research request from synthesis agent
                query = payload["research_request"]

                research_input = AgentInput(
                    content={"query": query, "type": "general", "depth": "light"},
                    source_agent=message.from_agent,
                )

                # Process and respond
                task_id = await agent.submit_task(research_input)
                result = await agent.get_task_result(task_id, timeout=30.0)

                # Send response back
                response_message = AgentMessage(
                    from_agent=agent.agent_id,
                    to_agent=message.from_agent,
                    message_type="response",
                    payload={"research_result": result.content},
                    correlation_id=message.id,
                )

                await agent.communicate(message.from_agent, response_message)

    except Exception as e:
        print(f"Error handling research message: {e}")


async def handle_synthesis_message(agent, message: AgentMessage) -> None:
    """Handle incoming messages for synthesis agent.

    Args:
        agent: Synthesis agent instance
        message: Incoming message
    """
    try:
        # Process responses and requests
        if message.message_type == "response":
            # Handle research results from research agent
            payload = message.payload
            if isinstance(payload, dict) and "research_result" in payload:
                print(
                    f"📨 Synthesis agent received research results from {message.from_agent}"
                )

        elif message.message_type == "request":
            # Handle synthesis requests
            payload = message.payload
            if isinstance(payload, dict) and "synthesis_request" in payload:
                # Process synthesis request
                topic = payload.get("topic", "Unknown topic")
                sources = payload.get("sources", [])

                synthesis_input = AgentInput(
                    content={"topic": topic, "sources": sources, "type": "analysis"},
                    source_agent=message.from_agent,
                )

                task_id = await agent.submit_task(synthesis_input)
                result = await agent.get_task_result(task_id, timeout=45.0)

                # Send response
                response_message = AgentMessage(
                    from_agent=agent.agent_id,
                    to_agent=message.from_agent,
                    message_type="response",
                    payload={"synthesis_result": result.content},
                    correlation_id=message.id,
                )

                await agent.communicate(message.from_agent, response_message)

    except Exception as e:
        print(f"Error handling synthesis message: {e}")


async def run_advanced_collaboration() -> None:
    """Run an advanced collaboration example with cross-agent requests."""
    print("🚀 Advanced Agent Collaboration Example")
    print("=" * 50)

    try:
        # Setup similar to basic collaboration
        comm_handler = CommunicationHandler()
        await comm_handler.initialize()

        research_agent, synthesis_agent = AgentFactory.create_agent_pair("advanced")

        research_agent.set_communication_handler(comm_handler)
        synthesis_agent.set_communication_handler(comm_handler)

        await comm_handler.register_agent(
            research_agent.agent_id,
            lambda msg: asyncio.create_task(
                handle_research_message(research_agent, msg)
            ),
        )
        await comm_handler.register_agent(
            synthesis_agent.agent_id,
            lambda msg: asyncio.create_task(
                handle_synthesis_message(synthesis_agent, msg)
            ),
        )

        await research_agent.start()
        await synthesis_agent.start()

        # Demonstrate cross-agent communication
        print("🔄 Testing cross-agent communication...")

        # Synthesis agent requests additional research
        request_message = AgentMessage(
            from_agent=synthesis_agent.agent_id,
            to_agent=research_agent.agent_id,
            message_type="request",
            payload={
                "research_request": "What are the latest developments in quantum computing applications?"
            },
        )

        # Send request and wait for response
        response = await comm_handler.send_request(
            research_agent.agent_id, request_message, timeout=60.0
        )

        print("✅ Cross-agent communication successful!")
        print(f"📨 Response received from {response.from_agent}")

        # Cleanup
        await research_agent.stop()
        await synthesis_agent.stop()
        await comm_handler.shutdown()

    except Exception as e:
        print(f"❌ Advanced collaboration failed: {e}")

    print("🎉 Advanced Collaboration Complete!")


if __name__ == "__main__":
    # Run examples
    asyncio.run(run_collaboration_example())
    print("\n" + "=" * 60 + "\n")
    asyncio.run(run_advanced_collaboration())
