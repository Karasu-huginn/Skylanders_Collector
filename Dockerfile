# Stage 1: Build React frontend
FROM node:22-alpine AS frontend
WORKDIR /build
COPY react/package.json react/package-lock.json ./
RUN npm ci
COPY react/ ./
RUN npm run build

# Stage 2: Python runtime
FROM python:3.12-slim AS runtime
WORKDIR /app

# System dependency for psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends libpq-dev curl && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY fastapi/pyproject.toml ./
RUN pip install --no-cache-dir .

# Copy backend code
COPY fastapi/ ./

# Copy seed script and data (used by seed container)
COPY db_maker.py skylanders_data.json ./

# Copy built frontend into static/
COPY --from=frontend /build/dist ./static
COPY react/public/assets ./static/assets

EXPOSE 8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
