# IntelliQuery AI Run Script
# Usage: .\run.ps1

Write-Host "🏙️ Launching IntelliQuery AI | Executive Insights..." -ForegroundColor Cyan

$pythonExe = Get-Command python.exe -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source

if (-not $pythonExe) {
    Write-Host "❌ Python not found. Please run setup.ps1 first." -ForegroundColor Red
    exit 1
}

# Ensure .env exists
if (-not (Test-Path .env)) {
    Write-Host "⚠️  Configuration missing (.env). Running setup first..." -ForegroundColor Yellow
    .\setup.ps1
}

# Launch Streamlit
Write-Host "📊 Starting Dashboard..." -ForegroundColor Green
& $pythonExe -m streamlit run app.py --server.port 8501
