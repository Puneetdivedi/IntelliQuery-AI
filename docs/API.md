# API Reference

## Agents

### `SQLAgent`
**Source:** `src/agents/sql_agent.py`

Translates natural language to SQL.

- `generate_sql(question: str) -> str`: Generates SQL query using Llama 3.
- `execute_sql(sql: str) -> DataFrame`: Executes query safely.
- `process_question(question: str) -> dict`: End-to-end processing.

### `VisualizationAgent`
**Source:** `src/agents/visualization_agent.py`

Creates charts from dataframes.

- `analyze_dataframe(df: DataFrame) -> dict`: Returns column types and stats.
- `select_chart_type(df: DataFrame, analysis: dict) -> str`: Heuristic for chart selection.
- `create_visualization(df: DataFrame, question: str) -> dict`: Returns Plotly figure.

### `InsightsAgent`
**Source:** `src/agents/insights_agent.py`

Generates business analysis.

- `generate_insights(df: DataFrame, question: str) -> dict`: Returns structured JSON with key insights, trends, and recommendations.

### `ReportAgent`
**Source:** `src/agents/report_agent.py`

Generates downloadable files.

- `generate_pdf_report(data: dict) -> str`: Returns path to generated PDF.
- `generate_docx_report(data: dict) -> str`: Returns path to generated DOCX.

### `Orchestrator`
**Source:** `src/agents/orchestrator.py`

Main pipeline coordinator.

- `process_query(question: str) -> dict`: Coordinates all agents to answer the user request.

---

## configuration

### `Settings`
**Source:** `src/config/settings.py`

- `GROQ_API_KEY`: API key for Groq Cloud.
- `DATABASE_URL`: Connection string for PostgreSQL.
- `MAX_CONVERSATION_HISTORY`: Limit for context window (default: 10).
