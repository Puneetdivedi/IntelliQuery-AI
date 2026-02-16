# IntelliQuery AI

![IntelliQuery AI Banner](https://img.icons8.com/cloud/100/1f77b4/business-report.png)

> Natural Language Business Intelligence Platform powered by GenAI

IntelliQuery AI translates natural language questions into SQL queries, executes them against your database, visualizes the results, extracts business insights, and generates downloadable reports—all automatically.

## ✨ Features

- **Multi-Agent Orchestration**: Specialized agents for SQL, Visualization, Insights, and Reporting.
- **Local Intelligence (New)**: Support for **Ollama**, allowing 100% private execution without API keys.
- **Obsidian Dark Theme**: Premium, modern interface designed for executive presentations.
- **Automated Reporting**: Downloadable PDF and Word reports generated instantly.
- **SQL Security**: Integrated query validation and dialect pinning (SQLite).

## 🏗️ Architecture

IntelliQuery AI follows a modular, agentic architecture. For a deep dive into how data flows through the system, see [ARCHITECTURE.md](file:///c:/Users/ADMIN/Desktop/IntelliQuery%20AI/ARCHITECTURE.md).

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.9+
- [Ollama](https://ollama.com/) (Optional: for local/offline intelligence)

### 2. Installation
```powershell
# Clone the repository
git clone <repo-url>
cd "IntelliQuery AI"

# Run the automated setup
./setup.ps1
```

### 3. Configuration (.env)
Choose between Cloud (Groq) or Local (Ollama) providers:

**Cloud Mode (Default):**
```env
LLM_PROVIDER=groq
GROQ_API_KEY=your_key_here
```

**Local Mode (No-API):**
1. Install Ollama and run `ollama run llama3`.
2. Update `.env`:
```env
LLM_PROVIDER=ollama
LLM_MODEL=llama3
OLLAMA_BASE_URL=http://localhost:11434
```

## 📊 Demo Mode
If no API key or local provider is found, the app automatically enables **Demo Mode**. This allows you to explore the platform using high-quality pre-defined patterns for sample queries (e.g., "Top 5 products", "Last 10 sales").

## 🏗️ Architecture

The system uses a multi-agent architecture orchestrated to handle the BI pipeline:

1. **User Question** → **Orchestrator**
2. **SQL Agent** → Generates SQL & Retrieves Data
3. **Visualization Agent** → Creates Plotly Charts
4. **Insights Agent** → Generates Analysis via LLM
5. **Report Agent** → Compiles PDF/DOCX
6. **UI** → Displays all results to user

## 🛠️ Tech Stack

- **LLM:** Groq API (Llama 3.1 70B)
- **Framework:** LangChain, Streamlit
- **Database:** SQLite or PostgreSQL (SQLAlchemy)
- **Visualization:** Plotly
- **Reports:** ReportLab, Python-Docx
- **Testing:** Pytest

## 🧪 Testing

Run the test suite to verify all agents:
```bash
pytest tests/ -v
```

## 🚢 Deployment

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for full deployment instructions.

## 📝 License

MIT License

## 👤 Author

**Puneet Divedi**
- [LinkedIn](#)
- [GitHub](#)
