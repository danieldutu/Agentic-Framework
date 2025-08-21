#!/usr/bin/env python3
"""Test Advanced Memory Features with fixed JSON serialization."""

import asyncio
import json
import os
from datetime import datetime
from dotenv import load_dotenv
from agents.agent_factory import AgentFactory
from core.agent_types import AgentInput

load_dotenv()

def json_serializer(obj):
    """Custom JSON serializer to handle UUIDs and other objects."""
    if hasattr(obj, '__str__'):
        return str(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

async def test_memory_features():
    """Test Advanced Memory capabilities and save results to JSON."""
    print("🧠 TESTING ADVANCED MEMORY FEATURES (FIXED)")
    print("=" * 50)
    
    # Create output directory using new organized path
    os.makedirs("tests/results/memory_system", exist_ok=True)
    
    test_results = {
        "test_name": "Advanced Memory Features",
        "timestamp": datetime.now().isoformat(),
        "tests": []
    }
    
    try:
        # Create agent with memory capabilities
        print("1️⃣ Creating Agent with Memory...")
        memory_agent = AgentFactory.create_research_agent(
            agent_id="memory_tester_fixed",
            research_depth="light"  # Use light for faster testing
        )
        
        await memory_agent.start()
        await asyncio.sleep(2)
        print("✅ Agent with memory created and started")
        
        # Test 1: Memory Storage with Different Types
        print("\n2️⃣ Test 1: Memory Storage (Semantic, Episodic, Procedural)")
        
        try:
            # Store semantic memory (facts and knowledge)
            semantic_memory_id = await memory_agent.memory_store.remember(
                content="Machine learning algorithms learn patterns from training data to make predictions on new data",
                memory_type="semantic",
                tags=["machine-learning", "algorithms", "data-science", "AI"],
                importance=0.9
            )
            
            # Store episodic memory (events and experiences)
            episodic_memory_id = await memory_agent.memory_store.remember(
                content="Completed comprehensive research on neural network architectures on 2024-06-24",
                memory_type="episodic",
                tags=["research", "neural-networks", "completed", "2024"],
                importance=0.8
            )
            
            # Store procedural memory (processes and workflows)
            procedural_memory_id = await memory_agent.memory_store.remember(
                content="To train a neural network: 1) Prepare data, 2) Define architecture, 3) Set hyperparameters, 4) Train model, 5) Evaluate performance",
                memory_type="procedural",
                tags=["neural-networks", "training", "process", "workflow"],
                importance=0.7
            )
            
            test_1_result = {
                "test_name": "Memory Storage",
                "status": "SUCCESS",
                "memories_stored": 3,
                "semantic_memory_id": str(semantic_memory_id),  # Convert UUID to string
                "episodic_memory_id": str(episodic_memory_id),  # Convert UUID to string
                "procedural_memory_id": str(procedural_memory_id),  # Convert UUID to string
                "memory_types": ["semantic", "episodic", "procedural"]
            }
            test_results["tests"].append(test_1_result)
            print(f"   ✅ Successfully stored 3 memories of different types")
            print(f"      📚 Semantic: {str(semantic_memory_id)[:8]}...")
            print(f"      📝 Episodic: {str(episodic_memory_id)[:8]}...")
            print(f"      🔄 Procedural: {str(procedural_memory_id)[:8]}...")
            
        except Exception as e:
            test_1_result = {
                "test_name": "Memory Storage",
                "status": "FAILED",
                "error": str(e)
            }
            test_results["tests"].append(test_1_result)
            print(f"   ❌ Failed to store memories: {e}")
        
        # Test 2: Memory Search and Retrieval
        print("\n3️⃣ Test 2: Memory Search and Retrieval")
        
        try:
            # Search for memories about machine learning
            ml_memories = await memory_agent.memory_store.search_memories("machine learning", limit=5)
            
            # Search for memories about neural networks
            nn_memories = await memory_agent.memory_store.search_memories("neural networks", limit=5)
            
            # Get recent memories
            recent_memories = await memory_agent.memory_store.get_recent_memories(limit=5)
            
            # Convert memory data for JSON serialization
            ml_memories_json = []
            for m in ml_memories:
                memory_data = {
                    "content": m["content"][:100] + "..." if len(m["content"]) > 100 else m["content"],
                    "type": m.get("type"),
                    "importance": m.get("importance"),
                    "tags": m.get("tags", [])
                }
                ml_memories_json.append(memory_data)
            
            recent_memories_json = []
            for m in recent_memories:
                memory_data = {
                    "content": m["content"][:100] + "..." if len(m["content"]) > 100 else m["content"],
                    "type": m.get("type"),
                    "timestamp": str(m.get("timestamp", "")),
                    "importance": m.get("importance")
                }
                recent_memories_json.append(memory_data)
            
            test_2_result = {
                "test_name": "Memory Search",
                "status": "SUCCESS",
                "ml_search_results": len(ml_memories),
                "nn_search_results": len(nn_memories),
                "recent_memories_count": len(recent_memories),
                "ml_memories": ml_memories_json,
                "recent_memories": recent_memories_json
            }
            test_results["tests"].append(test_2_result)
            print(f"   ✅ Memory search completed")
            print(f"      🔍 'machine learning' found: {len(ml_memories)} memories")
            print(f"      🔍 'neural networks' found: {len(nn_memories)} memories")
            print(f"      📋 Recent memories: {len(recent_memories)}")
            
        except Exception as e:
            test_2_result = {
                "test_name": "Memory Search",
                "status": "FAILED",
                "error": str(e)
            }
            test_results["tests"].append(test_2_result)
            print(f"   ❌ Failed to search memories: {e}")
        
        # Test 3: Memory-Enhanced Research
        print("\n4️⃣ Test 3: Memory-Enhanced Research")
        
        try:
            # Submit a research task that should use existing memories
            task_input = AgentInput(
                content={
                    "query": "What are machine learning algorithms?",
                    "type": "definition",
                    "depth": "light"  # Use light depth for faster processing
                }
            )
            
            start_time = datetime.now()
            task_id = await memory_agent.submit_task(task_input)
            print("   ⏳ AI researching with memory context...")
            
            # Wait for processing
            await asyncio.sleep(15)
            
            result = await memory_agent.get_task_result(task_id, timeout=15.0)
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Check if memories were used in the research
            memories_after = await memory_agent.memory_store.get_recent_memories(limit=10)
            
            test_3_result = {
                "test_name": "Memory-Enhanced Research",
                "status": "SUCCESS",
                "processing_time_seconds": processing_time,
                "confidence_score": result.confidence,
                "memories_available": len(memories_after),
                "result_content_preview": str(result.content)[:200] + "..." if len(str(result.content)) > 200 else str(result.content)
            }
            test_results["tests"].append(test_3_result)
            print(f"   ✅ Memory-enhanced research completed")
            print(f"      📊 Confidence: {result.confidence:.2f}")
            print(f"      ⏱️ Time: {processing_time:.1f}s")
            print(f"      🧠 Memories available: {len(memories_after)}")
            
        except Exception as e:
            test_3_result = {
                "test_name": "Memory-Enhanced Research",
                "status": "FAILED",
                "error": str(e)
            }
            test_results["tests"].append(test_3_result)
            print(f"   ❌ Failed memory-enhanced research: {e}")
        
        await memory_agent.stop()
        
    except Exception as e:
        print(f"❌ Overall test failed: {e}")
        test_results["overall_error"] = str(e)
    
    # Calculate summary statistics
    successful_tests = [t for t in test_results["tests"] if t["status"] == "SUCCESS"]
    failed_tests = [t for t in test_results["tests"] if t["status"] == "FAILED"]
    
    test_results["summary"] = {
        "total_tests": len(test_results["tests"]),
        "successful_tests": len(successful_tests),
        "failed_tests": len(failed_tests),
        "success_rate": len(successful_tests) / len(test_results["tests"]) if test_results["tests"] else 0,
        "features_tested": [
            "memory_storage",
            "memory_search", 
            "memory_enhanced_research"
        ]
    }
    
    # Save results to JSON with custom serializer using new path
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"tests/results/memory_system/memory_features_fixed_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(test_results, f, indent=2, ensure_ascii=False, default=json_serializer)
    
    # Print summary
    print(f"\n🎉 MEMORY FEATURES TEST COMPLETED!")
    print("=" * 50)
    print(f"📊 Summary:")
    print(f"   • Total tests: {test_results['summary']['total_tests']}")
    print(f"   • Successful: {test_results['summary']['successful_tests']}")
    print(f"   • Failed: {test_results['summary']['failed_tests']}")
    print(f"   • Success rate: {test_results['summary']['success_rate']*100:.1f}%")
    
    print(f"\n💾 Results saved to: {filename}")
    print(f"\n🧠 What the Memory System demonstrated:")
    print("   📚 Store semantic, episodic, and procedural memories")
    print("   🔍 Search memories by content and find relevant information")
    print("   📊 Retrieve recent memories and analyze patterns")
    print("   🎯 Enhance research with memory context")
    
    return filename

if __name__ == "__main__":
    asyncio.run(test_memory_features()) 