FROM python:3.11-slim

# ── System deps: Node.js 20 + Nanum fonts ──────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl ca-certificates fonts-nanum \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && fc-cache -fv \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ── Python deps ────────────────────────────────────────────────
COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# ── Frontend build ─────────────────────────────────────────────
COPY frontend/package*.json frontend/
RUN cd frontend && npm install

COPY frontend/ frontend/
RUN cd frontend && npm run build

# ── Backend source ─────────────────────────────────────────────
COPY backend/ backend/

# Move built React app into backend/static so FastAPI can serve it
RUN cp -r frontend/dist backend/static

WORKDIR /app/backend

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
