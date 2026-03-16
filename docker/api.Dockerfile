FROM python:3.11-slim

WORKDIR /app

# System-Abhaengigkeiten
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Python-Abhaengigkeiten
COPY pyproject.toml .
RUN pip install --no-cache-dir .

# Quellcode
COPY src/ src/

EXPOSE 8000

CMD ["uvicorn", "backend.api.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
