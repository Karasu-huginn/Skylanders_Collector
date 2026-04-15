# Skylanders Collector

A full-stack web app for managing your personal Skylanders figurine collection. Browse, search, and filter across all game editions — track which figures you own, how many copies, and their prices.

## Overview

Skylanders Collector lets you catalog your entire Skylanders collection in one place. The app ships with data for 800+ items spanning all six game editions (Spyro's Adventure through Imaginators), organized by element, type, and variant.

**Key capabilities:**

- **Search & filter** — Find items by name, filter by ownership status (captured, uncaptured, duplicates)
- **Inventory tracking** — Increment/decrement counts per figure with one click
- **Price management** — Record and edit prices per item (EUR)
- **Edition browsing** — Items organized across SSA, Giants, Swap Force, Trap Team, SuperChargers, and Imaginators
- **Element & type metadata** — Each item tagged with its element (Magic, Fire, Water, etc.) and type (Skylander, Giant, Swapper, Sensei, etc.)

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19, TypeScript, Vite 7, React Router 7, TanStack React Query 5 |
| Backend | FastAPI, SQLAlchemy 2.0, Pydantic v2 |
| Database | PostgreSQL 16 |
| Deployment | Docker (multi-stage build), Docker Compose |

## Getting Started

### With Docker (recommended)

The fastest way to get everything running — database, API, frontend, and seed data:

```bash
docker compose up --build
```

The app will be available at `http://localhost:8080` once all services are healthy. The seed service automatically populates the database with the full Skylanders catalog on first run.

### Local Development

#### Prerequisites

- Node.js 22+
- Python 3.11+
- PostgreSQL 16+

#### 1. Set up the database

Create a PostgreSQL database named `Skylanders`, then configure the connection in `fastapi/.env`:

```env
USER=postgres
PASSWORD=your_password
HOST=localhost
PORT=5432
DB_NAME=Skylanders
```

> [!TIP]
> See `fastapi/.env.example` for the full list of required variables.

#### 2. Start the backend

```bash
cd fastapi
pip install -e .
uvicorn main:app --reload
```

The API runs on `http://localhost:8000`. Tables are auto-created on startup.

#### 3. Seed the database

```bash
python db_maker.py
```

This reads `skylanders_data.json` and populates all editions, elements, types, variants, and items via the API.

#### 4. Start the frontend

```bash
cd react
npm install
npm run dev
```

The Vite dev server starts on `http://localhost:5173` and proxies `/api` requests to the backend automatically.

## Project Structure

```
├── react/                  # Frontend SPA
│   ├── src/
│   │   ├── App.tsx         # Landing page
│   │   ├── ItemSearch.tsx  # Browse, search & filter
│   │   ├── ItemDetails.tsx # Item detail view
│   │   ├── components/
│   │   │   └── ItemCard.tsx
│   │   └── types.tsx       # Shared TypeScript interfaces
│   └── public/assets/      # Figurine images, element icons, edition logos
├── fastapi/                # Backend API
│   ├── main.py             # App init, router mounting, CORS
│   ├── db.py               # Database engine & session
│   ├── base_models.py      # Pydantic request/response schemas
│   ├── models/             # SQLAlchemy ORM models
│   └── routers/            # One router per entity
├── Dockerfile              # Multi-stage build (Node + Python)
├── docker-compose.yml      # PostgreSQL + API + seed services
├── db_maker.py             # Database seeding script
└── skylanders_data.json    # Full collection data (800+ items)
```

## API

All endpoints are under the `/api` prefix.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/items` | GET | Search items with filters (`search`, `is_captured`, `is_duplicate`, `page`, `limit`) |
| `/api/items/{id}` | GET | Get a single item with full metadata |
| `/api/items/{id}` | PATCH | Update count or price (`count_add`, `price`) |
| `/api/editions` | GET | List all game editions |
| `/api/elements` | GET | List all elements |
| `/api/types` | GET | List all figure types |
| `/api/variants` | GET | List all variants |

## Architecture

```
┌────────────┐     /api/*      ┌──────────┐      ┌────────────┐
│   React    │ ───────────────>│ FastAPI  │ ────>│ PostgreSQL │
│   (Vite)   │<─── JSON ──────>│          │<─────│            │
└────────────┘                 └──────────┘      └────────────┘
```

- **Dev mode**: Vite proxies `/api` requests to the FastAPI backend
- **Production**: FastAPI serves the built SPA from `/static/` and handles API routes directly
- **Docker Compose**: Three services — `db` (PostgreSQL), `api` (FastAPI + static frontend), `seed` (one-shot data loader)
