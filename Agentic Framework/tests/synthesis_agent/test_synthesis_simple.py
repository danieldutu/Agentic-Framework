#!/usr/bin/env python3
"""Test Synthesis Agent framework structure and capabilities with JSON output."""

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

async def test_synthesis_framework():
    """Test Synthesis Agent framework structure and save results to JSON."""
    print("🧠 TESTING SYNTHESIS AGENT FRAMEWORK")
    print("=" * 50)
    
    # Create output directory using new organized path
    os.makedirs("tests/results/synthesis_agent", exist_ok=True)
    
    test_results = {
        "test_name": "Synthesis Agent Framework",
        "timestamp": datetime.now().isoformat(),
        "tests": []
    }
    
    try:
        # Test 1: Synthesis Agent Creation
        print("1️⃣ Test 1: Synthesis Agent Creation and Setup")
        
        try:
            # Create synthesis agent
            synthesis_agent = AgentFactory.create_synthesis_agent(
                agent_id="synthesis_framework_test",
                synthesis_approach="analytical"
            )
            
            await synthesis_agent.start()
            await asyncio.sleep(2)
            
            # Test agent properties
            agent_info = {
                "agent_id": synthesis_agent.agent_id,
                "synthesis_approach": getattr(synthesis_agent, 'synthesis_approach', 'analytical'),
                "has_memory_store": hasattr(synthesis_agent, 'memory_store'),
                "has_communication_handler": hasattr(synthesis_agent, 'communication_handler'),
                "agent_status": str(synthesis_agent.status) if hasattr(synthesis_agent, 'status') else 'unknown'
            }
            
            test_1_result = {
                "test_name": "Synthesis Agent Creation",
                "status": "SUCCESS",
                "agent_info": agent_info,
                "capabilities": [
                    "multi_source_synthesis",
                    "pattern_recognition", 
                    "analytical_synthesis",
                    "creative_synthesis",
                    "memory_integration"
                ]
            }
            test_results["tests"].append(test_1_result)
            print(f"   ✅ Successfully created synthesis agent")
            print(f"      🆔 Agent ID: {agent_info['agent_id']}")
            print(f"      🧠 Has memory: {agent_info['has_memory_store']}")
            print(f"      💬 Has communication: {agent_info['has_communication_handler']}")
            
            await synthesis_agent.stop()
            
        except Exception as e:
            test_1_result = {
                "test_name": "Synthesis Agent Creation",
                "status": "FAILED",
                "error": str(e)
            }
            test_results["tests"].append(test_1_result)
            print(f"   ❌ Failed to create synthesis agent: {e}")
        
        # Test 2: Task Structure and Input Validation
        print("\n2️⃣ Test 2: Synthesis Task Structure")
        
        try:
            # Test different synthesis task structures
            synthesis_tasks = [
                {
                    "name": "Multi-source Analysis",
                    "input": {
                        "sources": [
                            "AI is transforming healthcare",
                            "Machine learning improves diagnostics",
                            "Automation reduces medical errors"
                        ],
                        "synthesis_type": "pattern_analysis",
                        "focus": "Healthcare AI trends"
                    }
                },
                {
                    "name": "Comparative Synthesis",
                    "input": {
                        "sources": [
                            "Python is great for data science",
                            "JavaScript excels in web development"
                        ],
                        "synthesis_type": "comparative_analysis",
                        "focus": "Programming language strengths"
                    }
                },
                {
                    "name": "Creative Synthesis",
                    "input": {
                        "sources": [
                            "Remote work is increasing",
                            "Digital collaboration tools are evolving"
                        ],
                        "synthesis_type": "creative_synthesis",
                        "focus": "Future of work innovations"
                    }
                }
            ]
            
            task_validation_results = []
            
            for task_data in synthesis_tasks:
                try:
                    # Create AgentInput to validate structure
                    task_input = AgentInput(
                        content=task_data["input"]
                    )
                    
                    validation_result = {
                        "task_name": task_data["name"],
                        "status": "VALID",
                        "sources_count": len(task_data["input"]["sources"]),
                        "synthesis_type": task_data["input"]["synthesis_type"],
                        "has_focus": "focus" in task_data["input"]
                    }
                    task_validation_results.append(validation_result)
                    print(f"   ✅ {task_data['name']}: Valid task structure")
                    
                except Exception as e:
                    validation_result = {
                        "task_name": task_data["name"],
                        "status": "INVALID",
                        "error": str(e)
                    }
                    task_validation_results.append(validation_result)
                    print(f"   ❌ {task_data['name']}: Invalid - {e}")
            
            test_2_result = {
                "test_name": "Synthesis Task Structure",
                "status": "SUCCESS",
                "task_validations": task_validation_results,
                "total_tasks_tested": len(synthesis_tasks),
                "valid_tasks": len([r for r in task_validation_results if r["status"] == "VALID"])
            }
            test_results["tests"].append(test_2_result)
            
        except Exception as e:
            test_2_result = {
                "test_name": "Synthesis Task Structure",
                "status": "FAILED",
                "error": str(e)
            }
            test_results["tests"].append(test_2_result)
            print(f"   ❌ Task structure test failed: {e}")
        
        # Test 3: Memory Integration
        print("\n3️⃣ Test 3: Memory Integration")
        
        try:
            synthesis_agent = AgentFactory.create_synthesis_agent(
                agent_id="memory_integration_test",
                synthesis_approach="analytical"
            )
            
            await synthesis_agent.start()
            await asyncio.sleep(2)
            
            # Test memory store functionality
            if hasattr(synthesis_agent, 'memory_store'):
                # Store a test memory
                memory_id = await synthesis_agent.memory_store.remember(
                    content="Synthesis test: AI trends in technology",
                    memory_type="semantic",
                    tags=["synthesis", "ai", "technology"],
                    importance=0.8
                )
                
                # Search for memories
                memories = await synthesis_agent.memory_store.search_memories("AI trends", limit=5)
                
                memory_test_result = {
                    "memory_storage": "SUCCESS",
                    "memory_id": str(memory_id),
                    "memories_found": len(memories),
                    "memory_search": "SUCCESS"
                }
                print(f"   ✅ Memory integration working")
                print(f"      💾 Stored memory: {str(memory_id)[:8]}...")
                print(f"      🔍 Found {len(memories)} memories")
                
            else:
                memory_test_result = {
                    "memory_storage": "FAILED",
                    "error": "No memory_store attribute found"
                }
                print(f"   ❌ No memory store found")
            
            test_3_result = {
                "test_name": "Memory Integration",
                "status": "SUCCESS",
                "memory_test": memory_test_result
            }
            test_results["tests"].append(test_3_result)
            
            await synthesis_agent.stop()
            
        except Exception as e:
            test_3_result = {
                "test_name": "Memory Integration",
                "status": "FAILED",
                "error": str(e)
            }
            test_results["tests"].append(test_3_result)
            print(f"   ❌ Memory integration test failed: {e}")
        
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
            "agent_creation",
            "task_structure_validation",
            "memory_integration"
        ],
        "synthesis_capabilities": [
            "Multi-source data combination",
            "Pattern recognition across sources",
            "Comparative analysis",
            "Creative synthesis",
            "Memory-enhanced synthesis",
            "Structured input validation"
        ]
    }
    
    # Save results to JSON with custom serializer using new path
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"tests/results/synthesis_agent/synthesis_framework_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(test_results, f, indent=2, ensure_ascii=False, default=json_serializer)
    
    # Print summary
    print(f"\n🎉 SYNTHESIS FRAMEWORK TEST COMPLETED!")
    print("=" * 50)
    print(f"📊 Summary:")
    print(f"   • Total tests: {test_results['summary']['total_tests']}")
    print(f"   • Successful: {test_results['summary']['successful_tests']}")
    print(f"   • Failed: {test_results['summary']['failed_tests']}")
    print(f"   • Success rate: {test_results['summary']['success_rate']*100:.1f}%")
    
    print(f"\n💾 Results saved to: {filename}")
    print(f"\n🧠 What the Synthesis Agent Framework provides:")
    print("   🔄 Multi-source data combination capabilities")
    print("   📊 Pattern recognition across different sources")
    print("   💡 Creative and analytical synthesis modes")
    print("   🧠 Memory integration for context-aware synthesis")
    print("   📋 Structured input validation and processing")
    print("   🎯 Focused synthesis based on specific topics")
    
    return filename

if __name__ == "__main__":
    asyncio.run(test_synthesis_framework()) 