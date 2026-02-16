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
    """Display SQL query within an expander to save space."""
    if not query:
        return
        
    with st.expander("🔍 View Technical Query Details"):
        st.code(query, language="sql")

def data_table_display(df: pd.DataFrame, max_rows: int = 100):
    """Display a dataframe with a glassmorphism feel and download options."""
    if df is None or df.empty:
        st.info("No data to display.")
        return

    st.markdown(f"### 📊 Result Data ({len(df)} rows)")
    
    # Show subset for performance
    display_df = df.head(max_rows)
    st.dataframe(
        display_df, 
        use_container_width=True, 
        hide_index=True
    )
    
    # Download buttons in a row
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "💾 Export Result (CSV)",
        csv,
        "query_results.csv",
        "text/csv",
        key=f"download_csv_{len(df)}",
        use_container_width=False
    )

def visualization_display(viz_data: Dict[str, Any]):
    """Display Plotly chart with cleaner styling."""
    if not viz_data or not viz_data.get("figure"):
        return

    st.markdown("### 📈 Visual Analysis")
    st.plotly_chart(
        viz_data["figure"], 
        use_container_width=True, 
        theme="streamlit"
    )
    
    if viz_data.get("title"):
        st.caption(viz_data["title"])

def insights_card(insights: Dict[str, Any]):
    """Display insights in a professional executive summary format."""
    if not insights:
        return

    st.markdown("### 💡 Strategic Insights")
    
    # Summary Highlight
    if insights.get("summary"):
        st.markdown(f"""
        <div style="background: rgba(99, 102, 241, 0.1); border-left: 5px solid #6366f1; padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem;">
            <p style="margin: 0; font-size: 1.1rem; font-weight: 500; color: #E2E8F0;">
                {insights['summary']}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if insights.get("key_insights"):
            st.markdown("#### 🎯 Key Findings")
            for item in insights["key_insights"]:
                st.markdown(f"• {item}")
                
    with col2:
        if insights.get("recommendations"):
            st.markdown("#### 🚀 Action Plan")
            for item in insights["recommendations"]:
                st.markdown(f"• {item}")

def schema_viewer(schema: Dict[str, list]):
    """Sidebar component to explore database schema with better styling."""
    if not schema:
        st.sidebar.warning("Schema not available")
        return

    st.sidebar.markdown("### 🗄️ Database Directory")
    
    search = st.sidebar.text_input("🔍 Search Tables", "", key="schema_search").lower()
    
    for table, columns in schema.items():
        if search and search not in table.lower():
            continue
            
        with st.sidebar.expander(f"📄 {table}"):
            for col in columns:
                 icon = "🔑" if col.get("primary_key") else "•"
                 st.markdown(f"{icon} **{col['name']}** <span style='color:#94A3B8; font-size:0.8rem;'>({col['type']})</span>", unsafe_allow_html=True)

def display_agent_result(result: Dict[str, Any]):
    """Render results using a clean, professional vertical flow."""
    # 1. Performance Metadata at the top but subtle
    meta = result.get("metadata")
    if meta:
        st.caption(f"⏱️ Generation Time: {meta.get('execution_time', 0)}s | 📂 Data Size: {meta.get('row_count', 0)} records")

    # 2. Insights - High Priority at the top
    insights_card(result.get("insights"))

    # 3. Visualization
    visualization_display(result.get("visualization"))

    # 4. Data Table
    df = result.get("results")
    if df is not None:
        data_table_display(df)
    elif result.get("status") == "completed_no_data":
        st.warning(result.get("answer", "No relevant data found for this specific query."))

    # 5. Reports (Download Links) in a clean grid
    reports = result.get("reports")
    if reports:
        st.markdown("---")
        st.markdown("### 📄 Executive Reports")
        c1, c2, c3 = st.columns([1, 1, 2])
        with c1:
            if reports.get("pdf"):
                with open(reports["pdf"], "rb") as f:
                    st.download_button(
                        label="📄 PDF Report",
                        data=f,
                        file_name="intelliquery_report.pdf",
                        mime="application/pdf",
                        key=f"dl_pdf_{time()}",
                        use_container_width=True
                    )
        with c2:
            if reports.get("docx"):
                with open(reports["docx"], "rb") as f:
                    st.download_button(
                        label="📝 Word Report",
                        data=f,
                        file_name="intelliquery_report.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        key=f"dl_docx_{time()}",
                        use_container_width=True
                    )
    
    # 6. Technical Details at the bottom
    sql_display(result.get("sql_query"))

def loading_animation(message: str = "Processing..."):
    """Show a spinner with custom message."""
    return st.spinner(message)
