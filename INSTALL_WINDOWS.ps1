# Complete Installation & Run Guide for Windows PowerShell
# Cryptocurrency Price Tracker - Redis Edition

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "  Cryptocurrency Dashboard - Installation" -ForegroundColor Cyan
Write-Host "============================================`n" -ForegroundColor Cyan

# ============================================
# STEP 1: INSTALL REDIS (Memurai for Windows)
# ============================================

Write-Host "STEP 1: Redis Installation" -ForegroundColor Yellow
Write-Host "-------------------------------------------" -ForegroundColor Gray

Write-Host "`nOption A - Install using Chocolatey (Recommended):" -ForegroundColor Green
Write-Host "Run this command in an ADMIN PowerShell window:" -ForegroundColor White
Write-Host "  choco install memurai -y" -ForegroundColor Cyan
Write-Host "`nThen start Memurai:"
Write-Host "  memurai" -ForegroundColor Cyan

Write-Host "`nOption B - Manual Download:" -ForegroundColor Green
Write-Host "1. Download from: https://www.memurai.com/get-memurai" -ForegroundColor White
Write-Host "2. Install the .msi file"
Write-Host "3. Memurai starts automatically as a Windows service"

Write-Host "`nOption C - WSL + Redis:" -ForegroundColor Green
Write-Host "  wsl --install" -ForegroundColor Cyan
Write-Host "  wsl -d Ubuntu" -ForegroundColor Cyan
Write-Host "  sudo apt update && sudo apt install redis-server -y" -ForegroundColor Cyan
Write-Host "  redis-server" -ForegroundColor Cyan

Write-Host "`nVerify Redis is running:" -ForegroundColor Green
Write-Host "  redis-cli ping" -ForegroundColor Cyan
Write-Host "  Expected output: PONG`n" -ForegroundColor Gray

Read-Host "Press Enter once Redis is installed and running"

# ============================================
# STEP 2: VERIFY PREREQUISITES
# ============================================

Write-Host "`nSTEP 2: Verifying Prerequisites" -ForegroundColor Yellow
Write-Host "-------------------------------------------" -ForegroundColor Gray

# Check Python
Write-Host "`nChecking Python..." -ForegroundColor Green
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  ✓ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Python not found!" -ForegroundColor Red
    Write-Host "  Install from: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# Check Node.js
Write-Host "Checking Node.js..." -ForegroundColor Green
try {
    $nodeVersion = node --version 2>&1
    Write-Host "  ✓ Node.js $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Node.js not found!" -ForegroundColor Red
    Write-Host "  Install from: https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}

# Check Redis
Write-Host "Checking Redis connection..." -ForegroundColor Green
try {
    $redisCheck = redis-cli ping 2>&1
    if ($redisCheck -eq "PONG") {
        Write-Host "  ✓ Redis is running" -ForegroundColor Green
    } else {
        throw "Redis not responding"
    }
} catch {
    Write-Host "  ✗ Redis is not running!" -ForegroundColor Red
    Write-Host "  Start Redis first (see STEP 1)" -ForegroundColor Yellow
    exit 1
}

Write-Host "`n✓ All prerequisites satisfied!`n" -ForegroundColor Green

# ============================================
# STEP 3: INSTALL PYTHON DEPENDENCIES
# ============================================

Write-Host "STEP 3: Installing Python Dependencies" -ForegroundColor Yellow
Write-Host "-------------------------------------------" -ForegroundColor Gray

Set-Location pythonBackend

Write-Host "`nInstalling Python packages..." -ForegroundColor Green
pip install -r requirements.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Python dependencies installed" -ForegroundColor Green
} else {
    Write-Host "  ✗ Failed to install Python dependencies" -ForegroundColor Red
    exit 1
}

Set-Location ..

# ============================================
# STEP 4: INSTALL FRONTEND DEPENDENCIES
# ============================================

Write-Host "`nSTEP 4: Installing Frontend Dependencies" -ForegroundColor Yellow
Write-Host "-------------------------------------------" -ForegroundColor Gray

Set-Location frontend-react-app

Write-Host "`nInstalling npm packages (this may take a minute)..." -ForegroundColor Green
npm install

if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Frontend dependencies installed" -ForegroundColor Green
} else {
    Write-Host "  ✗ Failed to install frontend dependencies" -ForegroundColor Red
    exit 1
}

Set-Location ..

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "  ✓ Installation Complete!" -ForegroundColor Green
Write-Host "============================================`n" -ForegroundColor Cyan

Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Open 3 PowerShell terminals" -ForegroundColor White
Write-Host "2. Run the servers using the commands below`n" -ForegroundColor White

# ============================================
# INSTRUCTIONS FOR RUNNING
# ============================================

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  How to Run the Application" -ForegroundColor Cyan
Write-Host "============================================`n" -ForegroundColor Cyan

Write-Host "TERMINAL 1 - HTTP Server (Historical Data):" -ForegroundColor Yellow
Write-Host "  cd pythonBackend" -ForegroundColor Cyan
Write-Host "  python api_server.py`n" -ForegroundColor Cyan

Write-Host "TERMINAL 2 - WebSocket Server (Live Data):" -ForegroundColor Yellow
Write-Host "  cd pythonBackend" -ForegroundColor Cyan
Write-Host "  python websocket_server.py`n" -ForegroundColor Cyan

Write-Host "TERMINAL 3 - Frontend (React):" -ForegroundColor Yellow
Write-Host "  cd frontend-react-app" -ForegroundColor Cyan
Write-Host "  npm run dev`n" -ForegroundColor Cyan

Write-Host "Then open browser to: " -NoNewline -ForegroundColor White
Write-Host "http://localhost:5173`n" -ForegroundColor Green

Write-Host "============================================`n" -ForegroundColor Cyan
