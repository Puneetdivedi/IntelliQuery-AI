"""
Reusable Streamlit UI components for IntelliQuery AI.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from time import time
from typing import Any, Dict

def message_box(role: str, content: str, error: bool = False):
    """
    Display a chat message with robust styling.
    
    Args:
        role: 'user' or 'assistant'
        content: The text content
        error: If true, style as error
    """
    with st.chat_message(role):
        if error:
            st.error(content)
        else:
            st.markdown(content)

def sql_display(query: str):
    """Display SQL query with a copy button."""
    if not query:
        return
        
    st.markdown("### 🔍 Generated SQL")
    st.code(query, language="sql")

def data_table_display(df: pd.DataFrame, max_rows: int = 100):
    """Display a dataframe with download options."""
    if df is None or df.empty:
        st.info("No data to display.")
        return

    st.markdown(f"### 📊 Data Preview ({len(df)} rows)")
    
    # Show subset for performance
    display_df = df.head(max_rows)
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # Download buttons
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "⬇️ Download CSV",
        csv,
        "query_results.csv",
        "text/csv",
        key=f"download_csv_{len(df)}"
    )

def visualization_display(viz_data: Dict[str, Any]):
    """Display Plotly chart."""
    if not viz_data or not viz_data.get("figure"):
        return

    st.markdown("### 📈 Visualization")
    st.plotly_chart(viz_data["figure"], use_container_width=True)
    
    if viz_data.get("title"):
        st.caption(viz_data["title"])

def insights_card(insights: Dict[str, Any]):
    """Display insights in a styled card."""
    if not insights:
        return

    st.markdown("### 💡 AI Insights")
    
    with st.container():
        # Summary
        if insights.get("summary"):
            st.info(f"**Executive Summary:** {insights['summary']}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if insights.get("key_insights"):
                st.markdown("**Key Takeaways:**")
                for item in insights["key_insights"]:
                    st.markdown(f"- {item}")
                    
        with col2:
            if insights.get("recommendations"):
                st.markdown("**Recommendations:**")
                for item in insights["recommendations"]:
                    st.markdown(f"- {item}")

def schema_viewer(schema: Dict[str, list]):
    """Sidebar component to explore database schema."""
    if not schema:
        st.warning("Schema not available")
        return

    st.sidebar.markdown("### 🗄️ Database Schema")
    
    search = st.sidebar.text_input("🔍 Search Tables", "", key="schema_search").lower()
    
    for table, columns in schema.items():
        if search and search not in table.lower():
            continue
            
        with st.sidebar.expander(f"📄 {table}"):
            for col in columns:
                 icon = "🔑" if col.get("primary_key") else "🔹"
                 st.markdown(f"{icon} **{col['name']}**")
                 st.caption(f"Type: {col['type']}")

def display_agent_result(result: Dict[str, Any]):
    """Render the full result dictionary from the orchestrator using modular components."""
    # 1. SQL Query
    sql_display(result.get("sql_query"))

    # 2. Data Table
    df = result.get("results")
    if df is not None:
        data_table_display(df)
    elif result.get("status") == "completed_no_data":
        st.warning(result.get("answer", "No data found for this query."))

    # 3. Visualization
    visualization_display(result.get("visualization"))

    # 4. Insights
    insights_card(result.get("insights"))

    # 5. Reports (Download Links)
    reports = result.get("reports")
    if reports:
        st.markdown("### 📄 Reports")
        c1, c2 = st.columns(2)
        with c1:
            if reports.get("pdf"):
                with open(reports["pdf"], "rb") as f:
                    st.download_button(
                        label="📄 Download PDF Report",
                        data=f,
                        file_name="intelliquery_report.pdf",
                        mime="application/pdf",
                        key=f"dl_pdf_{time()}"
                    )
        with c2:
            if reports.get("docx"):
                with open(reports["docx"], "rb") as f:
                    st.download_button(
                        label="📝 Download Word Report",
                        data=f,
                        file_name="intelliquery_report.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        key=f"dl_docx_{time()}"
                    )
    
    # 6. Performance Metadata
    meta = result.get("metadata")
    if meta:
        st.markdown("---")
        st.caption(f"⏱️ **Performance:** {meta.get('execution_time', 0)}s | **Rows:** {meta.get('row_count', 0)}")

def loading_animation(message: str = "Processing..."):
    """Show a spinner with custom message."""
    return st.spinner(message)
