# Codebase Fix-Up Design

Fix all current issues in the Skylanders Collector project: hardcoded values, broken ORM layer, router bugs, frontend asset handling, and project hygiene.

## Approach

Bottom-up: fix the foundation (project structure, ORM), then the layer above (routers), then the top (frontend). Each layer is stable before the next builds on it.

## Section 1: Project Cleanup

- Remove `transfer/` directory and `transfer.7z` from the repo
- Remove `fastapi/.env` from git tracking; ensure `.gitignore` covers `*.env` files under `fastapi/`
- Add `fastapi/.env.example` with placeholder values (USER, PASSWORD, HOST, PORT, DB_NAME, HASH_KEY)
- Add `fastapi/pyproject.toml` declaring all Python dependencies: fastapi, uvicorn, sqlalchemy, sqlalchemy-utils, python-dotenv, psycopg2-binary
- Remove unused imports: `List` from `main.py`, `Date` from `element_model.py`, `type_model.py`, `variant_model.py`

## Section 2: ORM Modernization

### DeclarativeBase migration

Replace deprecated `declarative_base()` in `db.py` with SQLAlchemy 2.0 class-based approach:

```python
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass
```

Update all 5 models to inherit from the new `Base`.

### Item model FK column rename

Rename foreign key columns to avoid shadowing relationship names:
- `type` → `type_id`
- `edition` → `edition_id`
- `variant` → `variant_id`
- `element` → `element_id`

### Relationships

Add `relationship()` on the Item model:
- `type: Mapped["Type"] = relationship(back_populates="items")`
- `edition: Mapped["Edition"] = relationship(back_populates="items")`
- `variant: Mapped["Variant"] = relationship(back_populates="items")`
- `element: Mapped["Element"] = relationship(back_populates="items")`

Add corresponding `items` back-references on Edition, Element, Type, Variant models.

### Constraints

- Add `index=True` on FK columns (`type_id`, `edition_id`, `variant_id`, `element_id`) in Item
- Add `unique=True` on `name` column in Edition, Element, Type, Variant models

### Pydantic schemas

Update `base_models.py`:
- Add response schemas that include nested objects (e.g. `ItemResponse` with `edition: EditionBase` instead of `edition: int`)
- Keep existing create/update schemas that accept IDs

### Other

- Fix misleading date format comment in edition model ("YYYY-MM-DD hh:mm" → `Date` has no time component)

## Section 3: Router Fixes

### Duplicate function names

- `element_router.py`: rename the two `get_item_details()` functions to unique names (e.g. `get_element` and `get_element_items`)
- `variant_router.py`: same pattern (two `get_item_details()` functions)
- `type_router.py`: no duplicate names, but rename `get_items` → `get_types` and `get_item_details` → `get_type` for clarity

### Parameter naming

- `element_router.py`: `item_base` → `element_base`
- `type_router.py`: `item_base` → `type_base`
- `variant_router.py`: `item_base` → `variant_base`

### Error handling

- `item_router.py`: replace bare `except:` with `except Exception:`
- All routers: return 404 when an entity is not found (instead of `None`)

### Query updates

- Use `joinedload` (or similar) for queries that return items with related data
- Add response models to endpoints using updated Pydantic schemas

### db_maker.py

- Update `db_maker.py` at root: this script seeds via the HTTP API (`requests.post`), so update the base URL from `http://localhost:8000` to `http://localhost:8000/api` and update JSON payload keys from `type`/`edition`/`variant`/`element` to `type_id`/`edition_id`/`variant_id`/`element_id`

## Section 4: Frontend Fixes

### Vite proxy

Configure `vite.config.ts` to proxy `/api` requests to `http://127.0.0.1:8000`:

```typescript
server: {
  proxy: {
    '/api': {
      target: 'http://127.0.0.1:8000',
      changeOrigin: true,
    }
  }
}
```

### Backend route prefix

Add `/api` prefix to all FastAPI routes (either in `main.py` via a global prefix or at the router level).

### Frontend fetch calls

Replace all hardcoded URLs (`http://127.0.0.1:8000/...` and `http://localhost:8000/...`) with relative paths (`/api/items`, `/api/editions`, etc.) in:
- `ItemSearch.tsx`
- `ItemDetails.tsx`
- `components/ItemCard.tsx`

### Asset handling

- Move `react/src/assets/` contents to `react/public/assets/`
- Replace hardcoded asset paths with dynamic mapping:
  - Element icon: map `item.element.name` → `/assets/icons/{element}.png`
  - Edition logo: map `item.edition.name` → `/assets/logos/{edition}.png`
  - Item image: use `/assets/{item.image}`
- Remove hardcoded `"src/assets/icons/fire.png"` and `"src/assets/logos/SSA.png"`

### Code quality

- Fix `patchRequst` typo → `PatchRequest` in `ItemCard.tsx`

### CORS

- Tighten `allow_origins` in `main.py` — replace `"*"` with `["http://localhost:5173"]` (Vite dev server). In production (Docker), this will be configured to the actual frontend origin.

## Out of Scope

These are known but intentionally deferred:
- Docker setup
- Authentication/authorization
- Full pagination on all list endpoints
- Error boundaries in React
- Automated type generation (frontend ↔ backend)
- Swapper item logic (bot_count/top_count)
