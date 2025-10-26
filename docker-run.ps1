# اسکریپت PowerShell برای راه‌اندازی Docker

Write-Host "🐳 Starting Gold Trading System with Docker..." -ForegroundColor Green

# ساخت image
Write-Host "📦 Building Docker image..." -ForegroundColor Yellow
docker-compose build

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Build failed!" -ForegroundColor Red
    exit 1
}

# اجرای container
Write-Host "🚀 Starting container..." -ForegroundColor Yellow
docker-compose up -d

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Start failed!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Container started successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Useful commands:" -ForegroundColor Cyan
Write-Host "  - View logs:    docker-compose logs -f trading-system" -ForegroundColor White
Write-Host "  - Stop:         docker-compose stop" -ForegroundColor White
Write-Host "  - Restart:      docker-compose restart" -ForegroundColor White
Write-Host "  - Remove:       docker-compose down" -ForegroundColor White
Write-Host "  - Shell access: docker-compose exec trading-system bash" -ForegroundColor White
Write-Host ""

# نمایش logs
Write-Host "📋 Showing logs (Ctrl+C to exit)..." -ForegroundColor Yellow
docker-compose logs -f trading-system
