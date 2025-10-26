#!/bin/bash
# اسکریپت راه‌اندازی Docker

echo "🐳 Starting Gold Trading System with Docker..."

# ساخت image
echo "📦 Building Docker image..."
docker-compose build

# اجرای container
echo "🚀 Starting container..."
docker-compose up -d

# نمایش logs
echo "📋 Showing logs (Ctrl+C to exit)..."
docker-compose logs -f trading-system
