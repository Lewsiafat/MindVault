# syntax=docker/dockerfile:1.7

# ─── Stage 1: build frontend ─────────────────────────────────
FROM node:20-alpine AS frontend
WORKDIR /app/frontend

COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install

COPY frontend/ ./
# vite.config.ts outputs to ../src/static → /app/src/static
RUN npm run build


# ─── Stage 2: python runtime ─────────────────────────────────
FROM python:3.13-slim AS runtime
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --extra all --no-dev

COPY src/ ./src/
COPY --from=frontend /app/src/static/ ./src/static/
COPY data.example/ ./data.example/

ENV PORT=10016
EXPOSE 10016

CMD ["uv", "run", "--no-sync", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "10016"]
