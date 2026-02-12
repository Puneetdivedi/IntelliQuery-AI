"""
SQL Agent module for converting natural language questions into executable SQL queries.

Uses Llama 3 via Groq to generate SQL based on the provided database schema.
Includes validation to prevent destructive operations.
"""

from __future__ import annotations

import re
import pandas as pd
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from src.config.settings import Settings
from src.database.connection import execute_query, get_table_info
from src.utils.logger import setup_logger
from src.utils.error_handler import QueryGenerationError, DatabaseError

logger = setup_logger("sql_agent")


class SQLAgent:
    """Agent responsible for translating natural language to SQL and executing it."""

    def __init__(self):
        """Initialize the SQL Agent with LLM and schema context."""
        Settings.validate()
        
        self.llm = ChatGroq(
            model_name=Settings.LLM_MODEL,
            temperature=0,
            api_key=Settings.GROQ_API_KEY
        )
        
        # Load schema once during initialization
        self.schema_info = self._format_schema_for_prompt()
        self.system_prompt = self._build_system_prompt()

    def _format_schema_for_prompt(self) -> str:
        """Format database schema into a string for the LLM prompt."""
        try:
            schema = get_table_info()
            formatted = []
            
            for table, columns in schema.items():
                col_strs = [f"{c['name']} ({c['type']})" for c in columns]
                formatted.append(f"Table: {table}\nColumns: {', '.join(col_strs)}")
            
            # Add relationship hints hardcoded for better context
            relationships = [
                "Relationships:",
                "- customers.region_id -> regions.region_id",
                "- orders.customer_id -> customers.customer_id",
                "- order_items.order_id -> orders.order_id",
                "- order_items.product_id -> products.product_id"
            ]
            
            return "\n\n".join(formatted + relationships)
        except Exception as e:
            logger.error(f"Failed to fetch schema: {e}")
            return "Schema unavailable."

    def _build_system_prompt(self) -> str:
        """Construct the system prompt for SQL generation."""
        return f"""You are an expert PostgreSQL query generator.
        
You have access to a database with the following schema:

{self.schema_info}

Rules:
1. Return ONLY the SQL query. No markdown, no explanations, no code blocks.
2. Use standard PostgreSQL syntax.
3. Read the Question carefully.
4. If the question asks for "top X", use LIMIT X.
5. If the question implies a time period, filter on appropriate date columns.
6. Do NOT generate destructive queries (DROP, DELETE, INSERT, UPDATE, ALTER).
7. If you cannot answer the question given the schema, return "I cannot answer this question."
"""

    def generate_sql(self, question: str) -> str:
        """Generate SQL query from natural language question."""
        try:
            prompt = ChatPromptTemplate.from_messages([
                ("system", self.system_prompt),
                ("user", "{question}")
            ])
            
            chain = prompt | self.llm | StrOutputParser()
            
            logger.info(f"Generating SQL for: {question}")
            sql_response = chain.invoke({"question": question})
            
            # Clean up response (remove markdown code blocks if present)
            clean_sql = sql_response.strip()
            clean_sql = re.sub(r"```sql", "", clean_sql, flags=re.IGNORECASE)
            clean_sql = re.sub(r"```", "", clean_sql).strip()
            
            return clean_sql
            
        except Exception as e:
            logger.error(f"Error generating SQL: {e}")
            raise QueryGenerationError(f"Failed to generate SQL: {e}")

    def validate_sql(self, sql: str) -> bool:
        """Check provided SQL for destructive commands."""
        forbidden = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE", "GRANT", "REVOKE"]
        upper_sql = sql.upper()
        
        for term in forbidden:
            # Simple check: word boundary to avoid false positives (like "update_date")
            if re.search(r"\b" + term + r"\b", upper_sql):
                logger.warning(f"Validation failed: Forbidden keyword '{term}' found in SQL.")
                return False
        return True

    def execute_sql(self, sql: str) -> pd.DataFrame:
        """Execute the SQL query and return results as DataFrame."""
        if not self.validate_sql(sql):
            raise QueryGenerationError("Generated SQL contains forbidden commands.")
            
        try:
            return execute_query(sql)
        except DatabaseError as e:
            # Pass through database errors
            raise e
        except Exception as e:
            logger.error(f"Unexpected error executing SQL: {e}")
            raise DatabaseError(f"Execution failed: {e}")

    def process_question(self, question: str) -> dict:
        """Full pipeline: Question -> SQL -> DataFrame -> Result Dict."""
        sql = self.generate_sql(question)
        
        if "I cannot answer" in sql:
             raise QueryGenerationError("The question cannot be translated to SQL based on the schema.")

        df = self.execute_sql(sql)
        
        return {
            "question": question,
            "sql_query": sql,
            "results": df,
            "row_count": len(df)
        }
