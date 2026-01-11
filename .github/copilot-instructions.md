<!-- .github/copilot-instructions.md -->
# Repo-specific Copilot instructions

Purpose
- Provide quick, actionable guidance so AI coding agents are productive in this repo.

Big picture
- This repo contains small Python examples exploring LangGraph (stateful LLM workflows), Pydantic schemas/examples, and simple tool wrappers.
- Key behaviors:
  - `LangGraph.py` composes LLM-driven state graphs using `StateGraph`, `ToolNode`, and an in-memory checkpointer (`InMemorySaver`). The graph alternates between LLM nodes and tool execution paths.
  - `pydantic.py` shows Pydantic v2 patterns: `BaseModel`, `Field`, `@field_validator`, `@model_validator`, and `@computed_field`.
  - `tools.py` defines tools with `@tool` decorators that return dict-like payloads; these are intended to be bound to LLMs via `llm.bind_tools(...)`.

Key files (examples to reference)
- `LangGraph.py` — shows graph/node setup, `llm.bind_tools(tools)`, `ToolNode`, usage of `HumanMessage` and `invoke()`.
- `pydantic.py` — shows validators, computed fields, and model instantiation patterns.
- `tools.py` — shows the `@tool` decorator usage for `calculator` and `get_stock_price` functions.

Environment & run notes
- Expected environment variables (used or implied): `OPENAI_API_KEY` (for OpenAI-backed LLMs), `ALPHAVANTAGE_API_KEY` (for stock price tool if implemented), plus any provider-specific keys referenced by langchain connectors.
- To run examples locally (assumes dependencies installed):
  - `python LangGraph.py`
  - `python pydantic.py`

Dependencies observed (install before running)
- Core libs visible in code: `langgraph`, `langchain`, `pydantic`, `python-dotenv`, `langchain-openai`, `langchain-community`.
- Example install command (adjust to your environment):
  - `pip install langgraph langchain pydantic python-dotenv langchain-openai langchain-community`

Project-specific conventions & patterns
- Graphs and tools
  - Tools are plain Python functions decorated with `@tool` and should return serializable `dict` objects (see `tools.py`).
  - LLMs are often bound to tool lists via `llm.bind_tools(tools)` and invoked with message lists (see `LangGraph.py`).
  - Use `ToolNode` in graphs to route to tool execution; use `tools_condition` or similar to create conditional edges.
- Pydantic usage
  - Validators use `@field_validator` and `@model_validator` patterns; prefer `model_dump(exclude_unset=True)` for serializing instance state as shown in `pydantic.py`.

Integration points
- LLM provider: code imports `ChatOpenAI` / `langchain_openai`—assume chat-based APIs and token/streaming behaviors.
- External tools: `langchain_community.tools.DuckDuckGoSearchRun` and Alpha Vantage (stock) are referenced—implementations may require provider API keys and network access.

Editing guidance for AI agents
- When modifying graphs: keep node function signatures simple and state-typed using TypedDict or Pydantic models (the repo mixes both patterns).
- For new tools: follow `@tool` decorator style in `tools.py`; return a `dict` with predictable keys (e.g., `{ "result": ... }`).
- Preserve the simple invocation patterns used in `LangGraph.py` (message lists, `invoke()`), and avoid changing data-flow shape unless updating all callers.

Examples (copyable)
- Bind tools to LLM and invoke:
```
llm_with_tools = llm.bind_tools(tools)
out = chatbot.invoke({"messages": [HumanMessage(content":"What is 2*3?")]})
```
- Pydantic computed-field pattern:
```
class Student(BaseModel):
    ...
    @computed_field
    @property
    def bmi(self) -> float:
        return round(self.weight / (self.height**2), 2)
```

If anything in these examples is out-of-date or you want broader coverage (tests, a requirements file, or run scripts), tell me which area to expand first.

-- End of file
