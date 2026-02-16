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
            logger.info("Pipeline Step 1: SQL Generation & Execution")
            try:
                sql_result = self.sql_agent.process_question(question)
                result.update(sql_result)
                result["steps"].append("SQL Engine: Query generated and data retrieved")
            except Exception as e:
                msg = handle_error(e, context="SQL Agent")
                result["status"] = "failed"
                result["error"] = msg
                result["errors"].append(f"SQL Error: {str(e)}")
                logger.error(f"Critical pipeline failure at SQL stage: {e}")
                return result

            df = result.get("results")
            
            # If no data, stop early with a clean status
            if df is None or df.empty:
                result["status"] = "completed_no_data"
                result["answer"] = "The database returned an empty set for this query."
                result["metadata"] = {"execution_time": round(time.time() - start_time, 2), "row_count": 0}
                logger.info("Pipeline early exit: No data found.")
                return result

            # 2. Visualization (Best Effort)
            logger.info("Pipeline Step 2: Visualization Engine")
            try:
                viz_result = self.viz_agent.create_visualization(df, question)
                result["visualization"] = viz_result
                result["steps"].append("Viz Engine: Chart auto-generated")
            except Exception as e:
                logger.warning(f"Non-critical failure (Visualization): {e}")
                result["visualization"] = None
                result["errors"].append(f"Viz Error: {str(e)}")

            # 3. Insights (Best Effort)
            logger.info("Pipeline Step 3: Analysis Engine")
            try:
                insights = self.insights_agent.generate_insights(df, question)
                result["insights"] = insights
                result["steps"].append("Analysis Engine: Insights extracted")
            except Exception as e:
                logger.warning(f"Non-critical failure (Insights): {e}")
                result["insights"] = {"summary": "Insight generation skipped due to a minor error."}
                result["errors"].append(f"Insights Error: {str(e)}")

            # 4. Report Generation (Best Effort)
            logger.info("Pipeline Step 4: Document Engine")
            try:
                report_data = {
                    "question": question,
                    "sql_query": result.get("sql_query"),
                    "results": df,
                    "insights": result.get("insights", {})
                }
                
                pdf_path = self.report_agent.generate_pdf_report(report_data)
                docx_path = self.report_agent.generate_docx_report(report_data)
                
                result["reports"] = {"pdf": pdf_path, "docx": docx_path}
                result["steps"].append("Document Engine: PDF/Word reports ready")
            except Exception as e:
                logger.warning(f"Non-critical failure (Reports): {e}")
                result["reports"] = {}
                result["errors"].append(f"Report Error: {str(e)}")

            # Finalize
            duration = time.time() - start_time
            result["metadata"] = {
                "execution_time": round(duration, 2),
                "row_count": len(df),
                "columns": list(df.columns)
            }
            result["status"] = "completed"
            
            logger.info(f"Pipeline finished successfully in {duration:.2f}s")
            return result

        except Exception as e:
            logger.critical(f"Global pipeline crash: {e}")
            result["status"] = "failed"
            result["error"] = "An internal engine error occurred. Please check the logs."
            return result
