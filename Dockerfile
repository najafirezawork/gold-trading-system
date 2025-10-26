# استفاده از Python 3.13 slim image
FROM python:3.13-slim

# متغیرهای محیطی
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# ساخت دایرکتوری کاری
WORKDIR /app

# کپی فایل‌های requirements
COPY requirements.txt .

# نصب dependencies
RUN pip install --no-cache-dir -r requirements.txt

# کپی کل پروژه
COPY . .

# ساخت دایرکتوری برای logs
RUN mkdir -p /app/logs

# پورت‌های مورد نیاز (برای آینده - web dashboard)
EXPOSE 8000

# دستور پیش‌فرض
CMD ["python", "main.py"]
