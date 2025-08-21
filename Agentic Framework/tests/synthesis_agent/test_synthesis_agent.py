#!/usr/bin/env python3
"""Test Synthesis Agent functionality specifically with JSON output."""

import asyncio
import json
import os
from datetime import datetime
from dotenv import load_dotenv
from agents.agent_factory import AgentFactory
from core.agent_types import AgentInput

load_dotenv()

async def test_synthesis_agent():
    """Test Synthesis Agent capabilities and save results to JSON."""
    print("🧠 TESTING SYNTHESIS AGENT FUNCTIONALITY")
    print("=" * 50)
    
    # Create output directory
    os.makedirs("synthesis_tests", exist_ok=True)
    
    test_results = {
        "test_name": "Synthesis Agent Functionality",
        "timestamp": datetime.now().isoformat(),
        "tests": []
    }
    
    try:
        # Create synthesis agent
        print("1️⃣ Creating Synthesis Agent...")
        synthesis_agent = AgentFactory.create_synthesis_agent(
            agent_id="synthesis_tester",
            synthesis_approach="analytical"
        )
        
        await synthesis_agent.start()
        await asyncio.sleep(2)
        print("✅ Synthesis Agent created and started")
        
        # Test 1: Multi-source Programming Language Analysis
        print("\n2️⃣ Test 1: Programming Language Multi-source Analysis")
        
        sources_1 = [
            "Python is excellent for data science with libraries like NumPy, Pandas, and Scikit-learn",
            "JavaScript is the dominant language for web development, both frontend and backend",
            "Python has clean, readable syntax that makes it beginner-friendly",
            "JavaScript has event-driven programming and asynchronous capabilities",
            "Python is widely used in AI, machine learning, and scientific computing",
            "JavaScript has a vast ecosystem with npm and modern frameworks like React"
        ]
        
        task_input_1 = AgentInput(
            content={
                "sources": sources_1,
                "synthesis_type": "comparative_analysis",
                "focus": "Compare Python and JavaScript strengths and use cases",
                "approach": "analytical"
            }
        )
        
        start_time = datetime.now()
        task_id_1 = await synthesis_agent.submit_task(task_input_1)
        print("   ⏳ AI synthesizing programming language comparison...")
        
        # Wait for processing
        await asyncio.sleep(20)
        
        try:
            result_1 = await synthesis_agent.get_task_result(task_id_1, timeout=10.0)
            processing_time = (datetime.now() - start_time).total_seconds()
            
            test_1_result = {
                "test_name": "Programming Language Synthesis",
                "status": "SUCCESS",
                "sources_count": len(sources_1),
                "processing_time_seconds": processing_time,
                "confidence_score": result_1.confidence,
                "agent_processing_time": result_1.processing_time,
                "result_content": result_1.content,
                "metadata": result_1.metadata
            }
            
            test_results["tests"].append(test_1_result)
            print(f"   ✅ Success! Confidence: {result_1.confidence:.2f}, Time: {processing_time:.1f}s")
            
            # Show key insights if available
            if isinstance(result_1.content, dict) and "key_insights" in result_1.content:
                insights = result_1.content["key_insights"]
                if isinstance(insights, list) and insights:
                    print(f"   💡 Key insight: {insights[0][:100]}...")
                    
        except Exception as e:
            test_1_result = {
                "test_name": "Programming Language Synthesis",
                "status": "FAILED",
                "error": str(e),
                "sources_count": len(sources_1)
            }
            test_results["tests"].append(test_1_result)
            print(f"   ❌ Failed: {e}")
        
        # Test 2: Technology Trends Synthesis
        print("\n3️⃣ Test 2: Technology Trends Synthesis")
        
        sources_2 = [
            "Artificial Intelligence is transforming industries from healthcare to finance",
            "Cloud computing adoption has accelerated with remote work trends",
            "Cybersecurity has become critical as digital attacks increase",
            "Blockchain technology is finding applications beyond cryptocurrency",
            "Internet of Things (IoT) is connecting everyday devices to the internet",
            "5G networks are enabling faster mobile communications and new applications"
        ]
        
        task_input_2 = AgentInput(
            content={
                "sources": sources_2,
                "synthesis_type": "trend_analysis",
                "focus": "Identify key technology trends and their interconnections",
                "approach": "pattern_recognition"
            }
        )
        
        start_time = datetime.now()
        task_id_2 = await synthesis_agent.submit_task(task_input_2)
        print("   ⏳ AI synthesizing technology trends...")
        
        await asyncio.sleep(20)
        
        try:
            result_2 = await synthesis_agent.get_task_result(task_id_2, timeout=10.0)
            processing_time = (datetime.now() - start_time).total_seconds()
            
            test_2_result = {
                "test_name": "Technology Trends Synthesis",
                "status": "SUCCESS",
                "sources_count": len(sources_2),
                "processing_time_seconds": processing_time,
                "confidence_score": result_2.confidence,
                "agent_processing_time": result_2.processing_time,
                "result_content": result_2.content,
                "metadata": result_2.metadata
            }
            
            test_results["tests"].append(test_2_result)
            print(f"   ✅ Success! Confidence: {result_2.confidence:.2f}, Time: {processing_time:.1f}s")
            
        except Exception as e:
            test_2_result = {
                "test_name": "Technology Trends Synthesis",
                "status": "FAILED",
                "error": str(e),
                "sources_count": len(sources_2)
            }
            test_results["tests"].append(test_2_result)
            print(f"   ❌ Failed: {e}")
        
        # Test 3: Creative Synthesis
        print("\n4️⃣ Test 3: Creative Business Innovation Synthesis")
        
        sources_3 = [
            "Remote work has changed how teams collaborate and communicate",
            "Sustainability is becoming a key business priority for companies",
            "Digital transformation is accelerating across all industries", 
            "Customer experience expectations have risen significantly",
            "Data-driven decision making is becoming standard practice"
        ]
        
        task_input_3 = AgentInput(
            content={
                "sources": sources_3,
                "synthesis_type": "creative_synthesis",
                "focus": "Generate innovative business opportunities from these trends",
                "approach": "creative"
            }
        )
        
        start_time = datetime.now()
        task_id_3 = await synthesis_agent.submit_task(task_input_3)
        print("   ⏳ AI creating innovative synthesis...")
        
        await asyncio.sleep(20)
        
        try:
            result_3 = await synthesis_agent.get_task_result(task_id_3, timeout=10.0)
            processing_time = (datetime.now() - start_time).total_seconds()
            
            test_3_result = {
                "test_name": "Creative Business Synthesis",
                "status": "SUCCESS",
                "sources_count": len(sources_3),
                "processing_time_seconds": processing_time,
                "confidence_score": result_3.confidence,
                "agent_processing_time": result_3.processing_time,
                "result_content": result_3.content,
                "metadata": result_3.metadata
            }
            
            test_results["tests"].append(test_3_result)
            print(f"   ✅ Success! Confidence: {result_3.confidence:.2f}, Time: {processing_time:.1f}s")
            
        except Exception as e:
            test_3_result = {
                "test_name": "Creative Business Synthesis",
                "status": "FAILED", 
                "error": str(e),
                "sources_count": len(sources_3)
            }
            test_results["tests"].append(test_3_result)
            print(f"   ❌ Failed: {e}")
        
        await synthesis_agent.stop()
        
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
        "average_confidence": sum(t["confidence_score"] for t in successful_tests) / len(successful_tests) if successful_tests else 0,
        "average_processing_time": sum(t["processing_time_seconds"] for t in successful_tests) / len(successful_tests) if successful_tests else 0
    }
    
    # Save results to JSON
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"synthesis_tests/synthesis_agent_test_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(test_results, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print(f"\n🎉 SYNTHESIS AGENT TEST COMPLETED!")
    print("=" * 50)
    print(f"📊 Summary:")
    print(f"   • Total tests: {test_results['summary']['total_tests']}")
    print(f"   • Successful: {test_results['summary']['successful_tests']}")
    print(f"   • Failed: {test_results['summary']['failed_tests']}")
    print(f"   • Success rate: {test_results['summary']['success_rate']*100:.1f}%")
    
    if successful_tests:
        print(f"   • Average confidence: {test_results['summary']['average_confidence']:.2f}")
        print(f"   • Average time: {test_results['summary']['average_processing_time']:.1f}s")
    
    print(f"\n💾 Results saved to: {filename}")
    print(f"\n✨ What the Synthesis Agent can do:")
    print("   🔄 Combine multiple data sources into insights")
    print("   📊 Perform comparative analysis")
    print("   🧠 Identify patterns across different sources")
    print("   💡 Generate creative combinations")
    print("   🎯 Focus synthesis on specific topics")
    
    return filename

if __name__ == "__main__":
    asyncio.run(test_synthesis_agent()) 