"""Memory demonstration example showing agent memory capabilities."""

import asyncio
from datetime import datetime

from agents.agent_factory import AgentFactory
from core.agent_types import AgentInput
from memory.memory_store import MemoryStore


async def run_memory_demo() -> None:
    """Run a comprehensive memory demonstration."""
    print("🧠 Starting Memory System Demonstration")
    print("=" * 50)

    try:
        # Create a research agent for the demo
        agent = AgentFactory.create_research_agent(
            agent_id="memory_demo_agent", research_depth="medium"
        )

        await agent.start()
        print(f"✅ Agent '{agent.agent_id}' started")

        # Get the agent's memory store
        memory_store = agent.memory_store

        # Demonstrate different types of memory storage
        await demonstrate_memory_types(memory_store)

        # Demonstrate memory search capabilities
        await demonstrate_memory_search(memory_store)

        # Demonstrate memory with agent tasks
        await demonstrate_agent_memory_integration(agent)

        # Show memory statistics
        await show_memory_statistics(memory_store)

        # Demonstrate memory export/import
        await demonstrate_memory_backup(memory_store)

        await agent.stop()
        print("\n🛑 Agent stopped")

    except Exception as e:
        print(f"❌ Memory demo failed: {e}")
        import traceback

        traceback.print_exc()

    print("\n🎉 Memory Demonstration Complete!")


async def demonstrate_memory_types(memory_store: MemoryStore) -> None:
    """Demonstrate different types of memory storage."""
    print("\n📝 Phase 1: Memory Types Demonstration")
    print("-" * 40)

    # Store episodic memories (experiences)
    print("💭 Storing episodic memories...")
    episodic_id1 = await memory_store.remember_conversation(
        conversation=[
            {"role": "user", "content": "What is machine learning?"},
            {
                "role": "assistant",
                "content": "Machine learning is a subset of AI that enables systems to learn from data...",
            },
        ],
        context="Initial ML discussion",
        importance=0.8,
    )

    episodic_id2 = await memory_store.remember(
        content={
            "event": "Completed research on AI ethics",
            "outcome": "Found 15 relevant sources",
            "timestamp": datetime.now().isoformat(),
            "satisfaction": "high",
        },
        memory_type="episodic",
        tags=["research", "ethics", "ai"],
        importance=0.7,
    )

    print(f"  ✅ Stored conversation memory: {episodic_id1}")
    print(f"  ✅ Stored research event: {episodic_id2}")

    # Store semantic memories (facts/knowledge)
    print("\n🧠 Storing semantic memories...")
    semantic_id1 = await memory_store.remember_fact(
        fact="Python is a high-level programming language created by Guido van Rossum",
        source="Programming fundamentals",
        confidence=0.95,
        importance=0.6,
    )

    semantic_id2 = await memory_store.remember_fact(
        fact="Neural networks are inspired by biological neural networks",
        source="AI research literature",
        confidence=0.9,
        importance=0.8,
    )

    print(f"  ✅ Stored Python fact: {semantic_id1}")
    print(f"  ✅ Stored neural network fact: {semantic_id2}")

    # Store procedural memories (how-to knowledge)
    print("\n⚙️ Storing procedural memories...")
    procedural_id = await memory_store.remember_procedure(
        procedure_name="Conduct AI Research",
        steps=[
            "Define research question",
            "Search relevant sources",
            "Analyze and synthesize findings",
            "Document results",
            "Identify knowledge gaps",
        ],
        context="Standard research methodology",
        importance=0.9,
    )

    print(f"  ✅ Stored research procedure: {procedural_id}")


