#!/usr/bin/env python3
"""Simple test to verify Gemini integration works."""

import asyncio
import os
from dotenv import load_dotenv
from agents.agent_factory import AgentFactory
from core.agent_types import AgentInput

# Load environment variables
load_dotenv()

async def test_simple_research():
    """Test a simple research query with proper timing."""
    print("🔬 Testing Simple Research with Gemini...")
    
    try:
        # Create research agent
        research_agent = AgentFactory.create_research_agent(
            agent_id="simple_test",
            research_depth="light",
        )
        print("✅ Agent created")
        
        # Start agent
        await research_agent.start()
        print("✅ Agent started")
        
        # Give the agent a moment to start its processing loop
        await asyncio.sleep(1)
        
        # Create simple input
        task_input = AgentInput(
            content={
                "query": "What is Python programming?",
                "type": "definition",
                "depth": "light"
            }
        )
        print("📝 Task created")
        
        # Submit task
        task_id = await research_agent.submit_task(task_input)
        print(f"✅ Task submitted: {task_id}")
        
        # Wait a bit more for processing to begin
        await asyncio.sleep(2)
        
        # Get result with extended timeout
        print("⏳ Getting result...")
        result = await research_agent.get_task_result(task_id, timeout=90.0)
        
        print(f"\n🎉 SUCCESS! Task completed")
        print(f"📊 Confidence: {result.confidence}")
        print(f"⏱️  Time: {result.processing_time:.2f}s")
        print(f"📄 Content type: {type(result.content)}")
        
        # Show some of the result
        if isinstance(result.content, dict):
            for key, value in list(result.content.items())[:3]:
                print(f"  {key}: {str(value)[:100]}...")
        else:
            print(f"📋 Result: {str(result.content)[:200]}...")
        
        # Stop agent
        await research_agent.stop()
        print("✅ Agent stopped")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    print("🚀 Simple AI Agent Test")
    print("=" * 40)
    
    # Check API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ No GEMINI_API_KEY found")
        return
    
    print(f"✅ API key found (ends with: ...{api_key[-4:]})")
    
    # Run test
    success = await test_simple_research()
    
    if success:
        print("\n🎉 Framework is working perfectly!")
        print("🔥 You can now use the full AI Agent Framework!")
    else:
        print("\n❌ Test failed - check the error above")

if __name__ == "__main__":
    asyncio.run(main()) 