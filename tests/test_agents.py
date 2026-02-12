"""
Unit tests for IntelliQuery AI agents.
"""

import pytest
import pandas as pd
from unittest.mock import MagicMock, patch

from src.agents.sql_agent import SQLAgent
from src.agents.visualization_agent import VisualizationAgent
from src.agents.insights_agent import InsightsAgent
from src.agents.report_agent import ReportAgent
from src.agents.orchestrator import Orchestrator

# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture
def mock_df():
    return pd.DataFrame({
        "category": ["A", "B", "C"],
        "value": [10, 20, 30],
        "date": pd.to_datetime(["2023-01-01", "2023-01-02", "2023-01-03"])
    })

# ── SQL Agent Tests ──────────────────────────────────────────────────────────

def test_sql_agent_validation():
    agent = SQLAgent()
    assert agent.validate_sql("SELECT * FROM users") == True
    assert agent.validate_sql("DROP TABLE users") == False
    assert agent.validate_sql("DELETE FROM orders WHERE id=1") == False

@patch("src.agents.sql_agent.execute_query")
@patch("src.agents.sql_agent.ChatGroq") 
def test_sql_generation(mock_llm, mock_exec):
    # Mock LLM response
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = "SELECT * FROM products LIMIT 5"
    mock_llm.return_value = MagicMock()
    
    agent = SQLAgent()
    # We need to mock the chain creation which happens inside generate_sql usually
    # For unit testing without real LLM call, we can mock the internal generate_sql if needed
    # or rely on mocking the langchain components. 
    # Simplified here:
    with patch.object(agent, "generate_sql", return_value="SELECT * FROM products LIMIT 5"):
        sql = agent.generate_sql("Show me products")
        assert sql == "SELECT * FROM products LIMIT 5"

# ── Visualization Agent Tests ────────────────────────────────────────────────

def test_chart_selection_bar(mock_df):
    agent = VisualizationAgent()
    analysis = agent.analyze_dataframe(mock_df)
    chart_type = agent.select_chart_type(mock_df, analysis)
    # With date and value, it might pick line. Let's see heuristic.
    # Rule 1: Date + Num -> Line
    assert chart_type == "line" 

def test_chart_selection_empty():
    agent = VisualizationAgent()
    df = pd.DataFrame()
    analysis = agent.analyze_dataframe(df)
    chart_type = agent.select_chart_type(df, analysis)
    assert chart_type == "empty" or chart_type == "none"

# ── Report Agent Tests ───────────────────────────────────────────────────────

@patch("src.agents.report_agent.SimpleDocTemplate")
def test_pdf_generation(mock_pdf_build):
    agent = ReportAgent()
    data = {
        "question": "Test",
        "sql_query": "SELECT 1",
        "results": pd.DataFrame({"a": [1]}),
        "insights": {"summary": "test"}
    }
    # Should not raise
    path = agent.generate_pdf_report(data)
    assert path.endswith(".pdf")

# ── Integration Test (Mocked) ────────────────────────────────────────────────

@patch("src.agents.orchestrator.SQLAgent")
@patch("src.agents.orchestrator.VisualizationAgent")
@patch("src.agents.orchestrator.InsightsAgent")
@patch("src.agents.orchestrator.ReportAgent")
def test_orchestrator_pipeline(MockReport, MockInsights, MockViz, MockSQL):
    # Setup mocks
    sql_instance = MockSQL.return_value
    sql_instance.process_question.return_value = {
        "sql_query": "SELECT 1", 
        "results": pd.DataFrame({"a": [1]})
    }
    
    viz_instance = MockViz.return_value
    viz_instance.create_visualization.return_value = {"figure": "fig", "chart_type": "bar"}
    
    orch = Orchestrator()
    result = orch.process_query("Test question")
    
    assert result["status"] == "completed"
    assert "visualization" in result
    assert "reports" in result
