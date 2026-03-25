# Agent

A tool-calling agentic framework that connects large language models to real-world software — databases, APIs, and calculators — through an autonomous reasoning loop.

Built with **LangGraph** + **Gemini** on the backend and **Next.js** on the frontend.

## What it does

You give the agent a complex, multi-step task. It figures out which tools to call, executes them, reasons about the results, and loops until the task is complete — all streamed to a real-time dashboard.

```
"Compare the weather in Tokyo and Paris, then find the cheapest electronics under $100"
```

The agent will:
1. Call the weather API for both cities
2. Query the database for electronics under $100
3. Synthesize everything into a final response

## Architecture

```
client/ → Next.js dashboard (SSE stream, decision tree, tool logs)
server/ → FastAPI + LangGraph (reasoning loop, tool execution, checkpointing)
```

```
User → POST /api/chat → LangGraph State Machine
                              ↓
                          [Router] ← Gemini + 4 bound tools
                              ↓
                        [Tool Executor] ← Executes tool calls
                              ↓
                          [Router] ← More tools needed? ↺ loop
                              ↓
                        [Human Gate] ← Optional approval
                              ↓
                           [END] → Response
```

## Tools

| Tool | Description |
|------|-------------|
| `query_database` | Read-only SQL against SQLite (travel data, products) |
| `get_weather` | Current weather via OpenWeatherMap (mock fallback) |
| `search_news` | News search via NewsAPI (mock fallback) |
| `calculate` | Safe math expression evaluator |

## Tech Stack

**Server**: Python, FastAPI, LangGraph, LangChain, Gemini, SQLite, SSE  
**Client**: Next.js (App Router), TypeScript, Tailwind CSS, Framer Motion, Lucide

## Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- A [Google AI Studio](https://aistudio.google.com/) API key

### Setup

```bash
# Clone
git clone https://github.com/ShivamVats00/Agent.git
cd Agent

# Server
cd server
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
cp .env.example .env          # Add your GOOGLE_API_KEY
python -m uvicorn app.main:app --reload

# Client (new terminal)
cd client
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) and start giving the agent tasks.

## Key Features

- **Multi-step reasoning** — agent loops until the task is fully resolved
- **Real-time streaming** — SSE streams every node transition and tool call to the UI
- **Human-in-the-loop** — optional approval gate before final response
- **Error recovery** — exponential backoff retry on tool failures
- **State persistence** — SQLite checkpointing for crash recovery

## License

MIT
