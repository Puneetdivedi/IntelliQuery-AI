"""
IntelliQuery AI - Main Streamlit Application
"""

import streamlit as st
import pandas as pd
import time
import json
from typing import Dict, Any

from src.config.settings import Settings
from src.agents.orchestrator import Orchestrator
from src.database.connection import get_table_info, test_connection
from src.ui.components import (
    message_box,
    sql_display,
    data_table_display,
    visualization_display,
    insights_card,
    schema_viewer,
    loading_animation
)
from src.utils.logger import setup_logger

logger = setup_logger("app")

def display_agent_result(result: Dict[str, Any]):
    """Render the full result dictionary from the agent."""
    # 1. SQL
    sql = result.get("sql_query")
    if sql:
        with st.expander("View SQL Query", expanded=False):
            st.code(sql, language="sql")

    # 2. Data
    df = result.get("results")
    if df is not None and not df.empty:
        st.dataframe(df.head(100), use_container_width=True)
        
        # Download CSV
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "⬇️ Download CSV", 
            csv, 
            "data.csv", 
            "text/csv", 
            key=f"csv_{int(time.time())}_{len(str(result))}"
        )
    elif result.get("status") == "completed_no_data":
        st.warning("Query returned no results.")

    # 3. Visualization
    viz = result.get("visualization")
    if viz and viz.get("figure"):
            st.plotly_chart(viz["figure"], use_container_width=True)

    # 4. Insights
    insights = result.get("insights")
    if insights and insights.get("summary") != "Could not generate AI insights at this time.":
        with st.container():
            st.markdown("### 💡 AI Insights")
            st.info(insights.get("summary"))
            
            c1, c2 = st.columns(2)
            with c1:
                if insights.get("key_insights"):
                    st.markdown("**Key Takeaways**")
                    for k in insights["key_insights"]:
                        st.markdown(f"- {k}")
            with c2:
                if insights.get("recommendations"):
                    st.markdown("**Recommendations**")
                    for r in insights["recommendations"]:
                        st.markdown(f"- {r}")

    # 5. Reports
    reports = result.get("reports")
    if reports:
        c1, c2 = st.columns(2)
        with c1:
            if reports.get("pdf"):
                with open(reports["pdf"], "rb") as f:
                    st.download_button("📄 Download PDF Report", f, file_name="report.pdf", mime="application/pdf", key=f"pdf_{int(time.time())}")
        with c2:
            if reports.get("docx"):
                with open(reports["docx"], "rb") as f:
                    st.download_button("📝 Download Word Report", f, file_name="report.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", key=f"docx_{int(time.time())}")


# ── Configuration ────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="IntelliQuery AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .stChatMessage {
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 0.5rem;
    }
    .stButton button {
        border-radius: 20px;
    }
    .reportview-container .main .block-container {
        padding-top: 2rem;
    }
    h1 {
        color: #1f77b4;
    }
</style>
""", unsafe_allow_html=True)


# ── Initialization ───────────────────────────────────────────────────────────

@st.cache_resource
def get_orchestrator():
    """Initialize agent orchestrator (singleton)."""
    return Orchestrator()

@st.cache_data
def get_schema():
    """Fetch database schema for sidebar."""
    return get_table_info()

try:
    Settings.validate()
    orchestrator = get_orchestrator()
    schema = get_schema()
except Exception as e:
    st.error(f"Startup Error: {e}")
    st.stop()

# Session State for History
if "messages" not in st.session_state:
    st.session_state.messages = []


def process_user_input(prompt: str):
    """Handle the user loop: Add to history -> Process -> Display."""
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Agent response
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        
        with st.status("Thinking...", expanded=True) as status:
            st.write("Generating SQL query...")
            
            # Call Orchestrator
            result = orchestrator.process_query(prompt)
            
            if result.get("error"):
                status.update(label="Error", state="error", expanded=True)
                st.error(result["error"])
                st.session_state.messages.append({"role": "assistant", "content": result["error"], "error": True})
                return

            st.write("Executing query & creating visualization...")
            
            # Update status based on steps
            for step in result.get("steps", []):
                st.write(f"✅ {step}")
            
            status.update(label="Complete!", state="complete", expanded=False)

        # ── Display Results ────────────────────────────────────────────────
        
        # ── Display Results ────────────────────────────────────────────────
        display_agent_result(result)
        
        # Save interaction to history
        st.session_state.messages.append({
            "role": "assistant", 
            "content": result, # Store full result dict for re-rendering if needed
            "type": "result_dict"
        })


# ── Sidebar ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.image("https://img.icons8.com/cloud/100/1f77b4/business-report.png", width=50) # Placeholder icon
    st.title("IntelliQuery AI")
    st.markdown("Natural Language BI Platform")
    st.divider()
    
    # Schema Viewer
    schema_viewer(schema)
    st.divider()
    
    # Sample Queries
    st.markdown("### ⚡ Quick Queries")
    samples = [
        "Top 5 products by revenue",
        "Show sales trend over last year",
        "Customers by region breakdown",
        "List orders with 'Processing' status"
    ]
    
    for q in samples:
        if st.button(q, use_container_width=True):
             # This is a bit tricky in Streamlit - updating input via button 
             # usually requires session state callback or rerun.
             # Simplest way: set a session state var and rerun input logic?
             # For now, let's just insert into chat directly.
             process_user_input(q)
             st.rerun()

    st.divider()
    
    # System Status
    with st.expander("System Status"):
         if test_connection():
             st.success("Database: Connected")
         else:
             st.error("Database: Connection Failed")
         
         if Settings.GROQ_API_KEY.startswith("gsk_"):
             st.success("LLM API: Configured")
         else:
             st.warning("LLM API: Missing/Invalid")
             
    st.divider()

    # Export History
    if st.session_state.messages:
        chat_str = json.dumps(st.session_state.messages, default=str, indent=2)
        st.download_button(
            "💾 Export Conversation",
            chat_str,
            file_name=f"intelliquery_chat_{int(time.time())}.json",
            mime="application/json",
            use_container_width=True
        )

    if st.button("🗑️ Clear History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.caption("v1.0.1 | Built with IntelliQuery AI")


# ── Main Chat Interface ──────────────────────────────────────────────────────

st.title("Business Intelligence Assistant")
st.markdown("Ask questions about your data in plain English.")

# Display History
for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.markdown(msg["content"])
    elif msg["role"] == "assistant":
        with st.chat_message("assistant"):
            if msg.get("error"):
                 st.error(msg["content"])
            elif msg.get("type") == "result_dict":
                # Re-render result from history using the shared function
                display_agent_result(msg["content"])


# Input
if prompt := st.chat_input("Ask a question about your data..."):
    process_user_input(prompt)
