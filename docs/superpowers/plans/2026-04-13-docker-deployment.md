# Docker Deployment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Containerize the Skylanders Collector app with Docker Compose so it can be deployed on a home PC and accessed from any device via Tailscale.

**Architecture:** Three Docker Compose services — PostgreSQL database, FastAPI+React API server (multi-stage build), and a one-shot seed container. The API serves both the built React SPA and the backend routes through a single port (8080).

**Tech Stack:** Docker, Docker Compose, PostgreSQL 16, Node 22, Python 3.12, FastAPI, Vite

---

### Task 1: Create .dockerignore

**Files:**
- Create: `.dockerignore`

- [ ] **Step 1: Create the .dockerignore file**

```
node_modules
react/node_modules
react/dist
__pycache__
*.pyc
.git
.github
.claude
.superpowers
.env
.env.*
!.env.example
docs
*.md
.venv
.pytest_cache
```

- [ ] **Step 2: Commit**

```bash
git add .dockerignore
git commit -m "chore: add .dockerignore"
```

---

### Task 2: Modify db_maker.py to use configurable API URL

**Files:**
- Modify: `db_maker.py:1-4`

The seeding script hardcodes `http://localhost:8001/api`. Inside Docker, the seed container needs to reach the API at `http://api:8080/api`. Make the URL configurable via environment variable with a fallback.

- [ ] **Step 1: Replace the hardcoded URL with an env var**

Change the top of `db_maker.py` from:

```python
import json
import requests

DB_URL = "http://localhost:8001/api"
```

to:

```python
import json
import os
import requests

DB_URL = os.getenv("API_URL", "http://localhost:8001/api")
```

- [ ] **Step 2: Verify local dev still works**

Run the backend locally and confirm `db_maker.py` still uses the default URL:

```bash
cd fastapi
uvicorn main:app --port 8001 --reload &
cd ..
python -c "import os; print(os.getenv('API_URL', 'http://localhost:8001/api'))"
```

Expected output: `http://localhost:8001/api`

- [ ] **Step 3: Commit**

```bash
git add db_maker.py
git commit -m "feat: make db_maker API URL configurable via env var"
```

---

### Task 3: Modify FastAPI to serve static files in production

**Files:**
- Modify: `fastapi/main.py`

Add conditional static file serving so that when the `static/` directory exists (production Docker build), FastAPI serves the React SPA. When it doesn't exist (local dev), behavior is unchanged.

- [ ] **Step 1: Update main.py**

Replace the entire contents of `fastapi/main.py` with:

```python
import os
from pathlib import Path
from fastapi import APIRouter, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from db import engine, Base
import routers.edition_router as edition_router
import routers.item_router as item_router
import routers.type_router as type_router
import routers.variant_router as variant_router
import routers.element_router as element_router

app = FastAPI()

api_router = APIRouter(prefix="/api")
api_router.include_router(edition_router.router)
api_router.include_router(type_router.router)
api_router.include_router(variant_router.router)
api_router.include_router(element_router.router)
api_router.include_router(item_router.router)
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

# Serve built React frontend in production
STATIC_DIR = Path(__file__).parent / "static"
if STATIC_DIR.is_dir():
    # Figurine images, icons, logos
    app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(request: Request, full_path: str):
        """Serve React SPA — returns index.html for all non-API, non-asset routes."""
        file_path = STATIC_DIR / full_path
        if full_path and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(STATIC_DIR / "index.html")
```

Key details:
- The `/assets` mount goes before the catch-all so asset requests are handled directly by `StaticFiles` (efficient, supports caching headers)
- The catch-all `/{full_path:path}` serves JS/CSS files if they exist, otherwise returns `index.html` for client-side routing (`/search`, `/item/123`)
- API routes are registered via `include_router` before the catch-all, so `/api/*` takes priority
- The entire static block is inside `if STATIC_DIR.is_dir()` — in local dev, `static/` doesn't exist so nothing changes

- [ ] **Step 2: Verify local dev is unaffected**

```bash
cd fastapi
uvicorn main:app --port 8001 --reload
```

Open `http://localhost:8001/api/editions` in a browser — should return JSON. The catch-all route should NOT be registered (no `static/` directory).

- [ ] **Step 3: Commit**

```bash
git add fastapi/main.py
git commit -m "feat: serve React SPA from FastAPI when static/ exists"
```

---

### Task 4: Create the Dockerfile

**Files:**
- Create: `Dockerfile`

