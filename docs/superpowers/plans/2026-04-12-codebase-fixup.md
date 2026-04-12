# Codebase Fix-Up Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix all current issues in the Skylanders Collector project — hardcoded values, broken ORM layer, router bugs, frontend asset handling, and project hygiene.

**Architecture:** Bottom-up approach: project cleanup, then ORM modernization, then router fixes, then frontend. Each layer is stable before the next builds on it.

**Tech Stack:** FastAPI, SQLAlchemy 2.0, Pydantic v2, React 19, TypeScript, Vite 7

---

## File Map

**Modify:**
- `fastapi/db.py` — new DeclarativeBase
- `fastapi/base_models.py` — create + response Pydantic schemas
- `fastapi/main.py` — `/api` prefix, CORS, unused import cleanup
- `fastapi/models/item_model.py` — FK rename, relationships, indexes
- `fastapi/models/edition_model.py` — unique constraint, relationship, fix comment
- `fastapi/models/element_model.py` — remove unused import, unique, relationship
- `fastapi/models/type_model.py` — remove unused import, unique, relationship
- `fastapi/models/variant_model.py` — remove unused import, unique, relationship
- `fastapi/routers/item_router.py` — error handling, joinedload, response models
- `fastapi/routers/edition_router.py` — FK rename in filter, joinedload, 404s
- `fastapi/routers/element_router.py` — duplicate names, param naming, joinedload, 404s
- `fastapi/routers/type_router.py` — param naming, rename functions, joinedload, 404s
- `fastapi/routers/variant_router.py` — duplicate names, param naming, joinedload, 404s
- `react/vite.config.ts` — dev proxy
- `react/src/types.tsx` — shared Item and related interfaces
- `react/src/ItemSearch.tsx` — relative fetch URL, import types from types.tsx
- `react/src/ItemDetails.tsx` — relative fetch URL, nested object access
- `react/src/components/ItemCard.tsx` — relative fetch URL, dynamic assets, fix typo, type colors
- `db_maker.py` — new URL and FK field names
- `.gitignore` — ensure .env coverage

**Create:**
- `fastapi/.env.example`
- `fastapi/pyproject.toml`

**Delete:**
- `transfer/` directory
- `transfer.7z`

**Move:**
- `react/src/assets/*` → `react/public/assets/`

**Note on existing database:** `Base.metadata.create_all` does not alter existing tables. After applying these changes (renamed FK columns, new constraints), the existing database will need to be dropped and recreated. Use `db_maker.py` to reseed after recreation.

---

### Task 1: Project Cleanup

**Files:**
- Delete: `transfer/` directory, `transfer.7z`
- Modify: `.gitignore`
- Create: `fastapi/.env.example`, `fastapi/pyproject.toml`

- [ ] **Step 1: Remove transfer/ directory and transfer.7z**

Run:
```bash
cd C:\Users\erwan\Desktop\FOLDERS\Skylanders_Collector
rm -rf transfer/ transfer.7z
```

- [ ] **Step 2: Remove fastapi/.env from git tracking**

The file is already tracked despite `.gitignore` having `.env*` on line 138 — it was committed before the gitignore rule existed.

Run:
```bash
git rm --cached fastapi/.env fastapi/.env.local.db
```

This removes them from git tracking but keeps them on disk.

- [ ] **Step 3: Create fastapi/.env.example**

Create `fastapi/.env.example`:
```
USER="your_db_user"
PASSWORD="your_db_password"
HOST="127.0.0.1"
PORT="5432"
DB_NAME="Skylanders"
HASH_KEY="your_hash_key"
HASH_ALGO="HS256"
```

- [ ] **Step 4: Create fastapi/pyproject.toml**

Create `fastapi/pyproject.toml`:
```toml
[project]
name = "skylanders-collector-api"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn>=0.34.0",
    "sqlalchemy>=2.0.0",
    "sqlalchemy-utils>=0.41.0",
    "python-dotenv>=1.0.0",
    "psycopg2-binary>=2.9.0",
]
```

- [ ] **Step 5: Remove unused imports from backend files**

In `fastapi/main.py`, replace the entire file content with:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db import engine, Base
import routers.edition_router as edition_router
import routers.item_router as item_router
import routers.type_router as type_router
import routers.variant_router as variant_router
import routers.element_router as element_router