async def demonstrate_memory_search(memory_store: MemoryStore) -> None:
    """Demonstrate memory search capabilities."""
    print("\n🔍 Phase 2: Memory Search Demonstration")
    print("-" * 40)

    # Search by query
    print("🔎 Searching memories by query...")
    search_results = await memory_store.search_memories(
        query="machine learning", limit=5
    )

    print(f"  Found {len(search_results)} memories containing 'machine learning'")
    for i, memory in enumerate(search_results, 1):
        content_preview = (
            str(memory["content"])[:80] + "..."
            if len(str(memory["content"])) > 80
            else str(memory["content"])
        )
        print(f"    {i}. {memory['type']}: {content_preview}")

    # Search by memory type
    print("\n📚 Searching by memory type...")
    factual_memories = await memory_store.search_memories(
        memory_type="semantic", limit=3
    )

    print(f"  Found {len(factual_memories)} semantic memories")
    for memory in factual_memories:
        if isinstance(memory["content"], dict) and "fact" in memory["content"]:
            print(f"    • {memory['content']['fact']}")

    # Search by tags
    print("\n🏷️ Searching by tags...")
    research_memories = await memory_store.get_memories_by_tag("research", limit=3)

    print(f"  Found {len(research_memories)} memories tagged 'research'")
    for memory in research_memories:
        print(f"    • {memory['type']} memory (importance: {memory['importance']})")

    # Get important memories
    print("\n⭐ Finding important memories...")
    important_memories = await memory_store.get_important_memories(
        min_importance=0.7, limit=5
    )

    print(f"  Found {len(important_memories)} high-importance memories")
    for memory in important_memories:
        print(f"    • Importance {memory['importance']:.1f}: {memory['type']} memory")


async def demonstrate_agent_memory_integration(agent) -> None:
    """Demonstrate how agent tasks integrate with memory."""
    print("\n🤖 Phase 3: Agent-Memory Integration")
    print("-" * 40)

    # Perform research that will be stored in memory
    research_queries = [
        "What are the benefits of renewable energy?",
        "How does solar energy work?",
        "What are the challenges with wind power?",
    ]

    print("🔬 Performing research with memory integration...")

    for i, query in enumerate(research_queries, 1):
        print(f"  Query {i}: {query}")

        research_input = AgentInput(
            content={"query": query, "type": "factual", "depth": "light"},
            metadata={"demo": "memory_integration", "query_id": i},
        )

        try:
            task_id = await agent.submit_task(research_input)
            result = await agent.get_task_result(task_id, timeout=45.0)

            print(f"    ✅ Research completed (confidence: {result.confidence:.2f})")

        except Exception as e:
            print(f"    ❌ Research failed: {e}")

    # Check what was automatically stored in memory
    print("\n📖 Checking automatically stored research memories...")
    recent_memories = await agent.memory_store.get_recent_memories(limit=10)

    research_count = sum(1 for m in recent_memories if "research" in m.get("tags", []))
    print(f"  Found {research_count} research-related memories from recent activity")

    # Demonstrate memory-informed research
    print("\n🧠 Performing memory-informed research...")

    # This research should benefit from the previous renewable energy research
    informed_input = AgentInput(
        content={
            "query": "Compare renewable energy sources efficiency",
            "type": "comparative",
            "depth": "medium",
        },
        metadata={"demo": "memory_informed", "uses_memory": True},
    )

    try:
        task_id = await agent.submit_task(informed_input)
        result = await agent.get_task_result(task_id, timeout=60.0)

        print(f"  ✅ Memory-informed research completed")
        print(f"  📈 Confidence: {result.confidence:.2f}")

        # The agent should have found relevant context from previous research
        content = result.content
        if isinstance(content, dict):
            memory_matches = content.get("memory_matches", 0)
            print(f"  🔗 Used {memory_matches} memory matches for context")

    except Exception as e:
        print(f"  ❌ Memory-informed research failed: {e}")


