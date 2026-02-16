# Local LLM Integration: Ollama Setup

IntelliQuery AI supports **Ollama** for 100% private, local execution. This allows you to run the entire BI pipeline without external API keys or internet dependencies.

## 1. Install Ollama
Download and install Ollama from [ollama.com](https://ollama.com/).

## 2. Pull a Model
Open your terminal and pull a compatible model (Llama 3 is recommended):
```powershell
ollama pull llama3
```

## 3. Configure IntelliQuery AI
Update your `.env` file in the project root:

```env
# Choose Ollama as the provider
LLM_PROVIDER=ollama

# Specify the model you pulled
LLM_MODEL=llama3

# Default Ollama API endpoint
OLLAMA_BASE_URL=http://localhost:11434
```

## 4. Run Ollama Server
Ensure the Ollama application is running in the background. You can verify it by visiting `http://localhost:11434` in your browser.

## 5. Verification
Run the project tests to ensure the local LLM is correctly generating SQL:
```powershell
pytest tests/ -v
```

## Troubleshooting
- **Model not found:** Ensure the name in `.env` (e.g., `llama3`) exactly matches the name in `ollama list`.
- **Connection Refused:** Verify that the Ollama server is running and the `OLLAMA_BASE_URL` is correct.
