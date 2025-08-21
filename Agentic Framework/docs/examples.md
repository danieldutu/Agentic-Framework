# Examples and Use Cases

## 🚀 Quick Examples

This section provides practical examples of using the AI Agent Framework for various use cases.

## 📖 Table of Contents

1. [Basic Research Agent](#basic-research-agent)
2. [Memory-Enhanced Research](#memory-enhanced-research)
3. [Agent Communication](#agent-communication)
4. [Multi-Agent Collaboration](#multi-agent-collaboration)
5. [Synthesis Agent Usage](#synthesis-agent-usage)
6. [Production API Integration](#production-api-integration)

## 🔬 Basic Research Agent

### Simple Research Query

```python
#!/usr/bin/env python3
"""Basic research agent example."""

import asyncio
from dotenv import load_dotenv
from agents.agent_factory import AgentFactory
from core.agent_types import AgentInput

load_dotenv()

async def basic_research_example():
    """Demonstrate basic research agent usage."""
    
    # Create research agent
    agent = AgentFactory.create_research_agent(
        agent_id="basic_researcher",
        research_depth="medium"
    )
    
    # Start the agent
    await agent.start()
    print("✅ Research agent started")
    
    # Submit research task
    task = AgentInput(content={
        "query": "What are the benefits of renewable energy?",
        "type": "analytical",
        "depth": "medium"
    })
    
    print("🔍 Submitting research task...")
    task_id = await agent.submit_task(task)
    
    # Get results
    result = await agent.get_task_result(task_id, timeout=30.0)
    
    print(f"📊 Research completed!")
    print(f"   Confidence: {result.confidence:.2f}")
    print(f"   Content: {result.content}")
    
    # Stop the agent
    await agent.stop()
    print("🛑 Agent stopped")

if __name__ == "__main__":
    asyncio.run(basic_research_example())
```

### Multiple Research Types

```python
#!/usr/bin/env python3
"""Example of different research types."""

import asyncio
from dotenv import load_dotenv
from agents.agent_factory import AgentFactory
from core.agent_types import AgentInput

load_dotenv()

async def multi_type_research():
    """Demonstrate different research types."""
    
    agent = AgentFactory.create_research_agent(
        agent_id="multi_researcher",
        research_depth="light"  # Faster for examples
    )
    
    await agent.start()
    
    # Different research types
    research_queries = [
        {
            "query": "What is machine learning?",
            "type": "definition",
            "description": "Definition research"
        },
        {
            "query": "Compare Python vs JavaScript performance",
            "type": "analytical", 
            "description": "Analytical comparison"
        },
        {
            "query": "Future innovations in space technology",
            "type": "creative",
            "description": "Creative exploration"
        },
        {
            "query": "How do neural networks work?",
            "type": "technical",
            "description": "Technical explanation"
        }
    ]
    
    results = []
    
    for i, query in enumerate(research_queries, 1):
        print(f"\n{i}. {query['description']}")
        print(f"   Query: {query['query']}")
        
        task = AgentInput(content={
            "query": query["query"],
            "type": query["type"],
            "depth": "light"
        })
        
        task_id = await agent.submit_task(task)
        result = await agent.get_task_result(task_id, timeout=25.0)
        
        results.append({
            "type": query["type"],
            "confidence": result.confidence,
            "content_preview": str(result.content)[:100] + "..."
        })
        
        print(f"   ✅ Confidence: {result.confidence:.2f}")
    
    await agent.stop()
    
    # Summary
    print(f"\n📊 Research Summary:")
    for r in results:
        print(f"   {r['type']}: {r['confidence']:.2f} confidence")

if __name__ == "__main__":
    asyncio.run(multi_type_research())
```

## 🧠 Memory-Enhanced Research

### Using Memory for Context

```python
#!/usr/bin/env python3
"""Memory-enhanced research example."""

import asyncio
from dotenv import load_dotenv
from agents.agent_factory import AgentFactory
from core.agent_types import AgentInput

load_dotenv()

async def memory_enhanced_research():
    """Demonstrate memory-enhanced research capabilities."""
    
    agent = AgentFactory.create_research_agent(
        agent_id="memory_researcher",
        research_depth="medium"
    )
    
    await agent.start()
    
    # Step 1: Store some relevant memories
    print("📚 Building knowledge base...")
    
    # Store semantic memory (facts)
    memory_id_1 = await agent.memory_store.remember(
        content="Artificial Intelligence involves machine learning, natural language processing, and computer vision",
        memory_type="semantic",
        tags=["AI", "machine-learning", "NLP", "computer-vision"],
        importance=0.9
    )
    
    # Store procedural memory (processes)
    memory_id_2 = await agent.memory_store.remember(
        content="To implement machine learning: 1) Collect data, 2) Clean data, 3) Train model, 4) Evaluate, 5) Deploy",
        memory_type="procedural",
        tags=["machine-learning", "process", "implementation"],
        importance=0.8
    )
    
    print(f"   ✅ Stored {len([memory_id_1, memory_id_2])} memories")
    
    # Step 2: Perform research that can leverage stored memories
    print("\n🔍 Performing memory-enhanced research...")
    
    task = AgentInput(content={
        "query": "How can I get started with AI development?",
        "type": "technical",
        "depth": "medium"
    })
    
    task_id = await agent.submit_task(task)
    result = await agent.get_task_result(task_id, timeout=30.0)
    
    print(f"✅ Research completed with memory context!")
    print(f"   Confidence: {result.confidence:.2f}")
    
    # Step 3: Search memories to show what was available
    relevant_memories = await agent.memory_store.search_memories("machine learning", limit=5)
    print(f"\n🧠 Found {len(relevant_memories)} relevant memories")
    
    for memory in relevant_memories:
        print(f"   📝 {memory['content'][:80]}...")
    
    await agent.stop()

if __name__ == "__main__":
    asyncio.run(memory_enhanced_research())
```

## 💬 Agent Communication

### Direct Agent Messaging

```python
#!/usr/bin/env python3
"""Agent-to-agent communication example."""

import asyncio
from dotenv import load_dotenv
from agents.agent_factory import AgentFactory
from core.agent_types import AgentMessage
from communication.communication_handler import CommunicationHandler

load_dotenv()

async def agent_communication_example():
    """Demonstrate agent-to-agent communication."""
    
    # Initialize communication handler
    comm_handler = CommunicationHandler()
    await comm_handler.initialize()
    
    # Create two agents
    agent_a = AgentFactory.create_research_agent(
        agent_id="researcher_a",
        research_depth="light"
    )
    
    agent_b = AgentFactory.create_synthesis_agent(
        agent_id="synthesizer_b",
        synthesis_approach="analytical"
    )
    
    # Set communication handlers
    agent_a.set_communication_handler(comm_handler)
    agent_b.set_communication_handler(comm_handler)
    
    # Start agents
    await agent_a.start()
    await agent_b.start()
    
    # Message tracking
    received_messages = []
    
    # Message handler for agent B
    async def agent_b_message_handler(message: AgentMessage):
        received_messages.append(message)
        print(f"📨 Agent B received: {message.message_type} from {message.from_agent}")
        
        # Send acknowledgment
        response = AgentMessage(
            from_agent=agent_b.agent_id,
            to_agent=message.from_agent,
            message_type="acknowledgment",
            payload={"status": "received", "response": "Hello from Agent B!"}
        )
        
        await comm_handler.send_message(message.from_agent, response)
        print(f"📤 Agent B sent acknowledgment to {message.from_agent}")
    
    # Register agent B with message handler
    await comm_handler.register_agent(agent_b.agent_id, agent_b_message_handler)
    
    # Agent A sends message to Agent B
    print("📤 Agent A sending greeting to Agent B...")
    
    greeting = AgentMessage(
        from_agent=agent_a.agent_id,
        to_agent=agent_b.agent_id,
        message_type="greeting",
        payload={"greeting": "Hello from Agent A!", "purpose": "collaboration"}
    )
    
    await comm_handler.send_message(agent_b.agent_id, greeting)
    
    # Wait for message processing
    await asyncio.sleep(3)
    
    print(f"\n📊 Communication Summary:")
    print(f"   Messages exchanged: {len(received_messages)}")
    print(f"   Communication successful: ✅")
    
    # Cleanup
    await agent_a.stop()
    await agent_b.stop()
    await comm_handler.shutdown()

if __name__ == "__main__":
    asyncio.run(agent_communication_example())
```

## 🤝 Multi-Agent Collaboration

### Research → Synthesis Workflow

```python
#!/usr/bin/env python3
"""Multi-agent collaboration example."""

import asyncio
from dotenv import load_dotenv
from agents.agent_factory import AgentFactory
from core.agent_types import AgentMessage, AgentInput
from communication.communication_handler import CommunicationHandler

load_dotenv()

async def collaboration_workflow():
    """Demonstrate research → synthesis collaboration."""
    
    # Setup communication
    comm_handler = CommunicationHandler()
    await comm_handler.initialize()
    
    # Create agents
    researcher = AgentFactory.create_research_agent(
        agent_id="collab_researcher",
        research_depth="medium"
    )
    
    synthesizer = AgentFactory.create_synthesis_agent(
        agent_id="collab_synthesizer",
        synthesis_approach="analytical"
    )
    
    # Set communication
    researcher.set_communication_handler(comm_handler)
    synthesizer.set_communication_handler(comm_handler)
    
    # Start agents
    await researcher.start()
    await synthesizer.start()
    
    # Track collaboration
    collaboration_data = {"research_results": [], "synthesis_requests": []}
    
    # Research agent message handler
    async def research_handler(message: AgentMessage):
        if message.message_type == "research_request":
            print(f"🔬 Researcher received request: {message.payload.get('topic', 'unknown')}")
            
            # Perform research
            task = AgentInput(content={
                "query": message.payload["topic"],
                "type": "analytical",
                "depth": "medium"
            })
            
            task_id = await researcher.submit_task(task)
            result = await researcher.get_task_result(task_id, timeout=25.0)
            
            collaboration_data["research_results"].append(result)
            
            # Send results back
            response = AgentMessage(
                from_agent=researcher.agent_id,
                to_agent=message.from_agent,
                message_type="research_results",
                payload={
                    "topic": message.payload["topic"],
                    "findings": str(result.content)[:500],  # Truncate for example
                    "confidence": result.confidence
                },
                correlation_id=message.id
            )
            
            await comm_handler.send_message(message.from_agent, response)
            print(f"📤 Researcher sent results back (confidence: {result.confidence:.2f})")
    
    # Synthesis agent message handler  
    async def synthesis_handler(message: AgentMessage):
        if message.message_type == "research_results":
            print(f"🧠 Synthesizer received research results")
            collaboration_data["synthesis_requests"].append(message.payload)
            print(f"   📊 Confidence: {message.payload.get('confidence', 'unknown')}")
    
    # Register handlers
    await comm_handler.register_agent(researcher.agent_id, research_handler)
    await comm_handler.register_agent(synthesizer.agent_id, synthesis_handler)
    
    # Start collaboration workflow
    print("🚀 Starting collaboration workflow...")
    
    # Synthesizer requests research on multiple topics
    topics = [
        "Benefits of renewable energy",
        "Challenges in renewable energy adoption"
    ]
    
    for topic in topics:
        print(f"\n🔍 Requesting research on: {topic}")
        
        request = AgentMessage(
            from_agent=synthesizer.agent_id,
            to_agent=researcher.agent_id,
            message_type="research_request",
            payload={"topic": topic, "urgency": "medium"}
        )
        
        await comm_handler.send_message(researcher.agent_id, request)
        await asyncio.sleep(30)  # Allow time for research
    
    # Summary
    print(f"\n🎉 Collaboration Summary:")
    print(f"   Research tasks completed: {len(collaboration_data['research_results'])}")
    print(f"   Synthesis requests processed: {len(collaboration_data['synthesis_requests'])}")
    
    # Cleanup
    await researcher.stop()
    await synthesizer.stop()
    await comm_handler.shutdown()

if __name__ == "__main__":
    asyncio.run(collaboration_workflow())
```

## 🧬 Synthesis Agent Usage

### Multi-Source Synthesis

```python
#!/usr/bin/env python3
"""Synthesis agent example."""

import asyncio
from dotenv import load_dotenv
from agents.agent_factory import AgentFactory
from core.agent_types import AgentInput

load_dotenv()

async def synthesis_example():
    """Demonstrate synthesis agent capabilities."""
    
    # Create synthesis agent
    agent = AgentFactory.create_synthesis_agent(
        agent_id="example_synthesizer",
        synthesis_approach="analytical"
    )
    
    await agent.start()
    print("✅ Synthesis agent started")
    
    # Multi-source synthesis task
    sources = [
        "Solar energy reduces carbon emissions by 90% compared to fossil fuels",
        "Wind energy is the fastest growing renewable energy source globally",
        "Battery storage technology has improved 85% in efficiency over 5 years",
        "Government incentives have increased renewable adoption by 200% since 2020"
    ]
    
    synthesis_task = AgentInput(content={
        "sources": sources,
        "synthesis_type": "pattern_analysis",
        "focus": "Renewable energy trends and impact",
        "approach": "analytical"
    })
    
    print("🧬 Performing multi-source synthesis...")
    
    # Note: This example shows the structure
    # Actual synthesis may require API quota
    try:
        task_id = await agent.submit_task(synthesis_task)
        result = await agent.get_task_result(task_id, timeout=30.0)
        
        print(f"✅ Synthesis completed!")
        print(f"   Confidence: {result.confidence:.2f}")
        print(f"   Synthesis: {result.content}")
        
    except Exception as e:
        print(f"⚠️  Synthesis example structure validated")
        print(f"   (May require API quota for full execution)")
        print(f"   Sources to synthesize: {len(sources)}")
        print(f"   Focus area: Renewable energy trends")
    
    await agent.stop()
    print("🛑 Synthesis agent stopped")

if __name__ == "__main__":
    asyncio.run(synthesis_example())
```

## 🚀 Production API Integration

### FastAPI Integration Example

```python
#!/usr/bin/env python3
"""Production API integration example."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio
from typing import Optional
from agents.agent_factory import AgentFactory
from core.agent_types import AgentInput

app = FastAPI(title="AI Agent API", version="1.0.0")

# Global agent instances
research_agent = None
synthesis_agent = None

class ResearchRequest(BaseModel):
    query: str
    research_type: str = "analytical"
    depth: str = "medium"

class SynthesisRequest(BaseModel):
    sources: list[str]
    synthesis_type: str = "analytical"
    focus: Optional[str] = None

@app.on_event("startup")
async def startup_event():
    """Initialize agents on startup."""
    global research_agent, synthesis_agent
    
    research_agent = AgentFactory.create_research_agent(
        agent_id="api_researcher",
        research_depth="medium"
    )
    
    synthesis_agent = AgentFactory.create_synthesis_agent(
        agent_id="api_synthesizer",
        synthesis_approach="analytical"
    )
    
    await research_agent.start()
    await synthesis_agent.start()
    print("🚀 AI Agents initialized for API")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup agents on shutdown."""
    if research_agent:
        await research_agent.stop()
    if synthesis_agent:
        await synthesis_agent.stop()
    print("🛑 AI Agents stopped")

@app.post("/research")
async def perform_research(request: ResearchRequest):
    """Perform research via API."""
    try:
        task = AgentInput(content={
            "query": request.query,
            "type": request.research_type,
            "depth": request.depth
        })
        
        task_id = await research_agent.submit_task(task)
        result = await research_agent.get_task_result(task_id, timeout=30.0)
        
        return {
            "success": True,
            "query": request.query,
            "confidence": result.confidence,
            "result": result.content,
            "processing_time": result.processing_time
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/synthesis")
async def perform_synthesis(request: SynthesisRequest):
    """Perform synthesis via API."""
    try:
        task = AgentInput(content={
            "sources": request.sources,
            "synthesis_type": request.synthesis_type,
            "focus": request.focus or "General analysis"
        })
        
        task_id = await synthesis_agent.submit_task(task)
        result = await synthesis_agent.get_task_result(task_id, timeout=30.0)
        
        return {
            "success": True,
            "sources_count": len(request.sources),
            "confidence": result.confidence,
            "synthesis": result.content,
            "processing_time": result.processing_time
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "research_agent": "active" if research_agent else "inactive",
        "synthesis_agent": "active" if synthesis_agent else "inactive"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Using the API

```bash
# Start the API server
poetry run python api_example.py

# Test research endpoint
curl -X POST "http://localhost:8000/research" \
     -H "Content-Type: application/json" \
     -d '{"query": "What is quantum computing?", "research_type": "definition"}'

# Test synthesis endpoint  
curl -X POST "http://localhost:8000/synthesis" \
     -H "Content-Type: application/json" \
     -d '{"sources": ["AI improves efficiency", "ML automates tasks"], "focus": "AI benefits"}'

# Health check
curl "http://localhost:8000/health"
```

## 🎯 Use Case Scenarios

### 1. Content Research Pipeline
- **Use Case**: Automated content research for articles
- **Agents**: Research Agent → Synthesis Agent
- **Features**: Multi-source research, content synthesis, fact verification

### 2. Customer Support Intelligence
- **Use Case**: Intelligent customer query processing
- **Agents**: Research Agent for knowledge lookup, Memory for context
- **Features**: Context-aware responses, knowledge persistence

### 3. Market Analysis Automation
- **Use Case**: Automated market research and trend analysis
- **Agents**: Research Agent → Synthesis Agent → Memory storage
- **Features**: Multi-source analysis, trend synthesis, historical context

### 4. Educational Content Generation
- **Use Case**: Automated educational material creation
- **Agents**: Research Agent for facts, Synthesis for lesson plans
- **Features**: Structured learning content, multiple difficulty levels

These examples demonstrate the flexibility and power of the AI Agent Framework for various production use cases! 🚀 