async def show_memory_statistics(memory_store: MemoryStore) -> None:
    """Show comprehensive memory statistics."""
    print("\n📊 Phase 4: Memory Statistics")
    print("-" * 40)

    # Get overall statistics
    stats = await memory_store.get_memory_stats()

    print(f"Agent: {stats['agent_id']}")
    print(f"Total Memories: {stats['total_memories']}")

    print("\nMemory Types Distribution:")
    memory_types = stats.get("memory_types", {})
    for mem_type, count in memory_types.items():
        print(f"  {mem_type}: {count} memories")

    # Get memories by importance levels
    print("\nImportance Distribution:")
    all_memories = await memory_store.search_memories(limit=1000)

    importance_levels = {
        "Critical (0.9+)": len([m for m in all_memories if m["importance"] >= 0.9]),
        "High (0.7-0.89)": len(
            [m for m in all_memories if 0.7 <= m["importance"] < 0.9]
        ),
        "Medium (0.5-0.69)": len(
            [m for m in all_memories if 0.5 <= m["importance"] < 0.7]
        ),
        "Low (< 0.5)": len([m for m in all_memories if m["importance"] < 0.5]),
    }

    for level, count in importance_levels.items():
        print(f"  {level}: {count} memories")

    # Show most accessed memories
    print("\nMost Accessed Memories:")
    sorted_memories = sorted(
        all_memories, key=lambda m: m["accessed_count"], reverse=True
    )

    for i, memory in enumerate(sorted_memories[:3], 1):
        content_preview = (
            str(memory["content"])[:50] + "..."
            if len(str(memory["content"])) > 50
            else str(memory["content"])
        )
        print(f"  {i}. {content_preview} (accessed {memory['accessed_count']} times)")


async def demonstrate_memory_backup(memory_store: MemoryStore) -> None:
    """Demonstrate memory export and import capabilities."""
    print("\n💾 Phase 5: Memory Backup & Restore")
    print("-" * 40)

    # Export memories
    print("📤 Exporting memories...")
    exported_memories = await memory_store.export_memories()

    print(f"  ✅ Exported {len(exported_memories)} memories")

    # Show export sample
    if exported_memories:
        sample = exported_memories[0]
        print(f"  📄 Sample export format:")
        print(f"    ID: {sample['id']}")
        print(f"    Type: {sample['type']}")
        print(f"    Tags: {sample.get('tags', [])}")
        print(f"    Importance: {sample['importance']}")

    # Simulate memory cleanup and restore
    print("\n🧹 Simulating memory cleanup...")
    cleanup_count = await memory_store.cleanup_old_memories()
    print(f"  🗑️ Cleaned up {cleanup_count} old memory references")

    # Import demonstration (could import to a different agent)
    print("\n📥 Memory import capability available")
    print("  (In practice, you could import these memories to another agent)")
    print(f"  📊 Ready to import {len(exported_memories)} memory entries")


async def run_memory_performance_test() -> None:
    """Run a performance test for memory operations."""
    print("⚡ Memory Performance Test")
    print("=" * 30)

    try:
        # Create a test memory store
        memory_store = MemoryStore("performance_test_agent")

        # Test memory storage performance
        print("📝 Testing memory storage performance...")
        start_time = datetime.now()

        storage_tasks = []
        for i in range(20):
            task = memory_store.remember(
                content=f"Performance test memory {i}",
                memory_type="episodic" if i % 2 == 0 else "semantic",
                tags=["performance", "test", f"batch_{i//5}"],
                importance=0.1 + (i % 10) * 0.1,
            )
            storage_tasks.append(task)

        # Store all memories concurrently
        await asyncio.gather(*storage_tasks)

        storage_time = (datetime.now() - start_time).total_seconds()
        print(f"  ✅ Stored 20 memories in {storage_time:.2f} seconds")
        print(f"  📊 Average: {storage_time/20:.3f} seconds per memory")

        # Test search performance
        print("\n🔍 Testing search performance...")
        search_start = datetime.now()

        search_tasks = [
            memory_store.search_memories(query="performance", limit=10),
            memory_store.search_memories(memory_type="semantic", limit=10),
            memory_store.get_memories_by_tag("test", limit=10),
            memory_store.get_important_memories(min_importance=0.5, limit=10),
        ]

        search_results = await asyncio.gather(*search_tasks)
        search_time = (datetime.now() - search_start).total_seconds()

        print(f"  ✅ Performed 4 different searches in {search_time:.2f} seconds")
        print(f"  📊 Found {sum(len(r) for r in search_results)} total results")

    except Exception as e:
        print(f"❌ Performance test failed: {e}")

    print("🎉 Performance Test Complete!")


if __name__ == "__main__":
    # Run the main demo
    asyncio.run(run_memory_demo())
    print("\n" + "=" * 50 + "\n")
    # Run performance test
    asyncio.run(run_memory_performance_test())
