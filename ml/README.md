# Personal Assistant Implementations

This directory contains three different implementations of a personal assistant using different frameworks:

## 1. CrewAI Implementation (`crewai_assistant/`)

This implementation uses CrewAI to create a team of specialized agents that work together:
- Research Specialist: Finds and analyzes information
- Communication Expert: Crafts personalized responses
- Personal Assistant Manager: Coordinates tasks and maintains context

Features:
- Team-based approach with specialized agents
- Built-in tools for web search and Wikipedia queries
- Sequential process flow
- Maintains conversation context

## 2. LangGraph Implementation (`langgraph_assistant/`)

This implementation uses LangGraph to create a graph-based workflow:
- Personality Manager: Maintains consistent personality and context
- Skill Router: Directs requests to appropriate handlers
- Research and Task Management nodes
- Communication Handler: Composes final responses

Features:
- Graph-based state management
- Flexible routing between skills
- Strong typing with Pydantic
- Persistent memory across conversations

## 3. MetaGPT Implementation (`metagpt_assistant/`)

This implementation uses MetaGPT's role-based architecture:
- Sophisticated memory management
- Action-based workflow
- Built-in analysis and response generation
- Preference learning and adaptation

Features:
- Structured memory system
- Action-based architecture
- Automatic context and preference learning
- Detailed request analysis

## Setup and Usage

Each implementation has its own requirements.txt file. To use any implementation:

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install requirements:
```bash
cd <implementation_directory>
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file in each implementation directory with your API keys:
```
OPENAI_API_KEY=your_key_here
```

4. Run the example:
```bash
python personal_assistant.py
```

## Key Differences

- **CrewAI**: Best for tasks requiring multiple specialized agents working together
- **LangGraph**: Best for complex workflows with multiple decision points
- **MetaGPT**: Best for sophisticated memory management and learning from interactions

Each implementation showcases different approaches to building a personal assistant, with their own strengths and use cases. 