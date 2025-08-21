#!/usr/bin/env python3
"""Simple AI Agent Framework Demo with JSON output."""

import asyncio
import json
import os
from datetime import datetime
from dotenv import load_dotenv
from agents.agent_factory import AgentFactory
from core.agent_types import AgentInput

load_dotenv()

async def test_research_agent_json():
    """Test research agent capabilities and save responses to JSON."""
    print("🔬 TESTING RESEARCH AGENT (JSON OUTPUT)")
    print("=" * 50)
    
    # Create output directory using new organized path
    os.makedirs("tests/results/research_agent", exist_ok=True)
    
    try:
        # Create research agent
        research_agent = AgentFactory.create_research_agent(
            agent_id="json_demo_research",
            research_depth="medium"
        )
        
        # Start the agent
        await research_agent.start()
        await asyncio.sleep(2)
        print("✅ Research agent started successfully")
        
        # Test questions with different research types
        test_questions = [
            {
                "query": "What is artificial intelligence?", 
                "type": "definition",
                "description": "Testing definition research"
            },
            {
                "query": "Compare Python vs JavaScript for web development",
                "type": "analytical", 
                "description": "Testing analytical research"
            },
            {
                "query": "What is the future of renewable energy?",
                "type": "creative",
                "description": "Testing creative research"
            }
        ]
        
        results = []
        
        for i, question in enumerate(test_questions, 1):
            print(f"\n{i}️⃣ Testing: {question['description']}")
            print(f"   Question: {question['query']}")
            
            try:
                # Create task input
                task_input = AgentInput(
                    content={
                        "query": question["query"],
                        "type": question["type"],
                        "depth": "medium"
                    }
                )
                
                # Submit task
                start_time = datetime.now()
                task_id = await research_agent.submit_task(task_input)
                print("   ⏳ AI thinking and researching...")
                
                # Get result
                result = await research_agent.get_task_result(task_id, timeout=30.0)
                processing_time = (datetime.now() - start_time).total_seconds()
                
                # Prepare JSON-friendly result
                json_result = {
                    "question_number": i,
                    "question": question["query"],
                    "research_type": question["type"],
                    "description": question["description"],
                    "timestamp": datetime.now().isoformat(),
                    "processing_time_seconds": processing_time,
                    "confidence_score": result.confidence,
                    "ai_response": str(result.content),
                    "success": True,
                    "agent_id": research_agent.agent_id
                }
                
                results.append(json_result)
                
                # Save individual result
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"tests/results/research_agent/question_{i}_{question['type']}_{timestamp}.json"
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(json_result, f, indent=2, ensure_ascii=False)
                
                print(f"   ✅ Research completed!")
                print(f"      📊 Confidence: {result.confidence:.2f}")
                print(f"      ⏱️ Time: {processing_time:.1f}s")
                print(f"      💾 Saved to: {filename}")
                
            except Exception as e:
                print(f"   ❌ Failed: {e}")
                error_result = {
                    "question_number": i,
                    "question": question["query"],
                    "research_type": question["type"],
                    "description": question["description"],
                    "timestamp": datetime.now().isoformat(),
                    "success": False,
                    "error": str(e),
                    "agent_id": research_agent.agent_id
                }
                results.append(error_result)
        
        # Create comprehensive summary
        summary = {
            "test_name": "Research Agent JSON Demo",
            "timestamp": datetime.now().isoformat(),
            "total_questions": len(test_questions),
            "successful_tests": len([r for r in results if r.get("success", False)]),
            "failed_tests": len([r for r in results if not r.get("success", False)]),
            "average_confidence": sum([r.get("confidence_score", 0) for r in results if r.get("success", False)]) / max(len([r for r in results if r.get("success", False)]), 1),
            "total_processing_time": sum([r.get("processing_time_seconds", 0) for r in results]),
            "results": results,
            "agent_info": {
                "agent_id": research_agent.agent_id,
                "agent_type": "research_agent",
                "research_depth": "medium"
            },
            "features_demonstrated": [
                "definition_research",
                "analytical_research", 
                "creative_research",
                "json_output_format",
                "confidence_scoring",
                "processing_time_tracking"
            ]
        }
        
        # Save comprehensive summary
        summary_filename = f"tests/results/research_agent/comprehensive_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_filename, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        # Stop the agent
        await research_agent.stop()
        
        print(f"\n🎉 ALL TESTS COMPLETED!")
        print("=" * 50)
        print(f"📊 Summary:")
        print(f"   • Total Questions: {summary['total_questions']}")
        print(f"   • Successful: {summary['successful_tests']}")
        print(f"   • Failed: {summary['failed_tests']}")
        print(f"   • Average Confidence: {summary['average_confidence']:.2f}")
        print(f"   • Total Time: {summary['total_processing_time']:.1f}s")
        print(f"\n💾 Comprehensive summary saved to: {summary_filename}")
        
        return summary_filename
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return None

if __name__ == "__main__":
    asyncio.run(test_research_agent_json()) 