#!/usr/bin/env python3
"""Demo that stores AI agent responses in JSON format for easy understanding."""

import asyncio
import json
import os
from datetime import datetime
from dotenv import load_dotenv
from agents.agent_factory import AgentFactory
from core.agent_types import AgentInput

load_dotenv()

class JSONResultCollector:
    """Collects and stores AI agent results in JSON format."""
    
    def __init__(self, output_dir="ai_responses"):
        self.output_dir = output_dir
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results = []
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
    
    def add_result(self, agent_type, query, result, processing_time, error=None):
        """Add a result to the collection."""
        result_data = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "agent_type": agent_type,
            "query": query,
            "processing_time_seconds": processing_time,
            "success": error is None,
            "error": str(error) if error else None,
            "result": result
        }
        self.results.append(result_data)
    
    def save_session(self):
        """Save all results from this session to a JSON file."""
        filename = f"{self.output_dir}/ai_responses_{self.session_id}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        return filename
    
    def save_individual_result(self, result_data):
        """Save an individual result to its own file."""
        timestamp = result_data["timestamp"].replace(":", "").replace(".", "")
        agent_type = result_data["agent_type"]
        filename = f"{self.output_dir}/{agent_type}_{timestamp}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, indent=2, ensure_ascii=False)
        return filename

async def test_research_agent_with_json():
    """Test research agent and save responses to JSON."""
    print("🔬 TESTING RESEARCH AGENT - SAVING TO JSON")
    print("=" * 50)
    
    collector = JSONResultCollector()
    
    research_agent = AgentFactory.create_research_agent(
        agent_id="json_researcher",
        research_depth="medium"
    )
    
    await research_agent.start()
    await asyncio.sleep(1)
    
    # Test different types of research questions
    test_questions = [
        {
            "query": "What are the benefits of renewable energy?",
            "type": "analytical",
            "description": "Analytical research about renewable energy"
        },
        {
            "query": "How does machine learning work?",
            "type": "technical", 
            "description": "Technical explanation of machine learning"
        },
        {
            "query": "What is cryptocurrency?",
            "type": "definition",
            "description": "Definition and explanation of cryptocurrency"
        },
        {
            "query": "Future applications of quantum computing",
            "type": "creative",
            "description": "Creative exploration of quantum computing future"
        }
    ]
    
    for i, test in enumerate(test_questions, 1):
        print(f"\n📝 Question {i}/4: {test['description']}")
        print(f"   Query: '{test['query']}'")
        print(f"   Type: {test['type']}")
        
        start_time = datetime.now()
        
        try:
            task_input = AgentInput(
                content={
                    "query": test["query"],
                    "type": test["type"],
                    "depth": "medium"
                }
            )
            
            task_id = await research_agent.submit_task(task_input)
            print("   ⏳ AI processing...")
            
            # Wait for result with longer timeout
            result = await research_agent.get_task_result(task_id, timeout=30.0)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            print(f"   ✅ Completed! Confidence: {result.confidence:.2f}")
            print(f"   ⏱️ Time: {processing_time:.1f}s")
            
            # Add to collector
            collector.add_result(
                agent_type="research_agent",
                query=test["query"],
                result={
                    "confidence": result.confidence,
                    "processing_time": result.processing_time,
                    "content": result.content,
                    "metadata": result.metadata,
                    "research_type": test["type"]
                },
                processing_time=processing_time
            )
            
            # Save individual result
            individual_file = collector.save_individual_result(collector.results[-1])
            print(f"   💾 Saved to: {individual_file}")
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            print(f"   ❌ Error: {e}")
            
            collector.add_result(
                agent_type="research_agent",
                query=test["query"],
                result=None,
                processing_time=processing_time,
                error=e
            )
    
    await research_agent.stop()
    return collector

