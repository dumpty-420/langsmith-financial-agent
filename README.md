# LangSmith Financial Agent 💰

A LangGraph-powered financial analysis agent that performs cash flow and spending analysis using SQL tools, with full observability via LangSmith tracing. Built with Claude Sonnet, FastAPI, and PostgreSQL.

---

## What it does

- Accepts a user ID and runs a complete cash flow and spending analysis
- Uses a LangGraph agent loop with SQL tools to query a PostgreSQL database
- Traces every step (agent calls, tool use, LLM responses) to LangSmith for debugging and observability
- Exposes the analysis via a FastAPI REST API

---

## Tech Stack

| Layer | Technology |
|---|---|
| LLM | Anthropic Claude Sonnet (`claude-sonnet-4-6`) |
| Agent Framework | LangGraph |
| Observability | LangSmith (`@traceable` decorators) |
| API | FastAPI |
| Database | PostgreSQL |
| SQL Tools | Custom LangChain tools (schema, query, checker) |
| Package Manager | uv |

---

## Project Structure & File Explanations

```
langsmith-financial-agent/
├── main.py                          # FastAPI app entry point
├── pyproject.toml                   # Project dependencies (uv)
├── .env.example                     # Environment variable template
├── .gitignore
└── src/
    ├── agents/
    │   └── financial_agent.py       # LangGraph agent with SQL tools
    ├── routes/
    │   └── analysis_route.py        # FastAPI routes for cashflow analysis
    ├── tools/
    │   ├── sql_db_schema.py         # Tool to fetch DB schema
    │   ├── sql_db_query.py          # Tool to run SQL queries
    │   └── sql_db_checker.py        # Tool to validate SQL before execution
    ├── prompts/
    │   └── sql_prompts.py           # System prompt for financial analysis
    └── dtos/
        └── message_dtos.py          # Pydantic request/response models
```

### `main.py`
FastAPI app entry point. Registers the analysis router and starts the server. Loads environment variables at startup.

### `src/agents/financial_agent.py`
The core LangGraph agent. Builds a stateful graph with two nodes — `agent` (Claude) and `tools` (SQL tool node) — connected in a loop. The agent calls tools to explore the database schema, validate SQL, and run queries until it has enough data to produce a final analysis. Every node is decorated with `@traceable` for LangSmith visibility.

### `src/routes/analysis_route.py`
FastAPI router with two endpoints: `POST /api/analysis/cashflow` (accepts a JSON body with `id`) and `GET /api/analysis/cashflow/{id}` (accepts ID as a path parameter). Both call `FinancialAgent.analyze()` and return the result. Also decorated with `@traceable`.

### `src/tools/sql_db_schema.py`
LangChain tool that fetches the database schema — table names, columns, and types. The agent uses this first to understand what data is available before writing queries.

### `src/tools/sql_db_query.py`
LangChain tool that executes SQL queries against the PostgreSQL database and returns results. Used by the agent to retrieve transaction and spending data.

### `src/tools/sql_db_checker.py`
LangChain tool that validates SQL syntax before execution. Prevents the agent from running malformed queries.

### `src/prompts/sql_prompts.py`
Generates the system prompt for the financial analysis, including the user ID and instructions for what to analyze (cash flow, spending patterns, etc.).

### `src/dtos/message_dtos.py`
Pydantic models for request (`AnalysisRequest`) and response (`AnalysisResponse`) validation.

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/dumpty-420/langsmith-financial-agent.git
cd langsmith-financial-agent
```

### 2. Install dependencies

```bash
pip install uv
uv sync
```

### 3. Set up environment variables

Create a `.env` file:

```env
ANTHROPIC_API_KEY=your_anthropic_api_key
LANGCHAIN_API_KEY=your_langsmith_api_key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=Langsmith_Debugging_Anthropic
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=transaction_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=admin
```

Get your LangSmith key from [smith.langchain.com](https://smith.langchain.com) → Settings → API Keys.

### 4. Set up PostgreSQL

Make sure PostgreSQL is running locally with a `transaction_db` database containing transaction data.

### 5. Run the server

```bash
uv run uvicorn main:app --reload
```

Open Swagger UI at `http://localhost:8000/docs`

---

## API Endpoints

### `POST /api/analysis/cashflow`

```json
{
  "id": 1
}
```

### `GET /api/analysis/cashflow/{id}`

```
GET /api/analysis/cashflow/1
```

Both return:

```json
{
  "id": 1,
  "analysis": "Complete cash flow analysis...",
  "status": "completed"
}
```

---

## How the Agent Works

```
User Request (id)
      ↓
FinancialAgent.analyze()
      ↓
LangGraph Loop:
  Agent (Claude) → decides which tool to call
      ↓
  SQL Tools:
    - SqlDbSchemaTool  → understand the database
    - SqlDbCheckerTool → validate SQL
    - SqlDbQueryTool   → run the query
      ↓
  Agent receives results → decides if more queries needed
      ↓
  Final Answer → returned to API
```

---

## LangSmith Observability

Every step is traced to LangSmith automatically:

| Trace Name | What it tracks |
|---|---|
| `analyze_financials` | Full workflow from request to response |
| `agent_call` | Each LLM invocation |
| `should_continue` | Conditional routing decisions |
| `cashflow_analysis_post` | API route call |

View traces at [smith.langchain.com](https://smith.langchain.com) → your project.

---

## Notes

- Requires an active Anthropic API subscription with credits
- LangSmith tracing is optional but recommended for debugging
- PostgreSQL must be running locally before starting the server

---

## Author

Built by [Seerat Chugh](https://github.com/dumpty-420)
