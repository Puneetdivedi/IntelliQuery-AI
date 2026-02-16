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
    display_agent_result,
    schema_viewer,
    loading_animation
)


# ── Configuration ────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="IntelliQuery AI | Executive Insights",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Professional Executive Look
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Global Typography */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Main Background & Gradient Mesh */
    .stApp {
        background-color: #0F172A;
        background-image: 
            radial-gradient(at 0% 0%, rgba(30, 58, 138, 0.3) 0, transparent 50%), 
            radial-gradient(at 50% 0%, rgba(79, 70, 229, 0.15) 0, transparent 50%),
            radial-gradient(at 100% 0%, rgba(30, 58, 138, 0.3) 0, transparent 50%);
        background-attachment: fixed;
    }
    
    /* Sidebar Refinement */
    [data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.95);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
    }
    
    /* Header Styling */
    .main-header {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(to right, #F8FAFC, #94A3B8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .sub-header {
        font-size: 1.1rem;
        color: #94A3B8;
        margin-bottom: 2rem;
    }

    /* Professional Metric Cards */
    [data-testid="stMetric"] {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1rem;
        transition: all 0.3s ease;
    }
    [data-testid="stMetric"]:hover {
        border-color: #6366F1;
        background: rgba(30, 41, 59, 0.8);
    }

    /* Chat Input Refinement */
    [data-testid="stChatInput"] {
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        background: rgba(30, 41, 59, 0.8) !important;
    }

    /* Status & Spinners */
    .stStatusWidget {
        background: rgba(30, 41, 59, 0.8) !important;
        border-radius: 12px !important;
    }

    /* Button Animations */
    .stButton button {
        border-radius: 10px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    /* Custom Scroller */
    ::-webkit-scrollbar {
        width: 8px;
    }
    ::-webkit-scrollbar-track {
        background: transparent;
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 255, 255, 0.2);
    }
    /* System Health Pod */
    .health-pod {
        background: rgba(30, 41, 59, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 0.85rem;
        border-radius: 12px;
        margin-top: 1rem;
        font-size: 0.85rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        transition: transform 0.2s ease;
    }
    .health-pod:hover {
        transform: translateY(-2px);
        background: rgba(30, 41, 59, 0.6);
        border-color: rgba(99, 102, 241, 0.3);
    }
</style>
""", unsafe_allow_html=True)


# ── Initialization ───────────────────────────────────────────────────────────

def get_orchestrator():
    """Initialize agent orchestrator."""
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
        display_agent_result(result)
        
        # Save interaction to history
        st.session_state.messages.append({
            "role": "assistant", 
            "content": result, # Store full result dict for re-rendering if needed
            "type": "result_dict"
        })


# ── Sidebar Navigation ──────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/cloud/100/1f77b4/business-report.png", width=60) 
    st.markdown('<h2 style="margin-top:0;">IntelliQuery AI</h2>', unsafe_allow_html=True)
    st.caption("Strategic Business Intelligence")
    st.divider()

    # 1. Configuration & Health
    with st.expander("🛠️ System Configuration", expanded=True):
        provider_options = ["Ollama (Local)", "Groq (Cloud)", "Demo Mode"]
        current_idx = 0 if Settings.LLM_PROVIDER == "ollama" else (1 if Settings.LLM_PROVIDER == "groq" else 2)
        
        selected_provider = st.selectbox(
            "Intelligence Provider",
            options=provider_options,
            index=current_idx
        )
        
        if "Ollama" in selected_provider:
            Settings.LLM_PROVIDER = "ollama"
        elif "Groq" in selected_provider:
            Settings.LLM_PROVIDER = "groq"
        else:
            Settings.LLM_PROVIDER = "demo"

        # Mini Health Pod
        st.markdown('<div class="health-pod">', unsafe_allow_html=True)
        if Settings.LLM_PROVIDER == "ollama":
            is_healthy = Settings.check_ollama_health()
            status_color = "#10B981" if is_healthy else "#EF4444"
            st.markdown(f"**Ollama**: <span style='color:{status_color}'>{'● Online' if is_healthy else '○ Offline'}</span>", unsafe_allow_html=True)
        elif Settings.LLM_PROVIDER == "groq":
            status_color = "#10B981" if Settings.GROQ_API_KEY else "#F59E0B"
            st.markdown(f"**Groq**: <span style='color:{status_color}'>{'● Active' if Settings.GROQ_API_KEY else '○ Key Missing'}</span>", unsafe_allow_html=True)
        
        db_healthy = test_connection()
        db_color = "#10B981" if db_healthy else "#EF4444"
        st.markdown(f"**Database**: <span style='color:{db_color}'>{'● Ready' if db_healthy else '○ Error'}</span>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # 2. Schema Insights
    with st.expander("📂 Database Schema"):
        schema_viewer(schema)
    
    # 3. Quick Actions
    st.markdown("### ⚡ Quick Queries")
    samples = [
        "Top 5 products by revenue",
        "Show sales trend over last year",
        "Customers by region breakdown"
    ]
    for q in samples:
        if st.button(q, use_container_width=True):
             process_user_input(q)
             st.rerun()

    # 4. Utilities
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🧹 Clear", use_container_width=True, help="Clear cache"):
            st.cache_data.clear()
            st.toast("Cache cleared!")
    with col2:
        if st.button("🗑️ Reset", use_container_width=True, help="Clear history"):
            st.session_state.messages = []
            st.rerun()

    if st.session_state.messages:
        chat_str = json.dumps(st.session_state.messages, default=str, indent=2)
        st.download_button(
            "💾 Export Conversation",
            chat_str,
            file_name=f"intelliquery_export.json",
            mime="application/json",
            use_container_width=True
        )

    st.caption("🚀 v1.1.2 | Executive Intelligence")


# ── Main Chat Interface ──────────────────────────────────────────────────────

st.markdown('<h1 class="main-header">Executive BI Assistant</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Translate natural language into strategic business insights.</p>', unsafe_allow_html=True)

# Welcome Message if no history
if not st.session_state.messages:
    st.info("👋 **Welcome to IntelliQuery AI.** I can help you analyze sales trends, identify top customers, and generate executive reports. Try a query below or select a sample from the sidebar.")

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