async def test_synthesis_agent_with_json():
    """Test synthesis agent and save responses to JSON."""
    print(f"\n🧠 TESTING SYNTHESIS AGENT - SAVING TO JSON")
    print("=" * 50)
    
    collector = JSONResultCollector()
    
    synthesis_agent = AgentFactory.create_synthesis_agent(
        agent_id="json_synthesizer",
        synthesis_approach="analytical"
    )
    
    await synthesis_agent.start()
    await asyncio.sleep(1)
    
    # Test synthesis scenarios
    synthesis_tests = [
        {
            "name": "Programming Language Comparison",
            "sources": [
                "Python is excellent for data science and AI development",
                "JavaScript is the dominant language for web development",
                "Java is widely used in enterprise applications",
                "Python has simple, readable syntax",
                "JavaScript runs in browsers and on servers with Node.js",
                "Java is strongly typed and platform-independent"
            ],
            "focus": "Compare programming languages for different use cases"
        },
        {
            "name": "Technology Trends Analysis", 
            "sources": [
                "AI and machine learning are transforming industries",
                "Cloud computing adoption is accelerating",
                "Remote work is becoming permanent for many companies",
                "Cybersecurity threats are increasing",
                "Blockchain technology is finding new applications",
                "IoT devices are connecting everything"
            ],
            "focus": "Identify key technology trends and their impacts"
        }
    ]
    
    for i, test in enumerate(synthesis_tests, 1):
        print(f"\n🔄 Synthesis {i}/2: {test['name']}")
        print(f"   Sources: {len(test['sources'])} data points")
        print(f"   Focus: {test['focus']}")
        
        start_time = datetime.now()
        
        try:
            task_input = AgentInput(
                content={
                    "sources": test["sources"],
                    "synthesis_type": "analytical_synthesis",
                    "focus": test["focus"],
                    "approach": "comprehensive"
                }
            )
            
            task_id = await synthesis_agent.submit_task(task_input)
            print("   ⏳ AI synthesizing...")
            
            result = await synthesis_agent.get_task_result(task_id, timeout=30.0)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            print(f"   ✅ Synthesis completed! Confidence: {result.confidence:.2f}")
            print(f"   ⏱️ Time: {processing_time:.1f}s")
            
            # Add to collector
            collector.add_result(
                agent_type="synthesis_agent",
                query=test["name"],
                result={
                    "confidence": result.confidence,
                    "processing_time": result.processing_time,
                    "content": result.content,
                    "metadata": result.metadata,
                    "sources_count": len(test["sources"]),
                    "synthesis_focus": test["focus"]
                },
                processing_time=processing_time
            )
            
            # Save individual result
            individual_file = collector.save_individual_result(collector.results[-1])
            print(f"   💾 Saved to: {individual_file}")
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            print(f"   ❌ Error: {e}")
            
            collector.add_result(
                agent_type="synthesis_agent",
                query=test["name"],
                result=None,
                processing_time=processing_time,
                error=e
            )
    
    await synthesis_agent.stop()
    return collector

async def create_summary_json(research_collector, synthesis_collector):
    """Create a comprehensive summary JSON file."""
    print(f"\n📊 CREATING COMPREHENSIVE SUMMARY")
    print("=" * 40)
    
    # Combine all results
    all_results = research_collector.results + synthesis_collector.results
    
    # Calculate statistics
    successful_results = [r for r in all_results if r["success"]]
    failed_results = [r for r in all_results if not r["success"]]
    
    avg_processing_time = sum(r["processing_time_seconds"] for r in successful_results) / len(successful_results) if successful_results else 0
    avg_confidence = sum(r["result"]["confidence"] for r in successful_results if r["result"]) / len([r for r in successful_results if r["result"]]) if successful_results else 0
    
    summary = {
        "session_summary": {
            "timestamp": datetime.now().isoformat(),
            "total_tests": len(all_results),
            "successful_tests": len(successful_results),
            "failed_tests": len(failed_results),
            "success_rate": len(successful_results) / len(all_results) if all_results else 0,
            "average_processing_time_seconds": avg_processing_time,
            "average_confidence_score": avg_confidence
        },
        "agent_performance": {
            "research_agent": {
                "tests": len(research_collector.results),
                "successes": len([r for r in research_collector.results if r["success"]]),
                "avg_time": sum(r["processing_time_seconds"] for r in research_collector.results if r["success"]) / len([r for r in research_collector.results if r["success"]]) if research_collector.results else 0
            },
            "synthesis_agent": {
                "tests": len(synthesis_collector.results),
                "successes": len([r for r in synthesis_collector.results if r["success"]]),
                "avg_time": sum(r["processing_time_seconds"] for r in synthesis_collector.results if r["success"]) / len([r for r in synthesis_collector.results if r["success"]]) if synthesis_collector.results else 0
            }
        },
        "detailed_results": all_results
    }
    
    # Save comprehensive summary
    summary_file = f"ai_responses/comprehensive_summary_{research_collector.session_id}.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Summary saved to: {summary_file}")
    print(f"📊 Total tests: {len(all_results)}")
    print(f"✅ Successful: {len(successful_results)}")
    print(f"❌ Failed: {len(failed_results)}")
    print(f"📈 Success rate: {len(successful_results)/len(all_results)*100:.1f}%")
    print(f"⏱️ Average time: {avg_processing_time:.1f}s")
    print(f"🎯 Average confidence: {avg_confidence:.2f}")
    
    return summary_file

async def main():
    """Run the JSON output demo."""
    print("🚀 AI AGENT FRAMEWORK - JSON OUTPUT DEMO")
    print("=" * 60)
    print("This demo will test both agents and save all responses to JSON files")
    print("You can easily read and understand what the AI produced!\n")
    
    try:
        # Test research agent
        research_collector = await test_research_agent_with_json()
        
        # Test synthesis agent
        synthesis_collector = await test_synthesis_agent_with_json()
        
        # Create comprehensive summary
        summary_file = await create_summary_json(research_collector, synthesis_collector)
        
        print(f"\n🎉 ALL TESTS COMPLETED!")
        print("=" * 40)
        print("📁 Check the 'ai_responses' folder for all JSON files:")
        print("   • Individual responses for each test")
        print("   • Comprehensive summary with statistics")
        print("   • Easy-to-read JSON format")
        print(f"\n📋 Main summary file: {summary_file}")
        
        # Show what files were created
        print(f"\n📂 Files created in ai_responses/:")
        import os
        if os.path.exists("ai_responses"):
            files = sorted(os.listdir("ai_responses"))
            for file in files:
                if file.endswith('.json'):
                    print(f"   📄 {file}")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 