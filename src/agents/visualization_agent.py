"""
Visualization Agent module for automatically charting data.

Analyzes DataFrame structure and selects appropriate Plotly visualizations.
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.graph_objs import Figure

from src.utils.logger import setup_logger
from src.utils.error_handler import VisualizationError

logger = setup_logger("visualization_agent")


class VisualizationAgent:
    """Agent responsible for creating visualizations from data."""

    def analyze_dataframe(self, df: pd.DataFrame) -> dict:
        """Analyze DataFrame columns to determine types and potential chart mappings."""
        if df.empty:
            return {"type": "empty"}

        # Identify column types
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        datetime_cols = df.select_dtypes(include=['datetime', 'datetimetz']).columns.tolist()
        # Treat object/string as categorical
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

        return {
            "numeric": numeric_cols,
            "datetime": datetime_cols,
            "categorical": categorical_cols,
            "row_count": len(df),
            "col_count": len(df.columns)
        }

    def select_chart_type(self, df: pd.DataFrame, analysis: dict) -> str:
        """Heuristic logic to select the best chart type."""
        if df.empty:
            return "none"
            
        num_cols = analysis["numeric"]
        cat_cols = analysis["categorical"]
        date_cols = analysis["datetime"]
        row_count = analysis["row_count"]
        col_count = analysis["col_count"]

        # Rule 1: Time Series -> Line Chart
        # Requires at least one date column and one numeric column
        if date_cols and num_cols:
            return "line"

        # Rule 2: Comparison of Categories -> Bar Chart
        # Requires 1 categorical and 1+ numeric
        # E.g., Sales by Region
        if cat_cols and num_cols and row_count <= 20:
             return "bar"

        # Rule 3: Distribution / Part of Whole -> Pie Chart
        # 1 categorical, 1 numeric, few rows (<= 7)
        if len(cat_cols) == 1 and len(num_cols) == 1 and row_count <= 7:
             return "pie"

        # Rule 4: Correlation -> Scatter Plot
        # 2+ numeric columns, many rows
        if len(num_cols) >= 2 and row_count > 20:
            return "scatter"
            
        # Rule 5: Comparison of many Categories (>20) -> Bar Chart (Horizontal usually better but standardizing on bar)
        if cat_cols and num_cols:
            return "bar"

        # Default fallback: Data Table
        return "table"

    def create_bar_chart(self, df: pd.DataFrame, x: str, y: str, title: str) -> Figure:
        """Create a Plotly Bar chart."""
        fig = px.bar(
            df, x=x, y=y, title=title,
            template="plotly_white",
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        return self._style_figure(fig)

    def create_line_chart(self, df: pd.DataFrame, x: str, y: str, title: str) -> Figure:
        """Create a Plotly Line chart."""
        fig = px.line(
            df, x=x, y=y, title=title,
            markers=True,
            template="plotly_white",
             color_discrete_sequence=px.colors.qualitative.Safe
        )
        return self._style_figure(fig)

    def create_pie_chart(self, df: pd.DataFrame, names: str, values: str, title: str) -> Figure:
        """Create a Plotly Pie chart."""
        fig = px.pie(
            df, names=names, values=values, title=title,
            template="plotly_white",
             color_discrete_sequence=px.colors.qualitative.Safe
        )
        return self._style_figure(fig)

    def create_scatter_plot(self, df: pd.DataFrame, x: str, y: str, title: str) -> Figure:
        """Create a Plotly Scatter plot."""
        fig = px.scatter(
            df, x=x, y=y, title=title,
            template="plotly_white",
             color_discrete_sequence=px.colors.qualitative.Safe
        )
        return self._style_figure(fig)

    def _style_figure(self, fig: Figure) -> Figure:
        """Apply consistent styling to all figures."""
        fig.update_layout(
            font=dict(family="Arial", size=12),
            title=dict(font=dict(size=20)),
            margin=dict(l=40, r=40, t=60, b=40),
            hovermode="closest"
        )
        return fig

    def create_visualization(self, df: pd.DataFrame, question: str) -> dict:
        """Main entry point: Analyze data -> Select Chart -> Generate."""
        try:
            if df.empty:
                logger.warning("Empty DataFrame passed to visualization agent.")
                return {"figure": None, "chart_type": "none", "title": "No Data"}

            analysis = self.analyze_dataframe(df)
            chart_type = self.select_chart_type(df, analysis)
            
            # Heuristic for axis selection
            # Just take the first valid column for simplicity in this version
            # A real agent might use LLM to decide columns mapping
            
            fig = None
            title = f"Visualization for: {question}"
            
            if chart_type == "line":
                x_col = analysis["datetime"][0]
                y_col = analysis["numeric"][0]
                fig = self.create_line_chart(df, x=x_col, y=y_col, title=title)
                
            elif chart_type == "bar":
                x_col = analysis["categorical"][0] if analysis["categorical"] else df.columns[0]
                y_col = analysis["numeric"][0]
                fig = self.create_bar_chart(df, x=x_col, y=y_col, title=title)
                
            elif chart_type == "pie":
                names_col = analysis["categorical"][0]
                vals_col = analysis["numeric"][0]
                fig = self.create_pie_chart(df, names=names_col, values=vals_col, title=title)
                
            elif chart_type == "scatter":
                x_col = analysis["numeric"][0]
                y_col = analysis["numeric"][1] if len(analysis["numeric"]) > 1 else analysis["numeric"][0]
                fig = self.create_scatter_plot(df, x=x_col, y=y_col, title=title)
            
            # fallback or table handled by returning None figure but valid type
            return {
                "figure": fig,
                "chart_type": chart_type,
                "title": title
            }

        except Exception as e:
            logger.error(f"Visualization generation failed: {e}")
            raise VisualizationError(f"Could not create visualization: {e}")
