# Getting Started Guide

## 🚀 5-Minute Quick Start

Get your AI Agent Framework running in minutes!

## Prerequisites

- **Python 3.9+**
- **Redis** (for memory and communication)
- **Gemini API Key** (Google AI)
- **Poetry** (dependency management)

## Step 1: Environment Setup

```bash
# Clone the repository
git clone <repository-url>
cd agentic_common_repo

# Install Poetry (if not installed)
curl -sSL https://install.python-poetry.org | python3 -

# Create virtual environment and install dependencies
poetry install
poetry shell
```

## Step 2: Redis Setup

```bash
# Start Redis with Docker (recommended)
docker run -d -p 6379:6379 --name ai-agent-redis redis:7-alpine

# Or install Redis locally
# brew install redis  # macOS
# sudo apt install redis-server  # Ubuntu
```

## Step 3: Configuration

Create `.env` file in the project root:

```env
# Gemini AI Configuration
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-flash

# Redis Configuration  
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Framework Configuration
LOG_LEVEL=INFO
ENVIRONMENT=development
```

## Step 4: Test the Framework

```bash
# Run comprehensive tests
poetry run python run_tests.py

# Or test specific components
poetry run python run_tests.py research
poetry run python run_tests.py memory
```

## Step 5: First Agent Usage

Create a simple test script:

```python
# test_my_agent.py
import asyncio
from dotenv import load_dotenv
from agents.agent_factory import AgentFactory
from core.agent_types import AgentInput

load_dotenv()

async def main():
    # Create research agent
    agent = AgentFactory.create_research_agent(
        agent_id="my_first_agent",
        research_depth="medium"
    )
    
    # Start the agent
    await agent.start()
    
    # Submit a research task
    task = AgentInput(content={
        "query": "What is machine learning?",
        "type": "definition",
        "depth": "medium"
    })
    
    task_id = await agent.submit_task(task)
    result = await agent.get_task_result(task_id, timeout=30.0)
    
    print(f"✅ Research completed!")
    print(f"📊 Confidence: {result.confidence}")
    print(f"📄 Result: {result.content}")
    
    # Stop the agent
    await agent.stop()

if __name__ == "__main__":
    asyncio.run(main())
```

Run it:
```bash
poetry run python test_my_agent.py
```

## 🎉 Success!

If you see research results, congratulations! Your AI Agent Framework is working.

## What's Next?

1. **[Explore Examples](examples.md)** - See more use cases
2. **[Read Architecture](architecture.md)** - Understand the system
3. **[Test Features](testing-guide.md)** - Run comprehensive tests
4. **[Deploy to Production](deployment.md)** - Scale your agents

## Troubleshooting

### Common Issues:

**Redis Connection Error:**
```bash
# Check if Redis is running
docker ps | grep redis
# Restart if needed
docker restart ai-agent-redis
```

**Gemini API Error:**
```bash
# Verify your API key
echo $GEMINI_API_KEY
# Get key from: https://makersuite.google.com/app/apikey
```

**Import Errors:**
```bash
# Ensure virtual environment is active
poetry shell
# Reinstall dependencies
poetry install
```

## Framework Components

After setup, you'll have access to:

- **🔬 Research Agent**: Multi-type research with confidence scoring
- **🧠 Synthesis Agent**: Multi-source data combination
- **💾 Memory System**: Redis-backed persistent memory
- **💬 Communication**: Agent-to-agent messaging
- **🔄 Collaboration**: Multi-agent workflows
- **📊 JSON APIs**: Structured data exchange
- **🧪 Test Suite**: Comprehensive testing framework

Ready to build amazing AI agents! 🚀 