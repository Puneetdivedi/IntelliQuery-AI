"""
Orchestrator module that coordinates all specialized agents to process a user query.
"""

from __future__ import annotations

import time
from typing import Any

from src.agents.sql_agent import SQLAgent
from src.agents.visualization_agent import VisualizationAgent
from src.agents.insights_agent import InsightsAgent
from src.agents.report_agent import ReportAgent
from src.utils.logger import setup_logger
from src.utils.error_handler import handle_error

logger = setup_logger("orchestrator")


class Orchestrator:
    """
    Main coordinator that drives the multi-agent pipeline:
    Question -> SQL -> Data -> Visualization -> Insights -> Report
    """

    def __init__(self):
        """Initialize all sub-agents."""
        self.sql_agent = SQLAgent()
        self.viz_agent = VisualizationAgent()
        self.insights_agent = InsightsAgent()
        self.report_agent = ReportAgent()

    def process_query(self, question: str, conversation_history: list = None) -> dict[str, Any]:
        """
        Process a user question through the full pipeline.
        
        Args:
            question: The natural language query.
            conversation_history: List of previous interactions (not used in v1 but ready for context).
            
        Returns:
            Dictionary containing results, processing metadata, and paths to artifacts.
        """
        start_time = time.time()
        result: dict[str, Any] = {
            "question": question,
            "status": "processing",
            "steps": [],
            "errors": []
        }

        try:
            # 1. Generate & Execute SQL
            logger.info(f"Step 1: SQL Generation for '{question}'")
            try:
                sql_result = self.sql_agent.process_question(question)
                result.update(sql_result)
                result["steps"].append("SQL Generated & Executed")
            except Exception as e:
                msg = handle_error(e, context="SQL Agent")
                result["error"] = msg
                result["errors"].append(str(e))
                logger.error(f"Pipeline failed at SQL stage: {e}")
                return result

            df = result.get("results")
            
            # If no data, stop early
            if df is None or df.empty:
                result["status"] = "completed_no_data"
                result["answer"] = "The query returned no results."
                return result

            # 2. Visualization (Best Effort)
            try:
                logger.info("Step 2: Visualization")
                viz_result = self.viz_agent.create_visualization(df, question)
                result["visualization"] = viz_result
                result["steps"].append("Visualization Created")
            except Exception as e:
                logger.warning(f"Visualization failed (continuing pipeline): {e}")
                result["visualization"] = None
                result["errors"].append(f"Viz Error: {e}")

            # 3. Insights (Best Effort)
            try:
                logger.info("Step 3: Insights Analysis")
                insights = self.insights_agent.generate_insights(df, question)
                result["insights"] = insights
                result["steps"].append("Insights Generated")
            except Exception as e:
                logger.warning(f"Insights failed (continuing pipeline): {e}")
                result["insights"] = {}
                result["errors"].append(f"Insights Error: {e}")

            # 4. Report Generation (Best Effort)
            try:
                logger.info("Step 4: Report Generation")
                # Prepare data for report agent
                report_data = {
                    "question": question,
                    "sql_query": result.get("sql_query"),
                    "results": df,
                    "insights": result.get("insights", {})
                }
                
                pdf_path = self.report_agent.generate_pdf_report(report_data)
                docx_path = self.report_agent.generate_docx_report(report_data)
                
                result["reports"] = {
                    "pdf": pdf_path,
                    "docx": docx_path
                }
                result["steps"].append("Reports Generated")
            except Exception as e:
                logger.warning(f"Report generation failed: {e}")
                result["reports"] = {}
                result["errors"].append(f"Report Error: {e}")

            # Finalize
            duration = time.time() - start_time
            result["metadata"] = {
                "execution_time": round(duration, 2),
                "row_count": len(df),
                "columns": list(df.columns)
            }
            result["status"] = "completed"
            
            logger.info(f"Pipeline completed in {duration:.2f}s")
            return result

        except Exception as e:
            logger.critical(f"Unhandled pipeline error: {e}")
            result["status"] = "failed"
            result["error"] = "An unexpected error occurred processing your request."
            return result
