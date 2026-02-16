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
    """Render the full result dictionary from the agent using shared components."""
    # 1. SQL
    sql_display(result.get("sql_query"))

    # 2. Data
    df = result.get("results")
    if df is not None:
        data_table_display(df)
    elif result.get("status") == "completed_no_data":
        st.warning(result.get("answer", "No data found for this query."))

    # 3. Visualization
    visualization_display(result.get("visualization"))

    # 4. Insights
    insights_card(result.get("insights"))

    # 5. Reports
    reports = result.get("reports")
    if reports:
        st.markdown("### 📄 Reports")
        c1, c2 = st.columns(2)
        with c1:
            if reports.get("pdf"):
                with open(reports["pdf"], "rb") as f:
                    st.download_button("Download PDF", f, file_name="intelliquery_report.pdf", mime="application/pdf", key=f"pdf_{result.get('metadata', {}).get('execution_time', 0)}")
        with c2:
            if reports.get("docx"):
                with open(reports["docx"], "rb") as f:
                    st.download_button("Download DOCX", f, file_name="intelliquery_report.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", key=f"docx_{result.get('metadata', {}).get('execution_time', 0)}")
    
    # 6. Metadata Performance Footer
    meta = result.get("metadata")
    if meta:
        st.markdown("---")
        st.caption(f"⏱️ **Performance:** Executed in {meta.get('execution_time', 0)}s | **Volume:** {meta.get('row_count', 0)} rows retrieved")


# ── Configuration ────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="IntelliQuery AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium Look
st.markdown("""
<style>
    /* Main Background and Typography */
    .stApp {
        background: radial-gradient(circle at 20% 20%, rgba(99, 102, 241, 0.15) 0%, rgba(14, 17, 23, 1) 100%), #0E1117;
        background-attachment: fixed;
    }
    
    /* Glassmorphism Containers */
    [data-testid="stChatMessage"] {
        background: rgba(30, 41, 59, 0.7) !important;
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
        margin-bottom: 0.75rem;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: #0B0E14;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* Elegant Buttons */
    .stButton button {
        background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
        color: white;
        border: none;
        border-radius: 8px;
        transition: all 0.2s ease;
        font-weight: 500;
        letter-spacing: 0.5px;
    }
    .stButton button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 15px rgba(99, 102, 241, 0.4);
    }
    
    /* Metric Cards */
    [data-testid="stMetricValue"] {
        color: #6366f1;
        font-weight: 700;
    }
    
    /* Headings */
    h1, h2, h3 {
        color: #F8FAFC !important;
        font-family: 'Inter', sans-serif;
        font-weight: 700;
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
    
    # ── Demo Mode Banner ───────────────────────────────────────────
    if not Settings.GROQ_API_KEY:
        st.warning("🚀 **DEMO MODE ACTIVE**: No API Key found. High-performance AI processing is available via the **Quick Query** buttons in the sidebar. Standard chat requires an API key.")
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
         db_status = test_connection()
         if db_status:
             st.success("Database: Connected (SQLite)")
         else:
             st.error("Database: Connection Failed")
         
         if Settings.GROQ_API_KEY.startswith("gsk_"):
             st.success("LLM API: Configured")
         else:
             st.warning("LLM API: Missing/Invalid")
             
    st.divider()

    # Utilities
    if st.button("🧹 Clear Cache", use_container_width=True):
        st.cache_data.clear()
        st.cache_resource.clear()
        st.toast("Cache cleared successfully!")

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
    st.caption("🚀 v1.1.0 | Built with IntelliQuery AI")


# ── Main Chat Interface ──────────────────────────────────────────────────────

st.title("Business Intelligence Assistant")
st.markdown("Ask questions about your data in plain English.")

# Welcome Message if no history
if not st.session_state.messages:
    st.info("👋 **Welcome!** Try asking something like: *'What were our top 5 products by revenue last quarter?'* or *'Show me the sales distribution by region.'*")

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
