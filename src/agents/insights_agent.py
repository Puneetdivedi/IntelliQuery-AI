"""
Insights Agent module for generating business insights from data.

Uses Groq Llama 3 to analyze query results and provide structured insights.
"""

from __future__ import annotations

import json
import pandas as pd
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from src.config.settings import Settings
from src.utils.logger import setup_logger
from src.utils.error_handler import APIError

logger = setup_logger("insights_agent")


class InsightsAgent:
    """Agent responsible for deriving insights from data using LLM."""

    def __init__(self):
        """Initialize the Insights Agent."""
        Settings.validate()
        
        if Settings.GROQ_API_KEY:
            self.llm = ChatGroq(
                model_name=Settings.LLM_MODEL,
                temperature=0.2, # Slight creativity for insights
                api_key=Settings.GROQ_API_KEY
            )
        else:
            self.llm = None
            logger.info("InsightsAgent initialized in DEMO MODE.")

    def _calculate_statistics(self, df: pd.DataFrame) -> dict:
        """Calculate basic statistics for the dataframe."""
        if df.empty:
            return {}
            
        stats = {
            "row_count": len(df),
            "columns": list(df.columns),
            "numeric_summary": df.describe().to_dict()
        }
        return stats

    def generate_insights(self, df: pd.DataFrame, question: str) -> dict:
        """Generate structured business insights from data."""
        try:
            if df.empty:
                return {
                    "summary": "No data returned for this query.",
                    "key_insights": [],
                    "trends": "None",
                    "recommendations": []
                }

            # Prepare data summary for LLM context
            # limit rows to avoid token limits
            data_head = df.head(20).to_markdown(index=False)
            stats = self._calculate_statistics(df)
            
            system_prompt = """You are a senior business analyst. Analyze the provided data and answer the user's question with actionable insights.

Output MUST be a valid JSON object with the following keys:
{
  "summary": "1-2 sentence executive summary",
  "key_insights": ["Bullet point 1", "Bullet point 2", "Bullet point 3"],
  "trends": "Description of trends/patterns (if applicable)",
  "anomalies": "Any outliers or unusual data points (if applicable)",
  "recommendations": ["Actionable recommendation 1", "Actionable recommendation 2"]
}

Do not include markdown formatting like ```json ... ```. Return raw JSON only.
"""
            
            user_msg = f"""
Original Question: {question}

Data Sample (First 20 rows):
{data_head}

Statistical Summary:
{json.dumps(stats, default=str)}

Provide your analysis in JSON format.
"""

            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("user", user_msg)
            ])

            chain = prompt | self.llm | StrOutputParser()
            
            logger.info(f"Generating insights for: {question}")
            response = chain.invoke({})
            
            # Clean response
            clean_json = response.strip()
            if clean_json.startswith("```json"):
                clean_json = clean_json[7:]
            if clean_json.endswith("```"):
                clean_json = clean_json[:-3]
            clean_json = clean_json.strip()

            insights = json.loads(clean_json)
            return insights

        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            # Fallback
            return {
                "summary": "Could not generate AI insights at this time.",
                "key_insights": ["Data available in table."],
                "trends": "N/A",
                "recommendations": []
            }