Multi-stage build: Node builds the frontend, Python runs everything.

- [ ] **Step 1: Create the Dockerfile at the project root**

```dockerfile
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
```

- [ ] **Step 2: Verify the Dockerfile builds**

```bash
docker build -t skylanders-test .
```

Expected: Build completes successfully. Check the final line says something like `Successfully tagged skylanders-test:latest`.

- [ ] **Step 3: Commit**

```bash
git add Dockerfile
git commit -m "feat: add multi-stage Dockerfile"
```

---

### Task 5: Create the seed script

**Files:**
- Create: `seed.sh`

A shell script that waits for the API to be healthy, checks if data exists, and seeds if empty.

- [ ] **Step 1: Create seed.sh at the project root**

```bash
#!/bin/sh
set -e

API_URL="${API_URL:-http://api:8080/api}"

echo "Waiting for API at $API_URL ..."
until curl -sf "$API_URL/editions/" > /dev/null 2>&1; do
  sleep 2
done
echo "API is ready."

# Check if data already exists
ITEM_COUNT=$(curl -sf "$API_URL/items/" | python -c "import sys,json; print(len(json.load(sys.stdin).get('items',[])))" 2>/dev/null || echo "0")

if [ "$ITEM_COUNT" -gt "0" ]; then
  echo "Database already has $ITEM_COUNT items. Skipping seed."
  exit 0
fi

echo "Database is empty. Seeding..."
python db_maker.py
echo "Seeding complete."
```

- [ ] **Step 2: Commit**

```bash
git add seed.sh
git commit -m "feat: add auto-seed script"
```

---

### Task 6: Create docker-compose.yml

**Files:**
- Create: `docker-compose.yml`

Defines all three services with correct environment, dependencies, and health checks.

- [ ] **Step 1: Create docker-compose.yml at the project root**

```yaml
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: skylanders
      POSTGRES_DB: Skylanders
    volumes:
      - skylanders-db-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d Skylanders"]
      interval: 5s
      timeout: 3s
      retries: 10

  api:
    build: .
    ports:
      - "8080:8080"
    environment:
      USER: postgres
      PASSWORD: skylanders
      HOST: db
      PORT: "5432"
      DB_NAME: Skylanders
    depends_on:
      db:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-sf", "http://localhost:8080/api/editions/"]
      interval: 5s
      timeout: 3s
      retries: 10

  seed:
    build: .
    entrypoint: ["sh", "seed.sh"]
    environment:
      API_URL: http://api:8080/api
    depends_on:
      api:
        condition: service_healthy
    restart: "no"

volumes:
  skylanders-db-data:
```

- [ ] **Step 2: Full test — bring it all up**

```bash
docker compose up -d --build
```

Wait about 30-60 seconds, then check:

```bash
docker compose ps
```

Expected: `db` and `api` are `running` (healthy), `seed` has exited with code 0.

```bash
curl http://localhost:8080/api/items/?limit=1
```

Expected: JSON response with at least 1 item (seed ran successfully).

```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/
```

Expected: `200` (React index.html served).

```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/search
```

Expected: `200` (SPA catch-all returns index.html).

- [ ] **Step 3: Commit**

```bash
git add docker-compose.yml Dockerfile
git commit -m "feat: add docker-compose with db, api, and seed services"
```

---

### Task 7: End-to-end verification and cleanup

**Files:**
- No new files

Full smoke test of the containerized app.

- [ ] **Step 1: Clean restart**

```bash
docker compose down
docker compose up -d --build
```

- [ ] **Step 2: Wait for seed and verify**

```bash
docker compose logs seed --follow
```

Expected output ends with:
```
Seeding complete.
```

- [ ] **Step 3: Verify all pages load**

Open `http://localhost:8080` in a browser:
- Landing page loads with "Skylanders Collector" title
- Click "Explorer la collection" — search page loads with item cards
- Click on a card — detail page loads with image, metadata, count controls
- Refresh the detail page (F5) — should NOT get a 404 (SPA catch-all works)

- [ ] **Step 4: Verify re-seed is skipped**

```bash
docker compose down
docker compose up -d
docker compose logs seed --follow
```

Expected: `Database already has X items. Skipping seed.` (data persisted in volume).

- [ ] **Step 5: Final commit if any adjustments were needed**

```bash
git add -A
git commit -m "chore: deployment adjustments from e2e testing"
```

Skip this step if no changes were needed.
