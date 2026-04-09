# 🤖 Agentic Workflow Orchestration Framework

A production-grade tool-calling agentic framework powered by **LangGraph + Gemini**. Features multi-step reasoning, memory management, human-in-the-loop approval, and exponential backoff error recovery.

## Architecture

```
User Task → FastAPI → LangGraph State Machine
                          ↓
                      [Router] ← Gemini LLM with bound tools
                          ↓
                    [Tool Executor] ← DB, Weather, News, Calculator
                          ↓
                      [Router] ← Decides: more tools needed? 
                          ↓                    ↺ loops back
                    [Human Gate] ← Optional approval checkpoint
                          ↓
                      [Response] → Final answer
```

## Features

- **Multi-Step Reasoning**: Agent autonomously chains 3+ tool calls to complete complex tasks
- **4 Built-in Tools**: Database queries, Weather API, News search, Calculator
- **Memory Management**: SQLite checkpointing preserves state across sessions
- **Human-in-the-Loop**: Interrupt-based approval gates with checkpoint resume
- **Error Recovery**: Exponential backoff (1s→2s→4s) with structured error reporting
- **Real-time Streaming**: SSE events for node transitions, tool calls, and reasoning
- **Thread Management**: Multiple concurrent conversations with persistent state

## Quick Start

```bash
# 1. Install dependencies
cd backend
pip install -r requirements.txt

# 2. Configure API key
copy .env.example .env
# Edit .env and add your GOOGLE_API_KEY (Gemini)

# 3. Run the server
python -m app.main
# or
uvicorn app.main:app --reload --port 8000
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/chat` | Submit a task (sync response) |
| `GET` | `/api/chat/stream/{thread_id}?message=...` | Stream agent execution (SSE) |
| `POST` | `/api/approve/{thread_id}` | Resume paused graph with approval |
| `GET` | `/api/threads` | List all active threads |
| `GET` | `/api/health` | Health check |

## Example Task

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Compare the current weather in Tokyo, London, and New York, check the database for the best travel month for each, and recommend where to go in March."
  }'
```

This triggers **7+ sequential tool calls**:
1. Weather API × 3 cities
2. Database query for travel data
3. Synthesis and final recommendation

## Tech Stack

- **Backend**: FastAPI + Python 3.11+
- **Agent Framework**: LangGraph (state machine with cycles)
- **LLM**: Google Gemini (via langchain-google-genai)
- **State Persistence**: SQLite (langgraph-checkpoint-sqlite)
- **Streaming**: Server-Sent Events (sse-starlette)
- **Error Recovery**: Custom exponential backoff decorator
