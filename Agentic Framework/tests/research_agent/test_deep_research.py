#!/usr/bin/env python3
"""Test Deep Research functionality specifically with JSON output."""

import asyncio
import json
import os
from datetime import datetime
from dotenv import load_dotenv
from agents.agent_factory import AgentFactory
from core.agent_types import AgentInput

load_dotenv()

async def test_deep_research():
    """Test Deep Research capabilities and save results to JSON."""
    print("🔍 TESTING DEEP RESEARCH FUNCTIONALITY")
    print("=" * 50)
    
    # Create output directory
    os.makedirs("deep_research_tests", exist_ok=True)
    
    test_results = {
        "test_name": "Deep Research Functionality",
        "timestamp": datetime.now().isoformat(),
        "tests": []
    }
    
    try:
        # Test different research depths
        research_depths = ["light", "medium", "deep"]
        
        for depth in research_depths:
            print(f"\n📊 Testing {depth.upper()} Research Depth")
            
            try:
                # Create agent with specific depth
                agent = AgentFactory.create_research_agent(
                    agent_id=f"{depth}_researcher",
                    research_depth=depth,
                    max_search_results=5
                )
                
                await agent.start()
                await asyncio.sleep(2)
                
                # Submit research task
                task_input = AgentInput(
                    content={
                        "query": "What are the latest developments in quantum computing?",
                        "type": "analytical",
                        "depth": depth,
                        "focus": "recent_developments"
                    }
                )
                
                start_time = datetime.now()
                task_id = await agent.submit_task(task_input)
                print(f"   ⏳ AI conducting {depth} research...")
                
                # Wait based on depth
                wait_times = {"light": 15, "medium": 20, "deep": 30}
                await asyncio.sleep(wait_times[depth])
                
                try:
                    result = await agent.get_task_result(task_id, timeout=15.0)
                    processing_time = (datetime.now() - start_time).total_seconds()
                    
                    # Analyze content depth
                    content_analysis = {}
                    if isinstance(result.content, dict):
                        content_analysis = {
                            "has_summary": "summary" in result.content,
                            "has_key_findings": "key_findings" in result.content,
                            "has_analysis": "analysis" in result.content,
                            "content_length": len(str(result.content)),
                            "confidence_score": result.confidence
                        }
                        
                        if "key_findings" in result.content:
                            findings = result.content["key_findings"]
                            if isinstance(findings, list):
                                content_analysis["findings_count"] = len(findings)
                    
                    test_result = {
                        "test_name": f"{depth.title()} Research",
                        "status": "SUCCESS",
                        "research_depth": depth,
                        "processing_time_seconds": processing_time,
                        "confidence_score": result.confidence,
                        "agent_processing_time": result.processing_time,
                        "content_analysis": content_analysis,
                        "result_preview": str(result.content)[:300] + "..." if len(str(result.content)) > 300 else str(result.content)
                    }
                    
                    test_results["tests"].append(test_result)
                    print(f"   ✅ Success! Confidence: {result.confidence:.2f}, Time: {processing_time:.1f}s")
                    print(f"   📄 Content length: {content_analysis.get('content_length', 0)} characters")
                    
                except Exception as e:
                    test_result = {
                        "test_name": f"{depth.title()} Research",
                        "status": "FAILED",
                        "research_depth": depth,
                        "error": str(e)
                    }
                    test_results["tests"].append(test_result)
                    print(f"   ❌ Failed: {e}")
                
                await agent.stop()
                
            except Exception as e:
                test_result = {
                    "test_name": f"{depth.title()} Research Setup",
                    "status": "FAILED", 
                    "research_depth": depth,
                    "error": str(e)
                }
                test_results["tests"].append(test_result)
                print(f"   ❌ Setup failed: {e}")
        
        # Test different research types with medium depth
        print(f"\n🔬 Testing Different Research Types")
        
        research_types = [
            ("technical", "Explain the principles of machine learning algorithms"),
            ("analytical", "Compare different cloud computing platforms"),
            ("creative", "What are innovative applications of blockchain technology?"),
            ("definition", "What is artificial neural networks?")
        ]
        
        for research_type, query in research_types:
            print(f"\n📝 Testing {research_type.upper()} Research")
            
            try:
                agent = AgentFactory.create_research_agent(
                    agent_id=f"{research_type}_researcher",
                    research_depth="medium"
                )
                
                await agent.start()
                await asyncio.sleep(2)
                
                task_input = AgentInput(
                    content={
                        "query": query,
                        "type": research_type,
                        "depth": "medium"
                    }
                )
                
                start_time = datetime.now()
                task_id = await agent.submit_task(task_input)
                print(f"   ⏳ AI conducting {research_type} analysis...")
                
                await asyncio.sleep(20)
                
                try:
                    result = await agent.get_task_result(task_id, timeout=10.0)
                    processing_time = (datetime.now() - start_time).total_seconds()
                    
                    test_result = {
                        "test_name": f"{research_type.title()} Research Type",
                        "status": "SUCCESS",
                        "research_type": research_type,
                        "query": query,
                        "processing_time_seconds": processing_time,
                        "confidence_score": result.confidence,
                        "content_length": len(str(result.content)),
                        "has_structured_output": isinstance(result.content, dict)
                    }
                    
                    test_results["tests"].append(test_result)
                    print(f"   ✅ Success! Confidence: {result.confidence:.2f}")
                    
                except Exception as e:
                    test_result = {
                        "test_name": f"{research_type.title()} Research Type",
                        "status": "FAILED",
                        "research_type": research_type,
                        "error": str(e)
                    }
                    test_results["tests"].append(test_result)
                    print(f"   ❌ Failed: {e}")
                
                await agent.stop()
                
            except Exception as e:
                print(f"   ❌ Setup failed: {e}")
        
    except Exception as e:
        print(f"❌ Overall test failed: {e}")
        test_results["overall_error"] = str(e)
    
    # Calculate summary statistics
    successful_tests = [t for t in test_results["tests"] if t["status"] == "SUCCESS"]
    failed_tests = [t for t in test_results["tests"] if t["status"] == "FAILED"]
    
    # Analyze by depth
    depth_analysis = {}
    for test in successful_tests:
        if "research_depth" in test:
            depth = test["research_depth"]
            if depth not in depth_analysis:
                depth_analysis[depth] = {"count": 0, "avg_time": 0, "avg_confidence": 0}
            depth_analysis[depth]["count"] += 1
            depth_analysis[depth]["avg_time"] += test.get("processing_time_seconds", 0)
            depth_analysis[depth]["avg_confidence"] += test.get("confidence_score", 0)
    
    for depth in depth_analysis:
        count = depth_analysis[depth]["count"]
        if count > 0:
            depth_analysis[depth]["avg_time"] /= count
            depth_analysis[depth]["avg_confidence"] /= count
    
    test_results["summary"] = {
        "total_tests": len(test_results["tests"]),
        "successful_tests": len(successful_tests),
        "failed_tests": len(failed_tests),
        "success_rate": len(successful_tests) / len(test_results["tests"]) if test_results["tests"] else 0,
        "depth_analysis": depth_analysis,
        "features_tested": [
            "light_research",
            "medium_research", 
            "deep_research",
            "technical_research",
            "analytical_research",
            "creative_research",
            "definition_research"
        ]
    }
    
    # Save results to JSON
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"deep_research_tests/deep_research_test_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(test_results, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print(f"\n🎉 DEEP RESEARCH TEST COMPLETED!")
    print("=" * 50)
    print(f"📊 Summary:")
    print(f"   • Total tests: {test_results['summary']['total_tests']}")
    print(f"   • Successful: {test_results['summary']['successful_tests']}")
    print(f"   • Failed: {test_results['summary']['failed_tests']}")
    print(f"   • Success rate: {test_results['summary']['success_rate']*100:.1f}%")
    
    if depth_analysis:
        print(f"\n📈 Research Depth Analysis:")
        for depth, stats in depth_analysis.items():
            print(f"   • {depth.title()}: {stats['count']} tests, {stats['avg_time']:.1f}s avg, {stats['avg_confidence']:.2f} confidence")
    
    print(f"\n💾 Results saved to: {filename}")
    print(f"\n🔍 What Deep Research can do:")
    print("   📊 Multiple research depths (light/medium/deep)")
    print("   🔬 Different research types (technical/analytical/creative/definition)")
    print("   ⏱️ Longer processing for deeper analysis")
    print("   📈 Higher content quality with deeper research")
    print("   🎯 Specialized analysis for different query types")
    
    return filename

if __name__ == "__main__":
    asyncio.run(test_deep_research()) 