app = FastAPI()
app.include_router(edition_router.router)
app.include_router(type_router.router)
app.include_router(variant_router.router)
app.include_router(element_router.router)
app.include_router(item_router.router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


Base.metadata.create_all(bind=engine)
```

Note: CORS and `/api` prefix are updated in Task 5. This step only removes unused imports (`Annotated`, `List`, `Depends`, `HTTPException`, `status`, `Session`) and the unused root endpoint.

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "chore: project cleanup — remove transfer/, untrack .env, add pyproject.toml and .env.example, remove unused imports"
```

---

### Task 2: ORM Modernization — db.py and Models

**Files:**
- Modify: `fastapi/db.py`
- Modify: `fastapi/models/edition_model.py`
- Modify: `fastapi/models/element_model.py`
- Modify: `fastapi/models/type_model.py`
- Modify: `fastapi/models/variant_model.py`
- Modify: `fastapi/models/item_model.py`

- [ ] **Step 1: Rewrite db.py with SQLAlchemy 2.0 DeclarativeBase**

Replace `fastapi/db.py` entirely with:
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy_utils import database_exists, create_database
from dotenv import load_dotenv
import os


class Base(DeclarativeBase):
    pass


def get_engine():
    load_dotenv()
    user = os.getenv("USER")
    password = os.getenv("PASSWORD")
    port = os.getenv("PORT")
    db_name = os.getenv("DB_NAME")
    host = os.getenv("HOST")

    db_url = f"postgresql://{user}:{password}@{host}:{port}/{db_name}"
    if not database_exists(db_url):
        create_database(db_url)
    return create_engine(db_url)


engine = get_engine()
SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

- [ ] **Step 2: Rewrite edition_model.py**

Replace `fastapi/models/edition_model.py` entirely with:
```python
from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import relationship
from db import Base


class Edition(Base):
    __tablename__ = "edition"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    release_date = Column(Date)  # YYYY-MM-DD

    items = relationship("Item", back_populates="edition")
```

- [ ] **Step 3: Rewrite element_model.py**

Replace `fastapi/models/element_model.py` entirely with:
```python
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from db import Base


class Element(Base):
    __tablename__ = "element"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    items = relationship("Item", back_populates="element")
```

- [ ] **Step 4: Rewrite type_model.py**

Replace `fastapi/models/type_model.py` entirely with:
```python
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from db import Base


class Type(Base):
    __tablename__ = "type"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    items = relationship("Item", back_populates="type")
```

- [ ] **Step 5: Rewrite variant_model.py**

Replace `fastapi/models/variant_model.py` entirely with:
```python
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from db import Base


class Variant(Base):
    __tablename__ = "variant"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    items = relationship("Item", back_populates="variant")
```

- [ ] **Step 6: Rewrite item_model.py**

The FK columns use the `Column("db_column_name", ...)` form so the Python attribute is `type_id` but the DB column stays `type`. This avoids needing a database migration.

Replace `fastapi/models/item_model.py` entirely with:
```python
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import relationship
from db import Base


class Item(Base):
    __tablename__ = "item"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    details = Column(String, nullable=True)
    type_id = Column("type", Integer, ForeignKey("type.id"), index=True)
    edition_id = Column("edition", Integer, ForeignKey("edition.id"), index=True)
    image = Column(String, nullable=True)
    count = Column(Integer, default=0)
    price = Column(Integer, default=0)
    variant_id = Column("variant", Integer, ForeignKey("variant.id"), index=True)
    element_id = Column("element", Integer, ForeignKey("element.id"), index=True)
    swapper = Column(Boolean)
    bot_count = Column(Integer, nullable=True)
    top_count = Column(Integer, nullable=True)

    type = relationship("Type", back_populates="items")
    edition = relationship("Edition", back_populates="items")
    variant = relationship("Variant", back_populates="items")
    element = relationship("Element", back_populates="items")
```

- [ ] **Step 7: Commit**

```bash
git add fastapi/db.py fastapi/models/
git commit -m "refactor: modernize ORM — DeclarativeBase, relationships, FK rename, constraints"
```

---

### Task 3: Pydantic Schemas

**Files:**
- Modify: `fastapi/base_models.py`

- [ ] **Step 1: Rewrite base_models.py with create and response schemas**

Replace `fastapi/base_models.py` entirely with:
```python
from datetime import date
from pydantic import BaseModel, ConfigDict
from typing import Optional


# --- Create schemas (accept IDs, used for POST bodies) ---

class EditionBase(BaseModel):
    name: str
    release_date: date


class VariantBase(BaseModel):
    name: str


class TypeBase(BaseModel):
    name: str


class ElementBase(BaseModel):
    name: str


class ItemBase(BaseModel):
    name: str
    details: str
    type_id: int
    edition_id: int
    image: str
    count: int = 0
    price: int = 0
    variant_id: int
    element_id: int
    swapper: bool
    top_count: Optional[int] = None
    bot_count: Optional[int] = None


# --- Response schemas (nested objects, used for GET responses) ---

class EditionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    release_date: date


class VariantResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str


class TypeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str


class ElementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str


class ItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    details: Optional[str]
    type: TypeResponse
    edition: EditionResponse
    image: Optional[str]
    count: int
    price: int
    variant: VariantResponse
    element: ElementResponse
    swapper: bool
    top_count: Optional[int]
    bot_count: Optional[int]


class ItemsListResponse(BaseModel):
    items: list[ItemResponse]
```

- [ ] **Step 2: Commit**

```bash
git add fastapi/base_models.py
git commit -m "refactor: update Pydantic schemas — add response models with nested objects"
```

---

### Task 4: Router Fixes

**Files:**
- Modify: `fastapi/routers/item_router.py`
- Modify: `fastapi/routers/edition_router.py`
- Modify: `fastapi/routers/element_router.py`
- Modify: `fastapi/routers/type_router.py`
- Modify: `fastapi/routers/variant_router.py`

- [ ] **Step 1: Rewrite item_router.py**

Fixes: bare `except:` → `except Exception:`, return 404 when item not found, use joinedload, add response models, use renamed FK attributes.

Replace `fastapi/routers/item_router.py` entirely with:
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_
from sqlalchemy.orm import Session, joinedload
from starlette import status
from typing import Annotated

from models.item_model import Item
from base_models import ItemBase, ItemResponse, ItemsListResponse
from db import get_db

router = APIRouter(prefix="/items", tags=["items"])

db_dep = Annotated[Session, Depends(get_db)]


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_item(db: db_dep, item_base: ItemBase):
    create_item_model = Item(
        name=item_base.name,
        details=item_base.details,
        type_id=item_base.type_id,
        edition_id=item_base.edition_id,
        image=item_base.image,
        count=item_base.count,
        variant_id=item_base.variant_id,
        element_id=item_base.element_id,
        swapper=item_base.swapper,
        bot_count=item_base.bot_count,
        top_count=item_base.top_count,
    )
    db.add(create_item_model)
    db.commit()
    return {"status": 201, "details": "Resource created"}


@router.get("", response_model=ItemsListResponse)
def get_items(
    db: db_dep,
    search: str = "",
    is_captured: bool = False,
    is_uncaptured: bool = False,
    is_duplicate: bool = False,
    page: int = 1,
    limit: int = 10,
):
    filters = []
    if search:
        filters.append(Item.name.ilike("%" + search + "%"))
    if is_captured:
        filters.append(Item.count > 0)
    if is_uncaptured:
        filters.append(Item.count == 0)
    if is_duplicate:
        filters.append(Item.count > 1)
    query = db.query(Item).options(
        joinedload(Item.edition),
        joinedload(Item.element),
        joinedload(Item.type),
        joinedload(Item.variant),
    )
    if filters:
        query = query.filter(and_(*filters))
    items = query.offset((page - 1) * limit).limit(limit).all()
    return {"items": items}


@router.get("/{item_id}", response_model=ItemResponse)
def get_item(db: db_dep, item_id: int):
    item = (
        db.query(Item)
        .options(
            joinedload(Item.edition),
            joinedload(Item.element),
            joinedload(Item.type),
            joinedload(Item.variant),
        )
        .filter(Item.id == item_id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.patch("/{item_id}")
def update_item(
    db: db_dep,
    item_id: int,
    count_add: int = 0,
    price: int = 0,
    details: str = "",
    bot_count_add: int = 0,
    top_count_add: int = 0,
):
    if bot_count_add or top_count_add:
        update_dict = {
            "price": price if price else Item.price,
            "details": details if details else Item.details,
            "top_count": Item.top_count + top_count_add,
            "bot_count": Item.bot_count + bot_count_add,
        }
    else:
        update_dict = {
            "count": Item.count + count_add,
            "price": price if price else Item.price,
            "details": details if details else Item.details,
        }
    try:
        rows = db.query(Item).filter(Item.id == item_id).update(update_dict)
        if rows == 0:
            raise HTTPException(status_code=404, detail="Item not found")
        db.commit()
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=400, detail="Resource could not be updated")
    return {"status": 200, "details": "Resource updated"}
```

- [ ] **Step 2: Rewrite edition_router.py**

Fixes: use `Item.edition_id` in filter, add joinedload, add 404, add response models.

Replace `fastapi/routers/edition_router.py` entirely with:
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from starlette import status
from typing import Annotated

from models.edition_model import Edition
from models.item_model import Item
from base_models import EditionBase, EditionResponse, ItemResponse
from db import get_db

router = APIRouter(prefix="/editions", tags=["editions"])

db_dep = Annotated[Session, Depends(get_db)]


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_edition(db: db_dep, edition_base: EditionBase):
    create_edition_model = Edition(
        name=edition_base.name,
        release_date=edition_base.release_date,
    )
    db.add(create_edition_model)
    db.commit()
    return {"status": 201, "details": "Resource created"}


@router.get("/", response_model=list[EditionResponse])
def get_editions(db: db_dep):
    return db.query(Edition).all()


@router.get("/{edition_id}/items", response_model=list[ItemResponse])
def get_edition_items(db: db_dep, edition_id: int):
    edition = db.query(Edition).filter(Edition.id == edition_id).first()
    if not edition:
        raise HTTPException(status_code=404, detail="Edition not found")
    return (
        db.query(Item)
        .options(
            joinedload(Item.edition),
            joinedload(Item.element),
            joinedload(Item.type),
            joinedload(Item.variant),
        )
        .filter(Item.edition_id == edition_id)
        .all()
    )
```

- [ ] **Step 3: Rewrite element_router.py**

Fixes: rename duplicate `get_item_details` functions, `item_base` → `element_base`, add 404s, add joinedload, add response models.

Replace `fastapi/routers/element_router.py` entirely with:
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from starlette import status
from typing import Annotated

from models.element_model import Element
from models.item_model import Item
from base_models import ElementBase, ElementResponse, ItemResponse
from db import get_db

router = APIRouter(prefix="/elements", tags=["elements"])

db_dep = Annotated[Session, Depends(get_db)]


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_element(db: db_dep, element_base: ElementBase):
    create_element_model = Element(name=element_base.name)
    db.add(create_element_model)
    db.commit()
    return {"status": 201, "details": "Resource created"}


@router.get("/", response_model=list[ElementResponse])
def get_elements(db: db_dep):
    return db.query(Element).all()


@router.get("/{element_id}", response_model=ElementResponse)
def get_element(db: db_dep, element_id: int):
    element = db.query(Element).filter(Element.id == element_id).first()
    if not element:
        raise HTTPException(status_code=404, detail="Element not found")
    return element


@router.get("/{element_id}/items", response_model=list[ItemResponse])
def get_element_items(db: db_dep, element_id: int):
    element = db.query(Element).filter(Element.id == element_id).first()
    if not element:
        raise HTTPException(status_code=404, detail="Element not found")
    return (
        db.query(Item)
        .options(
            joinedload(Item.edition),
            joinedload(Item.element),
            joinedload(Item.type),
            joinedload(Item.variant),
        )
        .filter(Item.element_id == element_id)
        .all()
    )
```

- [ ] **Step 4: Rewrite type_router.py**

Fixes: `item_base` → `type_base`, rename functions for clarity, add 404, add response models.

Replace `fastapi/routers/type_router.py` entirely with:
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status
from typing import Annotated

from models.type_model import Type
from base_models import TypeBase, TypeResponse
from db import get_db

router = APIRouter(prefix="/types", tags=["types"])

db_dep = Annotated[Session, Depends(get_db)]


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_type(db: db_dep, type_base: TypeBase):
    create_type_model = Type(name=type_base.name)
    db.add(create_type_model)
    db.commit()
    return {"status": 201, "details": "Resource created"}


@router.get("/", response_model=list[TypeResponse])
def get_types(db: db_dep):
    return db.query(Type).all()


@router.get("/{type_id}", response_model=TypeResponse)
def get_type(db: db_dep, type_id: int):
    type_obj = db.query(Type).filter(Type.id == type_id).first()
    if not type_obj:
        raise HTTPException(status_code=404, detail="Type not found")
    return type_obj
```

- [ ] **Step 5: Rewrite variant_router.py**

Fixes: rename duplicate `get_item_details` functions, `item_base` → `variant_base`, add 404s, add joinedload, add response models.

Replace `fastapi/routers/variant_router.py` entirely with:
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from starlette import status
from typing import Annotated

from models.variant_model import Variant
from models.item_model import Item
from base_models import VariantBase, VariantResponse, ItemResponse
from db import get_db

router = APIRouter(prefix="/variants", tags=["variants"])

db_dep = Annotated[Session, Depends(get_db)]


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_variant(db: db_dep, variant_base: VariantBase):
    create_variant_model = Variant(name=variant_base.name)
    db.add(create_variant_model)
    db.commit()
    return {"status": 201, "details": "Resource created"}


@router.get("/", response_model=list[VariantResponse])
def get_variants(db: db_dep):
    return db.query(Variant).all()


@router.get("/{variant_id}", response_model=VariantResponse)
def get_variant(db: db_dep, variant_id: int):
    variant = db.query(Variant).filter(Variant.id == variant_id).first()
    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")
    return variant


@router.get("/{variant_id}/items", response_model=list[ItemResponse])
def get_variant_items(db: db_dep, variant_id: int):
    variant = db.query(Variant).filter(Variant.id == variant_id).first()
    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")
    return (
        db.query(Item)
        .options(
            joinedload(Item.edition),
            joinedload(Item.element),
            joinedload(Item.type),
            joinedload(Item.variant),
        )
        .filter(Item.variant_id == variant_id)
        .all()
    )
```

- [ ] **Step 6: Commit**

```bash
git add fastapi/routers/
git commit -m "fix: router fixes — unique function names, 404s, joinedload, response models, error handling"
```

---

### Task 5: main.py — /api Prefix and CORS

**Files:**
- Modify: `fastapi/main.py`

- [ ] **Step 1: Update main.py with /api prefix and tightened CORS**

Replace `fastapi/main.py` entirely with:
```python
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
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
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)
```

All routes are now under `/api` (e.g. `/api/items`, `/api/editions/`). CORS restricted to Vite dev server origin.

- [ ] **Step 2: Commit**

```bash
git add fastapi/main.py
git commit -m "feat: add /api route prefix and tighten CORS to localhost:5173"
```

---

### Task 6: Update db_maker.py

**Files:**
- Modify: `db_maker.py`

- [ ] **Step 1: Update db_maker.py with new URL prefix and FK field names**

Replace `db_maker.py` entirely with:
```python
import requests

DB_URL = "http://localhost:8000/api"


def add_editions():
    editions = [
        {"name": "Spyro's Adventures", "release_date": "2011-10-12"},
        {"name": "Giants", "release_date": "2012-10-17"},
        {"name": "Trap Team", "release_date": "2014-10-05"},
        {"name": "Swap Force", "release_date": "2013-10-13"},
        {"name": "Super Chargers", "release_date": "2015-09-20"},
        {"name": "Imaginators", "release_date": "2016-10-13"},
    ]
    for edition in editions:
        res = requests.post(DB_URL + "/editions/", json=edition)
        print(res.text)


def add_elements():
    element_names = ["Magic", "Earth", "Water", "Fire", "Tech", "Undead", "Air", "Life"]
    for element_name in element_names:
        res = requests.post(DB_URL + "/elements/", json={"name": element_name})
        print(res.text)


def add_types():
    type_names = [
        "Skylander",
        "Giant",
        "Traptanium Crystal Trap",
        "Swapper",
        "Vehicle",
        "Sensei",
        "Villain Sensei",
    ]
    for type_name in type_names:
        res = requests.post(DB_URL + "/types/", json={"name": type_name})
        print(res.text)


def add_skylanders():
    skylanders = [
        {"name": "Bash", "details": "", "type_id": 1, "edition_id": 1, "image": "SSA/Bash.png", "element_id": 2, "variant_id": 1, "swapper": False},
        {"name": "Boomer", "details": "", "type_id": 1, "edition_id": 1, "image": "SSA/Boomer.png", "element_id": 5, "variant_id": 1, "swapper": False},
        {"name": "Camo", "details": "", "type_id": 1, "edition_id": 1, "image": "SSA/Camo.png", "element_id": 8, "variant_id": 1, "swapper": False},
        {"name": "Chop Chop", "details": "", "type_id": 1, "edition_id": 1, "image": "SSA/ChopChop.png", "element_id": 6, "variant_id": 1, "swapper": False},
        {"name": "Cynder", "details": "", "type_id": 1, "edition_id": 1, "image": "SSA/Cynder.png", "element_id": 6, "variant_id": 1, "swapper": False},
        {"name": "Dino-rang", "details": "", "type_id": 1, "edition_id": 1, "image": "SSA/Dino-rang.png", "element_id": 2, "variant_id": 1, "swapper": False},
        {"name": "Double Trouble", "details": "", "type_id": 1, "edition_id": 1, "image": "SSA/DoubleTrouble.png", "element_id": 1, "variant_id": 1, "swapper": False},
        {"name": "Drill Sergeant", "details": "", "type_id": 1, "edition_id": 1, "image": "SSA/DrillSergeant.png", "element_id": 5, "variant_id": 1, "swapper": False},
        {"name": "Drobot", "details": "", "type_id": 1, "edition_id": 1, "image": "SSA/Drobot.png", "element_id": 5, "variant_id": 1, "swapper": False},
        {"name": "Eruptor", "details": "", "type_id": 1, "edition_id": 1, "image": "SSA/Eruptor.png", "element_id": 4, "variant_id": 1, "swapper": False},
        {"name": "Flameslinger", "details": "", "type_id": 1, "edition_id": 1, "image": "SSA/Flameslinger.png", "element_id": 4, "variant_id": 1, "swapper": False},
        {"name": "Ghost Roaster", "details": "", "type_id": 1, "edition_id": 1, "image": "SSA/GhostRoaster.png", "element_id": 6, "variant_id": 1, "swapper": False},
        {"name": "Gill Grunt", "details": "", "type_id": 1, "edition_id": 1, "image": "SSA/GillGrunt.png", "element_id": 3, "variant_id": 1, "swapper": False},
        {"name": "Hex", "details": "", "type_id": 1, "edition_id": 1, "image": "SSA/Hex.png", "element_id": 6, "variant_id": 1, "swapper": False},
        {"name": "Ignitor", "details": "", "type_id": 1, "edition_id": 1, "image": "SSA/Ignitor.png", "element_id": 4, "variant_id": 1, "swapper": False},
        {"name": "Lightning Rod", "details": "", "type_id": 1, "edition_id": 1, "image": "SSA/LightningRod.png", "element_id": 7, "variant_id": 1, "swapper": False},
        {"name": "Prism Break", "details": "", "type_id": 1, "edition_id": 1, "image": "SSA/PrismBreak.png", "element_id": 2, "variant_id": 1, "swapper": False},
        {"name": "Slam Bam", "details": "", "type_id": 1, "edition_id": 1, "image": "SSA/SlamBam.png", "element_id": 3, "variant_id": 1, "swapper": False},
        {"name": "Sonic Boom", "details": "", "type_id": 1, "edition_id": 1, "image": "SSA/SonicBoom.png", "element_id": 7, "variant_id": 1, "swapper": False},
        {"name": "Spyro", "details": "", "type_id": 1, "edition_id": 1, "image": "SSA/Spyro.png", "element_id": 1, "variant_id": 1, "swapper": False},
        {"name": "Stealth Elf", "details": "", "type_id": 1, "edition_id": 1, "image": "SSA/StealthElf.png", "element_id": 8, "variant_id": 1, "swapper": False},
        {"name": "Stump Smash", "details": "", "type_id": 1, "edition_id": 1, "image": "SSA/StumpSmash.png", "element_id": 8, "variant_id": 1, "swapper": False},
        {"name": "Sunburn", "details": "", "type_id": 1, "edition_id": 1, "image": "SSA/Sunburn.png", "element_id": 4, "variant_id": 1, "swapper": False},
        {"name": "Terrafin", "details": "", "type_id": 1, "edition_id": 1, "image": "SSA/Terrafin.png", "element_id": 2, "variant_id": 1, "swapper": False},
        {"name": "Trigger Happy", "details": "", "type_id": 1, "edition_id": 1, "image": "SSA/TriggerHappy.png", "element_id": 5, "variant_id": 1, "swapper": False},
        {"name": "Voodood", "details": "", "type_id": 1, "edition_id": 1, "image": "SSA/Voodood.png", "element_id": 1, "variant_id": 1, "swapper": False},
        {"name": "Warnado", "details": "", "type_id": 1, "edition_id": 1, "image": "SSA/Warnado.png", "element_id": 7, "variant_id": 1, "swapper": False},
        {"name": "Wham-Shell", "details": "", "type_id": 1, "edition_id": 1, "image": "SSA/Wham-Shell.png", "element_id": 3, "variant_id": 1, "swapper": False},
        {"name": "Whirlwind", "details": "", "type_id": 1, "edition_id": 1, "image": "SSA/Whirlwind.png", "element_id": 7, "variant_id": 1, "swapper": False},
        {"name": "Wrecking Ball", "details": "", "type_id": 1, "edition_id": 1, "image": "SSA/WreckingBall.png", "element_id": 1, "variant_id": 1, "swapper": False},
        {"name": "Zap", "details": "", "type_id": 1, "edition_id": 1, "image": "SSA/Zap.png", "element_id": 3, "variant_id": 1, "swapper": False},
        {"name": "Zook", "details": "", "type_id": 1, "edition_id": 1, "image": "SSA/Zook.png", "element_id": 8, "variant_id": 1, "swapper": False},
    ]
    for skylander in skylanders:
        res = requests.post(DB_URL + "/items/", json=skylander)
        print(res.text)


if __name__ == "__main__":
    add_editions()
    add_elements()
    add_types()
    add_skylanders()
```

Note: all seed functions are now called by default (uncommented) since you'll need to reseed after the DB schema changes.

- [ ] **Step 2: Commit**

```bash
git add db_maker.py
git commit -m "fix: update db_maker.py — /api prefix and renamed FK fields"
```

---

### Task 7: Frontend — Vite Proxy

**Files:**
- Modify: `react/vite.config.ts`

- [ ] **Step 1: Add proxy to vite.config.ts**

Replace `react/vite.config.ts` entirely with:
```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      }
    }
  }
})
```

- [ ] **Step 2: Commit**

```bash
git add react/vite.config.ts
git commit -m "feat: add Vite dev proxy for /api requests"
```

---

### Task 8: Frontend — Types, Assets, Fetch URLs, and Component Fixes

**Files:**
- Move: `react/src/assets/*` → `react/public/assets/`
- Modify: `react/src/types.tsx`
- Modify: `react/src/ItemSearch.tsx` (relative URL + shared types)
- Modify: `react/src/ItemDetails.tsx` (relative URL + nested object access)
- Modify: `react/src/components/ItemCard.tsx` (relative URL + dynamic assets + fix typo + type colors)

- [ ] **Step 1: Move assets from src/assets/ to public/assets/**

```bash
cd C:\Users\erwan\Desktop\FOLDERS\Skylanders_Collector\react
mkdir -p public/assets
cp -r src/assets/* public/assets/
rm -rf src/assets/
```

Files in `public/` are served at the root URL by Vite. So `public/assets/icons/fire.png` is accessible at `/assets/icons/fire.png`.

- [ ] **Step 2: Update types.tsx with shared interfaces**

The `Item` interface currently lives in `ItemSearch.tsx` and is imported by other components. Now that items have nested objects (from the ORM changes), update the shared types.

Replace `react/src/types.tsx` entirely with:
```typescript
export type ItemType =
    | "Skylander"
    | "Giant"
    | "Traptanium Crystal Trap"
    | "Swapper"
    | "Vehicle"
    | "Sensei"
    | "Villain Sensei"

export interface EditionResponse {
    id: number;
    name: string;
    release_date: string;
}

export interface ElementResponse {
    id: number;
    name: string;
}

export interface TypeResponse {
    id: number;
    name: string;
}

export interface VariantResponse {
    id: number;
    name: string;
}

export interface Item {
    id: number;
    name: string;
    details?: string;
    type: TypeResponse;
    edition: EditionResponse;
    image?: string;
    count: number;
    price: number;
    variant: VariantResponse;
    element: ElementResponse;
    swapper: boolean;
    bot_count?: number;
    top_count?: number;
}

export interface ItemsListResponse {
    items: Item[];
}
```

- [ ] **Step 3: Update ItemSearch.tsx — use shared types**

Replace `react/src/ItemSearch.tsx` entirely with:
```typescript
import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { ItemCard } from "./components/ItemCard";
import type { ItemsListResponse } from "./types";

export function ItemSearch() {
    const [search, setSearch] = useState("");
    const [page, setPage] = useState(1);
    const [isCaptured, setIsCaptured] = useState(false);
    const [isUncaptured, setIsUncaptured] = useState(false);
    const [isDuplicate, setIsDuplicate] = useState(false);
    const { isLoading, isError, error, data, refetch } = useQuery<ItemsListResponse>({
        queryKey: ['item_search', search, page, isCaptured, isUncaptured, isDuplicate],
        queryFn: async () => {
            const res = await fetch(`/api/items?search=${search}&page=${page}&is_captured=${isCaptured}&is_uncaptured=${isUncaptured}&is_duplicate=${isDuplicate}`);
            if (!res.ok) throw new Error("Network response was not ok");
            return res.json();
        },
        staleTime: 1000 * 60 * 5,
    });

    const handleSearch = (e: React.FormEvent) => {
        e.preventDefault();
        refetch();
    }

    const changePage = (page_add: number) => {
        setPage(page + page_add);
        refetch();
    }

    const filterCount = (state_captured: boolean, state_uncaptured: boolean, state_duplicate: boolean) => {
        setIsCaptured(state_captured);
        setIsUncaptured(state_uncaptured);
        setIsDuplicate(state_duplicate);
        setPage(1);
    }

    return <>
        <form onSubmit={handleSearch} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
            <span>
                <label htmlFor="search">Nom de la figurine : </label>
                <input id="search" name="search" type="text" placeholder="Nom de la figurine..." value={search} onChange={(e) => setSearch(e.target.value)} />
            </span>
            <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
                <span>
                    <input type="checkbox" name="is_captured" checked={isCaptured} onChange={() => filterCount(!isCaptured, false, false)} />
                    <label htmlFor="search">Capturés</label>
                </span>
                <span>
                    <input type="checkbox" name="is_uncaptured" checked={isUncaptured} onChange={() => filterCount(false, !isUncaptured, false)} />
                    <label htmlFor="search">À capturer</label>
                </span>
                <span>
                    <input type="checkbox" name="is_duplicate" checked={isDuplicate} onChange={() => filterCount(false, false, !isDuplicate)} />
                    <label htmlFor="search">Doublons</label>
                </span>
            </div>
            <button type="submit">Rechercher</button>
        </form>

        {isLoading && <div>Chargement...</div>}
        {isError && <div>Erreur : {(error as Error).message}</div>}
        {data && (
            <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: "1rem" }}>
                {data.items.length > 0 ? (
                    data.items.map((result) => (
                        <ItemCard key={result.id} item={result} />
                    ))
                ) : (
                    <h3>Aucun résultat trouvé. Essayez d'ajuster vos critères de recherche.</h3>
                )}
            </div>
        )}
        {page > 1 && <button onClick={() => changePage(-1)}>Page Précédente</button>}
        {data && data.items.length == 10 && <button onClick={() => changePage(1)}>Page Suivante</button>}
    </>
}
```

- [ ] **Step 4: Update ItemDetails.tsx — nested object access**

Replace `react/src/ItemDetails.tsx` entirely with:
```typescript
import type { Item } from "./types";
import { useQuery } from "@tanstack/react-query";
import { useParams } from "react-router";

export function ItemDetails() {
    const { item_id } = useParams();
    const { isLoading, isError, error, data } = useQuery<Item>({
        queryKey: ['item_details', item_id],
        queryFn: async () => {
            const res = await fetch(`/api/items/${item_id}`);
            if (!res.ok) throw new Error("Network response was not ok");
            return res.json();
        }
    });

    return <>
        <div style={{ display: "flex", flexDirection: "column" }}>
            {isLoading && <div>Chargement...</div>}
            {isError && <div>Erreur : {(error as Error).message}</div>}
            <h1>{data?.name}</h1>
            <h2>{data?.id}</h2>
            <h2>{data?.type.name}</h2>
            <h2>{data?.element.name}</h2>
            <h2>{data?.variant.name}</h2>
            <h2>{data?.count}</h2>
        </div>
    </>
}
```

- [ ] **Step 5: Update ItemCard.tsx — dynamic assets, fix typo, enable type colors**

The element icon files are: `air.png`, `earth.png`, `fire.png`, `life.png`, `magic.png`, `mechanic.png`, `undead.png`, `water.png`. All map from `element.name.toLowerCase()` except "Tech" → "mechanic".

The edition logo files are: `SSA.png`, `SG.png`, `STT.png`, `SSF.png`, `SSC.png`, `SI.png`. These need an explicit mapping from edition name.

Replace `react/src/components/ItemCard.tsx` entirely with:
```typescript
import { Link } from "react-router";
import type { Item, ItemType } from "../types";
import './ItemCard.css'
import { useState } from "react";
import { useMutation } from "@tanstack/react-query";

interface ItemCardProps {
    item: Item;
}

interface PatchRequest {
    itemId: number;
    newCount: number;
}

const patchCount = async (requestInfos: PatchRequest) => {
    const response = await fetch(`/api/items/${requestInfos.itemId}?count_add=${requestInfos.newCount}`, {
        method: "PATCH",
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
        }
    })
    return response
}

const typeColors: Record<ItemType, string> = {
    "Skylander": "type-skylander",
    "Giant": "type-giant",
    "Traptanium Crystal Trap": "type-traptanium-crystal-trap",
    "Swapper": "type-swapper",
    "Vehicle": "type-vehicle",
    "Sensei": "type-sensei",
    "Villain Sensei": "type-villain-sensei",
}

const elementIconMap: Record<string, string> = {
    "Magic": "magic.png",
    "Earth": "earth.png",
    "Water": "water.png",
    "Fire": "fire.png",
    "Tech": "mechanic.png",
    "Undead": "undead.png",
    "Air": "air.png",
    "Life": "life.png",
}

const editionLogoMap: Record<string, string> = {
    "Spyro's Adventures": "SSA.png",
    "Giants": "SG.png",
    "Trap Team": "STT.png",
    "Swap Force": "SSF.png",
    "Super Chargers": "SSC.png",
    "Imaginators": "SI.png",
}

export function ItemCard(props: ItemCardProps) {
    const { mutate } = useMutation({ mutationFn: patchCount });
    const { item } = props;
    const typeColor = typeColors[item.type.name as ItemType] || "";
    const [itemCount, setItemCount] = useState(item.count);
    const updateCount = (count_add: number) => {
        mutate({ itemId: item.id, newCount: count_add })
        setItemCount(itemCount + count_add);
    }
    return <>
        <div className={`item-card ${typeColor}`}>
            <Link to={`/item/${item.id}`} className="item-card-top">
                <img src={`/assets/icons/${elementIconMap[item.element.name]}`} className="skylander-element" />
                <h1 className="skylander-name">{item.name}</h1>
                <div className="shadow">
                    <img src={`/assets/${item.image}`} className="skylander-img" />
                </div>
                <p className="skylander-variant">{item.variant.name}</p>
            </Link>
            <div className="item-card-bottom">
                <button className="skylander-count-plus" onClick={() => updateCount(1)}>+</button>
                <p className="skylander-count">{itemCount}</p>
                <button className="skylander-count-minus" onClick={() => updateCount(-1)}>-</button>
                <img src={`/assets/logos/${editionLogoMap[item.edition.name]}`} width={300} height={200} className="skylander-edition" />
            </div>
        </div>
    </>
}
```

- [ ] **Step 6: Commit**

```bash
git add react/public/assets/ react/src/types.tsx react/src/ItemSearch.tsx react/src/ItemDetails.tsx react/src/components/ItemCard.tsx
git rm -r --cached react/src/assets/ 2>/dev/null; true
git add -u react/src/assets/
git commit -m "feat: frontend overhaul — relative /api URLs, shared types, dynamic assets, enable type colors"
```

---

### Task 9: Verify End-to-End

- [ ] **Step 1: Drop and recreate the database**

The schema changes (renamed FK columns, unique constraints, indexes) require a fresh database since `create_all` doesn't alter existing tables.

```bash
cd C:\Users\erwan\Desktop\FOLDERS\Skylanders_Collector\fastapi
# Drop the Skylanders database via psql (adjust credentials as needed)
psql -U postgres -h 127.0.0.1 -c "DROP DATABASE IF EXISTS \"Skylanders\";"
```

- [ ] **Step 2: Start the backend**

```bash
cd C:\Users\erwan\Desktop\FOLDERS\Skylanders_Collector\fastapi
uvicorn main:app --reload
```

The database and tables will be auto-created on startup.

- [ ] **Step 3: Seed the database**

In a separate terminal:
```bash
cd C:\Users\erwan\Desktop\FOLDERS\Skylanders_Collector
python db_maker.py
```

Expected: each POST returns `{"status":201,"details":"Resource created"}`.

- [ ] **Step 4: Verify API responses**

Test that items come back with nested objects:
```bash
curl http://localhost:8000/api/items?search=Spyro
```

Expected: items array with `"edition": {"id": 1, "name": "Spyro's Adventures", "release_date": "2011-10-12"}` instead of `"edition": 1`.

- [ ] **Step 5: Start the frontend and test**

```bash
cd C:\Users\erwan\Desktop\FOLDERS\Skylanders_Collector\react
npm run dev
```

Open `http://localhost:5173/search` in the browser. Verify:
- Search works and returns item cards
- Item cards show the correct element icon (not always fire)
- Item cards show the correct edition logo (not always SSA)
- Item cards are colored by type (purple for Skylander)
- Variant name displays as text (not a number)
- +/- count buttons work
- Clicking a card navigates to `/item/:id` and shows names (not IDs)
