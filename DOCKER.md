# Docker Deployment Guide 🐳

راهنمای جامع استفاده از Docker برای اجرای Gold Trading System.

## فهرست مطالب

1. [پیش‌نیازها](#پیشنیازها)
2. [ساختار Docker](#ساختار-docker)
3. [راه‌اندازی سریع](#راهاندازی-سریع)
4. [روش‌های اجرا](#روشهای-اجرا)
5. [تنظیمات پیشرفته](#تنظیمات-پیشرفته)
6. [Production Deployment](#production-deployment)
7. [عیب‌یابی](#عیبیابی)

---

## پیش‌نیازها

### نصب Docker

**Windows:**
- [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop)
- نیاز به WSL 2

**Linux:**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

**macOS:**
- [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop)

### بررسی نصب

```bash
docker --version
docker-compose --version
```

## ساختار Docker

### فایل‌های Docker

```
Data/
├── Dockerfile              # Image definition
├── docker-compose.yml      # Service orchestration
├── .dockerignore          # فایل‌های exclude شده
├── docker-run.sh          # Bash script (Linux/Mac)
└── docker-run.ps1         # PowerShell script (Windows)
```

### Dockerfile Overview

```dockerfile
FROM python:3.13-slim

WORKDIR /app

# نصب dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# کپی کد
COPY . .

# Expose port (برای web dashboard آینده)
EXPOSE 8000

# اجرا
CMD ["python", "main.py"]
```

### Docker Compose Overview

```yaml
version: '3.8'

services:
  trading-system:
    build: .
    container_name: gold-trading
    environment:
      - TWELVE_DATA_API_KEY=${TWELVE_DATA_API_KEY}
    volumes:
      - ./:/app              # Live code reload
      - ./logs:/app/logs     # Persistent logs
      - ./results:/app/results  # Persistent results
```

## راه‌اندازی سریع

### Windows (PowerShell)

```powershell
# 1. Build image
.\docker-run.ps1 build

# 2. Run container
.\docker-run.ps1 run

# 3. View logs
.\docker-run.ps1 logs

# 4. Stop container
.\docker-run.ps1 stop

# 5. Clean up
.\docker-run.ps1 clean
```

### Linux/Mac (Bash)

```bash
# 1. اجازه اجرا
chmod +x docker-run.sh

# 2. Build
./docker-run.sh build

# 3. Run
./docker-run.sh run

# 4. Logs
./docker-run.sh logs

# 5. Stop
./docker-run.sh stop
```

### Docker Compose

```bash
# Build و Run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down

# Rebuild
docker-compose build --no-cache
docker-compose up -d
```

## روش‌های اجرا

### 1. اجرای ساده

```bash
docker build -t gold-trading .
docker run gold-trading
```

### 2. با Environment Variables

```bash
docker run -e TWELVE_DATA_API_KEY=your_key gold-trading
```

### 3. با Volume Mount (توسعه)

```bash
docker run -v $(pwd):/app gold-trading
```

### 4. Interactive Mode

```bash
docker run -it gold-trading bash

# داخل container:
python main.py
python examples/backtest_examples.py
```

### 5. Background Mode

```bash
docker run -d --name gold-trading gold-trading

# چک کردن logs
docker logs -f gold-trading

# متوقف کردن
docker stop gold-trading
docker rm gold-trading
```

## تنظیمات پیشرفته

### Custom Commands

#### اجرای Backtest

```bash
docker run gold-trading python examples/backtest_examples.py
```

#### اجرای Test

```bash
docker run gold-trading python -m pytest test_system.py -v
```

#### Python Interactive

```bash
docker run -it gold-trading python

>>> from data_layer import TwelveDataClient
>>> client = TwelveDataClient()
>>> data = client.get_time_series("XAU/USD", "1h", 10)
>>> print(data.data[0])
```

### Volume Configuration

#### Log Persistence

```bash
docker run -v $(pwd)/logs:/app/logs gold-trading
```

#### Results Persistence

```bash
docker run -v $(pwd)/results:/app/results gold-trading
```

#### Full Mount

```yaml
# docker-compose.yml
volumes:
  - ./:/app                    # Code
  - ./logs:/app/logs           # Logs
  - ./results:/app/results     # Results
  - ./data:/app/data           # Data cache
```

### Environment Configuration

#### .env File

```bash
# .env
TWELVE_DATA_API_KEY=e2527b8bfdac451094f85f9aa826bc65
DEFAULT_SYMBOL=XAU/USD
LOG_LEVEL=INFO
```

```bash
docker run --env-file .env gold-trading
```

#### docker-compose.yml

```yaml
services:
  trading-system:
    environment:
      - TWELVE_DATA_API_KEY=${TWELVE_DATA_API_KEY}
      - LOG_LEVEL=DEBUG
      - DEFAULT_SYMBOL=XAU/USD
```

### Network Configuration

#### Port Mapping (برای web dashboard آینده)

```bash
docker run -p 8000:8000 gold-trading
```

```yaml
# docker-compose.yml
services:
  trading-system:
    ports:
      - "8000:8000"
```

### Multi-Stage Build (بهینه‌سازی)

```dockerfile
# Build stage
FROM python:3.13-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.13-slim

WORKDIR /app

# کپی dependencies از builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# کپی کد
COPY . .

CMD ["python", "main.py"]
```

این روش image size را کاهش می‌دهد.

## Production Deployment

### 1. Docker Hub

#### Build و Push

```bash
# Tag
docker tag gold-trading username/gold-trading:latest

# Login
docker login

# Push
docker push username/gold-trading:latest
```

#### Pull و Run

```bash
docker pull username/gold-trading:latest
docker run -d --name gold-trading username/gold-trading:latest
```

### 2. با Docker Compose (توصیه شده)

#### Production docker-compose.yml

```yaml
version: '3.8'

services:
  trading-system:
    image: gold-trading:latest
    container_name: gold-trading
    restart: unless-stopped
    
    environment:
      - TWELVE_DATA_API_KEY=${TWELVE_DATA_API_KEY}
      - LOG_LEVEL=INFO
    
    volumes:
      - ./logs:/app/logs
      - ./results:/app/results
    
    networks:
      - trading-network
    
    healthcheck:
      test: ["CMD", "python", "-c", "print('healthy')"]
      interval: 30s
      timeout: 10s
      retries: 3

networks:
  trading-network:
    driver: bridge
```

#### Deploy

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### 3. Auto-Restart

```yaml
restart: unless-stopped   # یا always
```

### 4. Resource Limits

```yaml
services:
  trading-system:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

### 5. Logging

```yaml
services:
  trading-system:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### 6. با PostgreSQL و Redis (آینده)

```yaml
version: '3.8'

services:
  trading-system:
    build: .
    depends_on:
      - postgres
      - redis
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/trading
      - REDIS_URL=redis://redis:6379
  
  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=trading
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

## عیب‌یابی

### مشکلات رایج

#### 1. Container بلافاصله Exit می‌شود

```bash
# بررسی logs
docker logs gold-trading

# اجرای interactive
docker run -it gold-trading bash
```

#### 2. API Key کار نمی‌کند

```bash
# بررسی env vars
docker run gold-trading env | grep TWELVE_DATA

# تست connection
docker run gold-trading python -c "
from data_layer import TwelveDataClient
client = TwelveDataClient()
print(client.get_quote('XAU/USD'))
"
```

#### 3. Volume mount کار نمی‌کند (Windows)

```powershell
# استفاده از absolute path
docker run -v C:\Users\...\Desktop\Projects\Data:/app gold-trading
```

#### 4. Build خیلی طول می‌کشد

```bash
# استفاده از cache
docker build --cache-from gold-trading:latest -t gold-trading .

# استفاده از .dockerignore
# اضافه کردن __pycache__, .git, etc.
```

#### 5. Image size زیاد است

```bash
# استفاده از alpine image
FROM python:3.13-alpine

# یا multi-stage build
# (مثال در بالا)

# بررسی size
docker images gold-trading
```

### دستورات مفید

```bash
# لیست containers
docker ps -a

# لیست images
docker images

# حذف container
docker rm gold-trading

# حذف image
docker rmi gold-trading

# حذف همه stopped containers
docker container prune

# حذف همه unused images
docker image prune -a

# بررسی disk usage
docker system df

# Clean all
docker system prune -a --volumes

# Inspect container
docker inspect gold-trading

# Stats
docker stats gold-trading

# Top processes
docker top gold-trading

# Execute command
docker exec gold-trading python --version

# Copy files
docker cp gold-trading:/app/results ./results-backup
```

### Performance Monitoring

```bash
# CPU و Memory usage
docker stats gold-trading --no-stream

# Logs با timestamp
docker logs --timestamps gold-trading

# Follow logs
docker logs -f --tail 100 gold-trading
```

## Automation

### Cron Job (Linux)

```bash
# crontab -e
0 * * * * cd /path/to/project && docker-compose up -d
```

### Windows Task Scheduler

```powershell
# Task Scheduler GUI یا:
schtasks /create /tn "Gold Trading" /tr "C:\path\docker-run.ps1 run" /sc hourly
```

### Health Check Script

```bash
#!/bin/bash
# health-check.sh

if ! docker ps | grep -q gold-trading; then
    echo "Container not running, restarting..."
    docker-compose up -d
fi
```

```bash
# crontab
*/5 * * * * /path/to/health-check.sh
```

## Next Steps

- [ ] اضافه کردن web dashboard با FastAPI
- [ ] Integration با PostgreSQL
- [ ] Integration با Redis برای caching
- [ ] Kubernetes deployment
- [ ] CI/CD با GitHub Actions

---

**برای سوالات بیشتر:**
- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- پروژه `README.md` و `DEVELOPER_GUIDE.md`
