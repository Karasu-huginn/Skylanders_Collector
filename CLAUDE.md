# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Skylanders Collector is a full-stack web app for managing a personal Skylanders figurine collection. Users can browse, search, filter, and track which figures they own (with counts and prices).

## Tech Stack

- **Frontend:** React 19 + TypeScript, Vite 7, React Router 7, TanStack React Query 5
- **Backend:** FastAPI (Python), SQLAlchemy 2.0, Pydantic v2, PostgreSQL
- **Build tooling:** SWC via @vitejs/plugin-react-swc

## Development Commands

### Frontend (run from `react/`)
```bash
npm run dev       # Vite dev server with HMR (proxies /api to backend)
npm run build     # TypeScript check + production build
npm run lint      # ESLint
npm run preview   # Preview production build
```

### Backend (run from `fastapi/`)
```bash
uvicorn main:app --reload   # Dev server on http://127.0.0.1:8000
```

### Database Seeding (requires backend running, run from project root)
```bash
python db_maker.py   # Seeds editions, elements, types, and sample items via /api
```

## Architecture

### Backend (`fastapi/`)

- **`main.py`** — App init, all routers mounted under `/api` prefix via `APIRouter`, CORS middleware, table creation via `Base.metadata.create_all`
- **`db.py`** — PostgreSQL engine setup from `.env`, SQLAlchemy 2.0 `DeclarativeBase`, session factory, `get_db` dependency
- **`base_models.py`** — Pydantic schemas: `*Base` for creation (accept IDs), `*Response` for GET responses (nested objects with `from_attributes=True`), `ItemsListResponse` wrapper
- **`models/`** — SQLAlchemy ORM models with `relationship()` definitions. Item FK columns use `Column("db_name", ...)` pattern (Python attr is `type_id` but DB column is `type`) to avoid migration
- **`routers/`** — One router per entity. Item-returning endpoints use `joinedload` for eager loading of all relationships

The backend runs from `fastapi/` as the working directory (imports are relative to that directory, not the project root).

### Frontend (`react/src/`)

- **`main.tsx`** — Router setup (`createBrowserRouter`) and React Query client provider
- **`types.tsx`** — Shared TypeScript interfaces: `Item` (with nested `TypeResponse`, `EditionResponse`, `VariantResponse`, `ElementResponse`), `ItemsListResponse`, `ItemType` union
- **`ItemSearch.tsx`** — Main interface: search, filter, pagination. Fetches from `/api/items`
- **`components/ItemCard.tsx`** — Card with +/- count controls, dynamic element icons, edition logos, and type-based color coding
- **`public/assets/`** — Static assets organized by game edition (SSA, SG, SSF, SSC, STT, SI) plus `icons/` and `logos/`

### API Proxy

In dev, Vite proxies `/api/*` requests to `http://127.0.0.1:8000`. All frontend fetch calls use relative paths (`/api/items`, `/api/editions`, etc.). No CORS issues in dev.

### Routes
```
/              → App.tsx (landing page)
/search        → ItemSearch.tsx (browse & filter)
/item/:item_id → ItemDetails.tsx (detail view)
```

### API Endpoints

All routers follow the same pattern. All under `/api` prefix:
- `/api/items` — search with query params (search, is_captured, pagination), PATCH for count/price updates
- `/api/editions`, `/api/types`, `/api/variants`, `/api/elements` — CRUD + nested `/items` lookups

### Database

PostgreSQL on port 5432. Connection config lives in `fastapi/.env` (see `fastapi/.env.example` for required variables). The DB and tables are auto-created on startup if they don't exist.

Five tables: `item`, `edition`, `type`, `variant`, `element`. Items reference the other four via foreign keys (`edition_id`, `type_id`, `variant_id`, `element_id` in Python; `edition`, `type`, `variant`, `element` as DB column names). Items with `swapper=True` have additional `bot_count`/`top_count` fields.
