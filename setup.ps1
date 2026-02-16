# IntelliQuery AI Setup Script
Write-Host "🚀 Starting IntelliQuery AI Setup..." -ForegroundColor Cyan

# 1. Check Python
if (!(Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Python not found. Please install Python 3.9+ and try again." -ForegroundColor Red
    exit
}

# 2. Install Dependencies
Write-Host "📦 Installing dependencies from requirements.txt..." -ForegroundColor Yellow
python -m pip install -r requirements.txt

# 3. Setup Database
Write-Host "🗄️ Setting up database..." -ForegroundColor Yellow
python scripts/setup_database.py

# 4. Generate Sample Data
Write-Host "📊 Generating realistic sample data..." -ForegroundColor Yellow
python scripts/generate_sample_data.py

# 5. Create .env if missing
if (!(Test-Path .env)) {
    Write-Host "📝 Creating .env from template..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "⚠️  IMPORTANT: Please open .env and add your GROQ_API_KEY!" -ForegroundColor Magenta
}

Write-Host "`n✅ Setup Complete! To launch the app, run:" -ForegroundColor Green
Write-Host "streamlit run app.py" -ForegroundColor Cyan
