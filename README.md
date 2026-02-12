# IntelliQuery AI

![IntelliQuery AI Banner](https://img.icons8.com/cloud/100/1f77b4/business-report.png)

> Natural Language Business Intelligence Platform powered by GenAI

IntelliQuery AI translates natural language questions into SQL queries, executes them against your database, visualizes the results, extracts business insights, and generates downloadable reports—all automatically.

## ⭐ Features

- **Natural Language to SQL**: Converts English questions into complex SQL queries.
- **Smart Visualization**: Auto-selects the best chart type (Bar, Line, Pie, Scatter) for your data.
- **AI Business Insights**: Analyzes trends, anomalies, and provides actionable recommendations.
- **Automated Reporting**: Generates professional PDF and DOCX reports on command.
- **Interactive UI**: Clean, responsive Streamlit interface with dark/light mode support.

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- PostgreSQL database (Local or Supabase)
- Groq Cloud API Key (Free)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/intelliquery-ai.git
   cd intelliquery-ai
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**
   Copy the example environment file and add your keys:
   ```bash
   cp .env.example .env
   ```
   Edit `.env`:
   ```env
   GROQ_API_KEY=your_groq_api_key
   DATABASE_URL=postgresql://user:password@localhost:5432/intelliquery_db
   ```

4. **Setup Database**
   Initialize schema and generate sample data:
   ```bash
   python scripts/setup_database.py
   python scripts/generate_sample_data.py
   ```

5. **Run Application**
   ```bash
   streamlit run app.py
   ```

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
- **Database:** PostgreSQL (SQLAlchemy)
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
