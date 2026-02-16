# IntelliQuery AI Professional Setup Script
# Usage: .\setup.ps1

$ErrorActionPreference = "Stop"

Write-Host "🚀 Starting IntelliQuery AI Professional Setup..." -ForegroundColor Cyan

# 1. Environment Check
Write-Host "🔍 Verifying environment..." -ForegroundColor Yellow
$pythonExe = Get-Command python.exe -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source
if (-not $pythonExe) {
    Write-Host "❌ Python 3.9+ not found in PATH. Please install Python and try again." -ForegroundColor Red
    exit 1
}
Write-Host "✅ Found Python at: $pythonExe" -ForegroundColor Green

# 2. Dependency Management
Write-Host "📦 Installing/Updating core dependencies..." -ForegroundColor Yellow
& $pythonExe -m pip install --upgrade pip
& $pythonExe -m pip install -r requirements.txt

# 3. Database Initialization
Write-Host "🗄️ Initializing Business Intelligence Database..." -ForegroundColor Yellow
& $pythonExe scripts/setup_database.py
& $pythonExe scripts/generate_sample_data.py
Write-Host "✅ Database ready." -ForegroundColor Green

# 4. Configuration Setup
if (-not (Test-Path .env)) {
    Write-Host "📝 Creating .env from template..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "⚠️  ACTION REQUIRED: Please add your GROQ_API_KEY to the .env file!" -ForegroundColor Magenta
}

Write-Host "`n✨ Setup Complete! ✨" -ForegroundColor Green
Write-Host "To launch the platform, run: " -ForegroundColor White -NoNewline
Write-Host ".\run.ps1" -ForegroundColor Cyan
