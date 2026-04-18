### Stage 1: Build frontend ###
FROM node:20-slim AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

### Stage 2: Python runtime ###
FROM python:3.13-slim
WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Install Python dependencies
COPY pyproject.toml ./
RUN uv sync --no-dev

# Copy backend source
COPY src/ ./src/

# Copy built frontend
COPY --from=frontend-builder /app/frontend/dist ./src/static/

# Copy sample data (will be overridden by volume mount in production)
COPY data/ ./data/

# Create wiki and cache directories
RUN mkdir -p data/wiki data/cache

EXPOSE 8000

ENV PYTHONPATH=/app

CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
