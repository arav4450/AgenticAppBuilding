# Agentic App Building

This repository demonstrates agentic application building.

## Projects & Examples

1. **Simple Calculator Agent using LangGraph**
   - Location: `app/calculator_agent.py`
   - Demonstrates an explicit LangGraph workflow featuring custom arithmetic tools (`add`, `subtract`), state management via `AgentState`, dynamic routing, and execution message sequence inspection.

---

## Getting Started

### Prerequisites

- [uv](https://docs.astral.sh/uv/) package manager installed

### Installation & Setup

1. **Install dependencies**:
   ```bash
   uv sync
   ```

2. **Configure environment variables**:
   Copy `.env.example` to `.env` and provide your `OPENAI_API_KEY`:
   ```bash
   # On Windows PowerShell
   Copy-Item .env.example .env
   ```

### Running the Examples

- **Calculator Agent**:
  ```bash
  uv run python app/calculator_agent.py
  ```

