FROM python:3.11-slim

WORKDIR /app

# System-Abhaengigkeiten fuer Playwright
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev \
    libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdrm2 libxkbcommon0 libxcomposite1 \
    libxdamage1 libxrandr2 libgbm1 libpango-1.0-0 \
    libasound2 libxshmfence1 \
    && rm -rf /var/lib/apt/lists/*

# Python-Abhaengigkeiten
COPY pyproject.toml .
RUN pip install --no-cache-dir . \
    && playwright install chromium

# Quellcode
COPY src/ src/

CMD ["scrapy", "list"]
