# Docker Deployment Design

## Goal

Deploy the Skylanders Collector app on a Windows home PC so it can be accessed from any device (phone, laptop) via Tailscale. The setup must be free, require minimal steps, and auto-seed the database on first run.

## Architecture

### Services (docker-compose.yml)

Three services orchestrated by Docker Compose:

1. **`db`** -- PostgreSQL 16 (alpine image)
   - Internal only, no port exposed to host
   - Data persisted via a named Docker volume (`skylanders-db-data`)
   - Environment variables define the database name, user, and password

2. **`api`** -- FastAPI + React static build (custom Dockerfile)
   - Multi-stage build: Node builds the frontend, Python runs the backend
   - Single exposed port: `8080`
   - Serves both `/api/*` routes and the React SPA
   - Health check on `/api/editions` for readiness

3. **`seed`** -- One-shot seeding container
   - Built from the same Dockerfile as `api` (shares the image, no extra build)
   - Waits for `api` to be healthy via `depends_on` condition
   - Checks if data already exists (GET `/api/items`), skips if populated
   - Runs `db_maker.py` if database is empty
   - `restart: "no"` -- runs once and stays stopped

### Dockerfile (multi-stage)

**Stage 1: `frontend`** (node:22-alpine)
- Copies `react/package.json` and `react/package-lock.json`
- Runs `npm ci`
- Copies `react/` source
- Runs `npm run build` producing `dist/`

**Stage 2: `runtime`** (python:3.12-slim)
- Installs `libpq-dev` (required by psycopg2)
- Copies `fastapi/` directory, installs Python deps via `pip install .`
- Copies `dist/` from Stage 1 into `static/`
- Copies `react/public/assets/` from Stage 1 into `static/assets/`
- Entry point: `uvicorn main:app --host 0.0.0.0 --port 8080`

Final image contains only Python + pre-built static files. Node is not in the production image.

### FastAPI Changes (main.py)

- Mount `StaticFiles` at `/assets` pointing to `static/assets/` (figurine images, icons, logos)
- Mount `StaticFiles` at `/` pointing to `static/` with `html=True` (React JS, CSS, index.html)
- Add a catch-all GET route returning `index.html` for client-side routing (so `/search`, `/item/123` work on direct access and refresh)
- Set CORS to allow all origins (access is already network-restricted by Tailscale)
- Static file mounts only activate if the `static/` directory exists, so local dev workflow is unaffected

### Environment Variables

All values defined in `docker-compose.yml`, no `.env` file needed:

| Variable | Value | Used by |
|----------|-------|---------|
| `POSTGRES_USER` | `postgres` | `db` service (creates the user) |
| `POSTGRES_PASSWORD` | `skylanders` | `db` service (sets the password) |
| `POSTGRES_DB` | `Skylanders` | `db` service (creates the database) |
| `USER` | `postgres` | `api` service (db.py reads it) |
| `PASSWORD` | `skylanders` | `api` service (db.py reads it) |
| `HOST` | `db` | `api` service (Docker DNS resolves to postgres container) |
| `PORT` | `5432` | `api` service |
| `DB_NAME` | `Skylanders` | `api` service |

No code changes needed in `db.py` -- it already reads these via `os.getenv()`.

### Auto-Seed Script (seed.sh)

```
1. Wait for API health (retry loop on GET /api/editions)
2. Check GET /api/items -- if items exist, print "already seeded" and exit 0
3. Run python db_maker.py
4. Exit
```

The `db_maker.py` URL target is changed from hardcoded `localhost:8001` to read from an environment variable (`API_URL`), defaulting to `http://api:8080/api` inside Docker.

### Network Access

**On the host PC:** `http://localhost:8080`

**From other devices (phone, laptop):**
1. Install Tailscale on the host PC and on the device
2. Sign in with the same Tailscale account
3. Access `http://<pc-tailscale-ip>:8080` from the device's browser

No port forwarding, no domain, no public exposure.

## Deployment Steps (end-user)

One-time setup on the Windows PC:

1. Install Docker Desktop
2. Install Tailscale, sign in
3. Clone the repo
4. Run `docker compose up -d`
5. Wait ~1 minute for build + seed on first run
6. Open `http://localhost:8080`

To update after a `git pull`:
```
docker compose up -d --build
```

## Files Created/Modified

| File | Action |
|------|--------|
| `Dockerfile` | Create (project root) |
| `docker-compose.yml` | Create (project root) |
| `seed.sh` | Create (project root) |
| `.dockerignore` | Create (exclude node_modules, .git, __pycache__, etc.) |
| `fastapi/main.py` | Modify (add static file serving + catch-all route) |
| `db_maker.py` | Modify (read API URL from env var with fallback) |

## What Stays Unchanged

- All React components, CSS, TypeScript
- All FastAPI routers and models
- `db.py` (already reads env vars)
- Local dev workflow (`npm run dev` + `uvicorn --reload`)
