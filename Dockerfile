FROM python:3.11-slim

# System deps for reportlab/matplotlib backends
RUN apt-get update && apt-get install -y \
    libfreetype6-dev libjpeg62-turbo-dev libpng-dev ghostscript \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# ---------- Defaults you can override at runtime ----------
# Use ARG -> ENV so we have sane defaults at build time, but can override via container env.
ARG LLM_PROVIDER=mock
ARG ALLOWED_FEATURES=single,relationship,yearly,monthly,daily,health,ai,diag
ARG AI_STRICT=0
ARG OPENAI_MODEL=gpt-4o-mini
# Security toggles (runtime overridable)
ARG SECURITY_BYPASS=0
ARG API_KEY=

ENV LLM_PROVIDER=${LLM_PROVIDER} \
    ALLOWED_FEATURES=${ALLOWED_FEATURES} \
    AI_STRICT=${AI_STRICT} \
    OPENAI_MODEL=${OPENAI_MODEL} \
    SECURITY_BYPASS=${SECURITY_BYPASS} \
    API_KEY=${API_KEY}

# Expose FastAPI port
EXPOSE 8000

# Run API
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
