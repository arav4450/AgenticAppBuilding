# Agentic App Building

This repository demonstrates agentic application building, progressing from local tool-calling workflows to decoupled tool services using the **Model Context Protocol (MCP)** pattern.

---

## Projects & Examples

### 1. Simple Calculator Agent using LangGraph
- **Location**: [`app/calculator_agent.py`](app/calculator_agent.py)
- **Overview**: Demonstrates an explicit LangGraph workflow featuring local arithmetic tools (`add`, `subtract`), state management via `AgentState`, conditional tool routing, and execution message sequence inspection.

### 2. HTTP Math MCP Demo (Client & Server)
- **Locations**:
  - **MCP Server**: [`app/http_math_server.py`](app/http_math_server.py)
  - **MCP Client**: [`app/http_math_client.py`](app/http_math_client.py)
- **Overview**: Demonstrates a lightweight, HTTP-based Model Context Protocol (MCP) architecture:
  - **`http_math_server.py`**: Runs a zero-dependency HTTP server on `http://localhost:8001/mcp` that accepts MCP-formatted JSON envelopes (`context` + `payload`), safely parses and evaluates arithmetic expressions (`+`, `-`, `*`, `/`, `^`) using Python's `ast` module (preventing unsafe `eval()` execution), and returns structured JSON responses.
  - **`http_math_client.py`**: Acts as an MCP client that constructs standardized JSON request envelopes (`request_id`, `role`, `content`), sends `POST` requests to the server, and handles both valid results and error states (e.g., division by zero).

---

## Why MCP is Required & Where the LLM Fits In

### Why is MCP Required?
In the first example (`calculator_agent.py`), the tools (`add`, `subtract`) are **tightly coupled** inside the same script as the agent. As agentic systems scale, this approach creates bottlenecks that MCP solves:

1. **Standardized Communication (The "USB-C for AI")**: Without a standard protocol, connecting $N$ different LLM frameworks to $M$ external tools requires custom wrapper code for every pair. MCP defines a consistent JSON request/response envelope (`context` and `payload`) so any agent can talk to any tool server uniformly.
2. **Decoupling & Reusability**: By hosting the math evaluator as a standalone service (`http_math_server.py`), multiple agents (built in LangGraph, CrewAI, AutoGen, or IDE assistants) can invoke the exact same server over HTTP without duplicating tool logic.
3. **Security & Process Isolation**: Executing expressions, database queries, or system commands directly inside the agent process is risky. The MCP server isolates execution behind a dedicated boundary and uses safe AST parsing (`ast.parse`) rather than raw Python `eval()`.
4. **Deterministic Execution vs. Probabilistic LLMs**: LLMs predict tokens probabilistically and frequently hallucinate on multi-step or complex math. Offloading calculations to a deterministic MCP server guarantees 100% mathematical accuracy.



## Getting Started

### Prerequisites

- [uv](https://docs.astral.sh/uv/) package manager installed

### Installation & Setup

1. **Install dependencies**:
   ```powershell
   uv sync
   ```

2. **Configure environment variables**:
   Copy `.env.example` to `.env` and provide your `OPENAI_API_KEY`:
   ```powershell
   Copy-Item .env.example .env
   ```

---

## Running the Examples

### 1. Calculator Agent (LangGraph)
```powershell
uv run python app/calculator_agent.py
```

### 2. HTTP Math MCP Demo
Open **two terminals**:

**Terminal 1 — Start the MCP Math Server**:
```powershell
uv run python app/http_math_server.py
```
*(Listens at `http://localhost:8001/mcp`)*

**Terminal 2 — Run the MCP Math Client**:
```powershell
uv run python app/http_math_client.py
```
