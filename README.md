# AI Agent Framework

A production-ready AI agent framework for hackathons and rapid prototyping, featuring Research and Synthesis agents powered by Google Gemini AI.


## 🚀 Quick Start

Get agents running in under 5 minutes:

```bash
# 1. Clone and setup
git clone <repository-url>
cd ai-agent-framework

# 2. Install dependencies
pip install poetry
poetry install

# 3. Configure environment
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# 4. Start Redis (for communication and memory)
docker run -d -p 6379:6379 redis:latest

# 5. Run examples
poetry run python examples/basic_research_example.py
```

## 📋 Requirements

- Python 3.9+
- Redis (for communication and memory)
- Google Gemini API key
- Docker (optional, for containerized deployment)

## 🏗️ Architecture

### Core Components

```
ai-agent-framework/
├── agents/                 # Agent implementations
│   ├── research_agent.py   # Research specialist
│   ├── synthesis_agent.py  # Analysis specialist  
│   └── agent_factory.py    # Agent creation factory
├── core/                   # Base framework
│   ├── base_agent.py       # Abstract agent base
│   ├── agent_types.py      # Data models
│   └── exceptions.py       # Error handling
├── communication/          # Inter-agent messaging
│   ├── message_broker.py   # Message infrastructure
│   └── communication_handler.py  # Agent communication
├── memory/                 # Agent memory system
│   ├── memory_handler.py   # Memory storage
│   └── memory_store.py     # Simplified interface
├── config/                 # Configuration management
│   ├── settings.py         # App settings
│   └── gemini_config.py    # Gemini AI setup
└── examples/               # Working demonstrations
```

### Agent Types

**Research Agent**
- 🔍 Information gathering and research
- 📊 Data analysis and source evaluation
- 🧠 Memory-based context retrieval
- 🔗 Extensible for web search APIs

**Synthesis Agent** 
- 🧩 Multi-source information synthesis
- 📋 Analysis and insight generation
- 💡 Pattern recognition and recommendations
- 🎯 Customizable synthesis styles

## 🛠️ Installation

### Option 1: Poetry (Recommended)

```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install

# Activate environment
poetry shell
```

### Option 2: pip

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### Option 3: Docker

```bash
# Build container
docker build -t ai-agent-framework .

# Run with environment variables
docker run -e GEMINI_API_KEY=your_key ai-agent-framework
```

## ⚙️ Configuration

### Environment Variables

Create `.env` file from `.env.example`:

```bash
# Required
GEMINI_API_KEY=your_gemini_api_key_here

# Optional (with defaults)
GEMINI_MODEL=gemini-pro
GEMINI_TEMPERATURE=0.7
REDIS_URL=redis://localhost:6379/0
LOG_LEVEL=INFO
```

### Configuration Files

```python
from config.settings import get_settings

settings = get_settings()
print(f"Using model: {settings.gemini_model}")
```

## 🎯 Usage Examples

### Basic Research Agent

```python
import asyncio
from agents.agent_factory import AgentFactory
from core.agent_types import AgentInput

async def main():
    # Create research agent
    agent = AgentFactory.create_research_agent(
        agent_id="researcher",
        research_depth="medium"
    )
    
    await agent.start()
    
    # Submit research task
    research_input = AgentInput(
        content={
            "query": "What are the latest AI developments?",
            "type": "trend",
            "depth": "medium"
        }
    )
    
    task_id = await agent.submit_task(research_input)
    result = await agent.get_task_result(task_id)
    
    print(f"Research findings: {result.content}")
    
    await agent.stop()

asyncio.run(main())
```

### Agent Collaboration

```python
import asyncio
from agents.agent_factory import AgentFactory
from communication.communication_handler import CommunicationHandler

async def collaboration_example():
    # Setup communication
    comm_handler = CommunicationHandler()
    await comm_handler.initialize()
    
    # Create agent pair
    research_agent, synthesis_agent = AgentFactory.create_agent_pair(
        base_id="collab_demo"
    )
    
    # Configure communication
    research_agent.set_communication_handler(comm_handler)
    synthesis_agent.set_communication_handler(comm_handler)
    
    await research_agent.start()
    await synthesis_agent.start()
    
    # Research phase
    research_input = AgentInput(
        content={"query": "AI ethics principles", "type": "technical"}
    )
    task_id = await research_agent.submit_task(research_input)
    research_result = await research_agent.get_task_result(task_id)
    
    # Synthesis phase
    synthesis_input = AgentInput(
        content={
            "topic": "AI Ethics Analysis",
            "sources": [research_result.content],
            "type": "analysis"
        }
    )
    task_id = await synthesis_agent.submit_task(synthesis_input)
    synthesis_result = await synthesis_agent.get_task_result(task_id)
    
    print(f"Final analysis: {synthesis_result.content}")
    
    # Cleanup
    await research_agent.stop()
    await synthesis_agent.stop()
    await comm_handler.shutdown()

asyncio.run(collaboration_example())
```

### Memory Integration

```python
from memory.memory_store import MemoryStore

async def memory_example():
    memory = MemoryStore("my_agent")
    
    # Store different types of memories
    conversation_id = await memory.remember_conversation([
        {"role": "user", "content": "Explain machine learning"},
        {"role": "assistant", "content": "ML is a subset of AI..."}
    ])
    
    fact_id = await memory.remember_fact(
        "Python is a programming language",
        source="Programming guide"
    )
    
    procedure_id = await memory.remember_procedure(
        "Code Review Process",
        ["Read code", "Check logic", "Test functionality", "Approve"]
    )
    
    # Search memories
    results = await memory.search_memories(query="machine learning")
    important = await memory.get_important_memories(min_importance=0.8)
    
    print(f"Found {len(results)} relevant memories")
    print(f"Found {len(important)} important memories")
```

## 🔧 Extending the Framework

### Creating Custom Agents

```python
from core.base_agent import BaseAgent
from core.agent_types import AgentCapability, AgentInput, AgentOutput

class CustomAgent(BaseAgent):
    def get_capabilities(self):
        return [AgentCapability.ANALYSIS, AgentCapability.REASONING]
    
    async def process(self, input_data: AgentInput) -> AgentOutput:
        # Implement custom processing logic
        result = await self.custom_processing(input_data.content)
        
        return AgentOutput(
            content=result,
            source_agent=self.agent_id,
            confidence=0.85
        )
    
    async def custom_processing(self, content):
        # Your custom logic here
        return {"processed": content}

# Register with factory
from agents.agent_factory import AgentFactory
AgentFactory.register_agent_type("custom", CustomAgent)

# Use the custom agent
agent = AgentFactory.create_agent("custom", "my_custom_agent")
```

### Adding Communication Channels

```python
from communication.message_broker import MessageBroker

class WebSocketBroker(MessageBroker):
    async def publish(self, channel: str, message: AgentMessage):
        # Implement WebSocket publishing
        pass
    
    async def subscribe(self, channel: str, handler):
        # Implement WebSocket subscription
        pass

# Use custom broker
from communication.communication_handler import CommunicationHandler
comm_handler = CommunicationHandler(WebSocketBroker())
```

## 📊 Monitoring & Debugging

### Agent Metrics

```python
# Get agent performance metrics
metrics = agent.get_metrics()
print(f"Tasks processed: {metrics['tasks_processed']}")
print(f"Average time: {metrics['total_processing_time'] / metrics['tasks_processed']}")
```

### Communication Monitoring

```python
# Get communication status
status = comm_handler.get_status()
print(f"Active agents: {status['registered_agents']}")
print(f"Message history: {status['message_history_size']}")

# Get message history
history = await comm_handler.get_message_history(limit=10)
```

### Memory Statistics

```python
# Get memory usage statistics
stats = await memory_store.get_memory_stats()
print(f"Total memories: {stats['total_memories']}")
print(f"Memory types: {stats['memory_types']}")
```

## 🧪 Testing

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=agents --cov=core --cov=communication --cov=memory

# Run specific test category
poetry run pytest tests/test_agents.py
poetry run pytest tests/test_communication.py
poetry run pytest tests/test_memory.py
```

## 🐳 Docker Deployment

### Single Container

```dockerfile
# Dockerfile included in repo
docker build -t ai-agent-framework .
docker run -p 8000:8000 ai-agent-framework
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'
services:
  agents:
    build: .
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

```bash
docker-compose up -d
```

## 🔍 API Documentation

FastAPI automatically generates documentation:

```bash
# Start the API server
poetry run uvicorn main:app --reload

# View documentation
open http://localhost:8000/docs
```

## 🤝 Contributing

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Make changes** with tests
4. **Run tests**: `poetry run pytest`
5. **Run linting**: `poetry run black . && poetry run flake8`
6. **Commit changes**: `git commit -m 'Add amazing feature'`
7. **Push branch**: `git push origin feature/amazing-feature`
8. **Open Pull Request**

### Development Setup

```bash
# Install development dependencies
poetry install --with dev

# Setup pre-commit hooks
poetry run pre-commit install

# Run code formatting
poetry run black .
poetry run isort .

# Type checking
poetry run mypy .
```

## 📚 Documentation

- **[Setup Guide](docs/SETUP.md)**: Detailed setup instructions
- **[Architecture](docs/ARCHITECTURE.md)**: System design and components
- **[API Reference](docs/API.md)**: Complete API documentation
- **[Examples](docs/EXAMPLES.md)**: More usage examples
- **[Contributing](docs/CONTRIBUTING.md)**: Development guidelines

## 🔧 Troubleshooting

### Common Issues

**Redis Connection Failed**
```bash
# Start Redis
docker run -d -p 6379:6379 redis:latest
# or
redis-server
```

**Gemini API Errors**
```bash
# Check API key
echo $GEMINI_API_KEY
# Verify key at https://makersuite.google.com/app/apikey
```

**Memory Import Errors**
```python
# Check Python version
python --version  # Should be 3.9+
```

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
export DEBUG=true

# Run with verbose output
poetry run python examples/basic_research_example.py
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Google Gemini AI for language model capabilities
- Redis for communication and memory infrastructure  
- FastAPI for API framework
- Pydantic for data validation
- The open-source community for inspiration and tools

## 🔗 Related Projects

- [LangChain](https://github.com/hwchase17/langchain) - LLM application framework
- [AutoGPT](https://github.com/Significant-Gravitas/Auto-GPT) - Autonomous AI agents
- [CrewAI](https://github.com/joaomdmoura/crewAI) - Multi-agent collaboration

---

**Built for hackathons, designed for production** 🚀

For questions, issues, or contributions, please open an issue or reach out to the maintainers. 
