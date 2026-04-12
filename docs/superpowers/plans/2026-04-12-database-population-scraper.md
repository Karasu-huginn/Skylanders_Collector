# Database Population Scraper Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Scrape all Skylanders figure data from skylanderscharacterlist.com via its WordPress REST API, download images, and import everything into the local database.

**Architecture:** Two-phase approach. Phase 1 (`scraper.py`) fetches all posts from the WP REST API, parses categories to resolve edition/element/type/variant, downloads images, and outputs `skylanders_data.json`. Phase 2 (`db_maker.py` rewrite) reads that JSON and POSTs to the FastAPI backend.

**Tech Stack:** Python 3, requests, beautifulsoup4, FastAPI backend (already exists)

**Spec:** `docs/superpowers/specs/2026-04-12-database-population-scraper-design.md`

---

### Task 1: Make element_id nullable in backend schema

**Files:**
- Modify: `fastapi/models/item_model.py:18`
- Modify: `fastapi/base_models.py:34`
- Modify: `fastapi/base_models.py:78`

- [ ] **Step 1: Update the SQLAlchemy model**

In `fastapi/models/item_model.py`, change line 18 from:

```python
    element_id = Column("element", Integer, ForeignKey("element.id"), index=True)
```

to:

```python
    element_id = Column("element", Integer, ForeignKey("element.id"), index=True, nullable=True)
```

- [ ] **Step 2: Update ItemBase Pydantic schema**

In `fastapi/base_models.py`, change line 34 from:

```python
    element_id: int
```

to:

```python
    element_id: Optional[int] = None
```

- [ ] **Step 3: Update ItemResponse Pydantic schema**

In `fastapi/base_models.py`, change line 78 from:

```python
    element: ElementResponse
```

to:

```python
    element: Optional[ElementResponse] = None
```

- [ ] **Step 4: Verify the backend starts**

Run from `fastapi/`:
```bash
cd fastapi && uvicorn main:app --reload --port 8001
```

Expected: Server starts without errors. The table will be recreated with the nullable element column on next startup (if using `create_all`).

- [ ] **Step 5: Commit**

```bash
git add fastapi/models/item_model.py fastapi/base_models.py
git commit -m "feat: make element_id nullable to support element-less figures"
```

---

### Task 2: Install beautifulsoup4

**Files:**
- None (dependency installation only)

- [ ] **Step 1: Install the package**

```bash
pip install beautifulsoup4
```

Expected: Successfully installed beautifulsoup4.

- [ ] **Step 2: Verify import works**

```bash
python -c "from bs4 import BeautifulSoup; print('OK')"
```

Expected: `OK`

---

### Task 3: Write scraper.py — complete scraper

**Files:**
- Create: `scraper.py`

This is the full scraper file. It fetches from the WP REST API, parses post categories and HTML content, downloads images, and outputs `skylanders_data.json`.

- [ ] **Step 1: Create scraper.py with all code**

Create `scraper.py` in the project root with:

```python
import json
import os
import time
from urllib.parse import unquote, urlparse

import requests
from bs4 import BeautifulSoup

WP_API = "https://skylanderscharacterlist.com/wp-json/wp/v2"
ASSETS_DIR = os.path.join("react", "public", "assets")
DELAY = 0.5

# ── Category mappings ──────────────────────────────────────────────

EDITION_CATEGORIES = {
    4: {"db_name": "Spyro's Adventures", "release_date": "2011-10-12", "code": "SSA"},
    47: {"db_name": "Giants", "release_date": "2012-10-17", "code": "SG"},
    66: {"db_name": "Swap Force", "release_date": "2013-10-13", "code": "SSF"},
    134: {"db_name": "Trap Team", "release_date": "2014-10-05", "code": "STT"},
    234: {"db_name": "Super Chargers", "release_date": "2015-09-20", "code": "SSC"},
    276: {"db_name": "Imaginators", "release_date": "2016-10-13", "code": "SI"},
}

ELEMENT_CATEGORIES = {
    6: "Air",
    10: "Earth",
    16: "Fire",
    20: "Life",
    25: "Magic",
    30: "Tech",
    35: "Undead",
    40: "Water",
    222: "Dark",
}

TYPE_CATEGORIES = {
    3: "Skylander",
    46: "Skylander",
    48: "LightCore",
    50: "Giant",
    67: "Swapper",
    89: "Adventure Pack",
    90: "Magic Item",
    103: "Level",
    105: "Battle Pack",
    135: "Trap Master",
    203: "Eon's Elite",
    235: "SuperCharger",
    277: "Sensei",
    278: "Creation Crystal",
    279: "Battlecast",
}

SERIES_CATEGORIES = {3: "Series 1", 46: "Series 2"}

VARIANT_CATEGORY_ID = 78


# ── API helpers ────────────────────────────────────────────────────


def fetch_paginated(endpoint, params=None):
    """Fetch all pages from a WP REST API endpoint (4 results/page cap)."""
    all_results = []
    page = 1
    while True:
        p = {**(params or {}), "page": page, "per_page": 100}
        time.sleep(DELAY)
        resp = requests.get(f"{WP_API}/{endpoint}", params=p)
        if resp.status_code == 400:
            break
        resp.raise_for_status()
        data = resp.json()
        if not data:
            break
        all_results.extend(data)
        page += 1
    return all_results


def get_media_url(media_id):
    """Resolve a WP media ID to its source URL."""
    if not media_id:
        return None
    time.sleep(DELAY)
    resp = requests.get(f"{WP_API}/media/{media_id}")
    if resp.status_code != 200:
        return None
    return resp.json().get("source_url")


# ── HTML parsing ───────────────────────────────────────────────────


def parse_html_table(html_content):
    """Parse key-value pairs from the Basic Info table in a post's HTML."""
    soup = BeautifulSoup(html_content, "html.parser")
    info = {}
    for table in soup.find_all("table"):
        for row in table.find_all("tr"):
            th = row.find("th")
            td = row.find("td")
            if th and td:
                key = th.get_text(strip=True).rstrip(":")
                value = td.get_text(strip=True)
                info[key] = value
    return info


# ── Detection functions ────────────────────────────────────────────


def detect_edition(post_categories):
    """Return the edition info dict for the first matching edition category."""
    for cat_id in post_categories:
        if cat_id in EDITION_CATEGORIES:
            return EDITION_CATEGORIES[cat_id]
    return None


def detect_element(post_categories):
    """Return the element name for the first matching element category."""
    for cat_id in post_categories:
        if cat_id in ELEMENT_CATEGORIES:
            return ELEMENT_CATEGORIES[cat_id]
    return None


def detect_type(post_categories, html_info):
    """Determine the DB type from WP categories, with HTML fallback."""
    for cat_id in post_categories:
        if cat_id in TYPE_CATEGORIES:
            return TYPE_CATEGORIES[cat_id]

    # Fallback: parse HTML fields
    series_field = html_info.get("Series", "")
    if "Vehicle" in series_field:
        return "Vehicle"

    return "Skylander"


def detect_variant(post_categories, html_info):
    """Determine variant name. 'Standard' unless category 78 is present."""
    if VARIANT_CATEGORY_ID in post_categories:
        variant_type = html_info.get("Variant Type", "")
        if variant_type:
            return variant_type
        return "Variant"
    return "Standard"


def is_villain_sensei(post_categories, html_info, name):
    """Check if a Sensei post is actually a Villain Sensei."""
    if 277 not in post_categories:
        return False
    battle_class = html_info.get("Battle Class", "")
    if "Villain" in battle_class or "Villain" in name:
        return True
    return False


def build_item_name(title, post_categories):
    """Build item name, appending '(Series N)' for core Skylander types."""
    name = title.strip()
    for cat_id in post_categories:
        if cat_id in SERIES_CATEGORIES:
            series_label = SERIES_CATEGORIES[cat_id]
            if series_label not in name:
                name = f"{name} ({series_label})"
            break
    return name


# ── Image downloading ──────────────────────────────────────────────


def download_image(url, edition_code):
    """Download an image and return its relative asset path (EDITION_CODE/filename)."""
    parsed = urlparse(url)
    filename = os.path.basename(unquote(parsed.path))
    dir_path = os.path.join(ASSETS_DIR, edition_code)
    os.makedirs(dir_path, exist_ok=True)
    file_path = os.path.join(dir_path, filename)

    if os.path.exists(file_path):
        return f"{edition_code}/{filename}"

    time.sleep(DELAY)
    resp = requests.get(url)
    if resp.status_code == 200:
        with open(file_path, "wb") as f:
            f.write(resp.content)
        return f"{edition_code}/{filename}"

    print(f"    WARNING: failed to download {url}")
    return None


# ── Main scraping orchestration ────────────────────────────────────


def scrape_all():
    seen_post_ids = set()
    all_items = []
    collected_editions = {}
    collected_elements = set()
    collected_types = set()
    collected_variants = set()

    for edition_cat_id, edition_info in EDITION_CATEGORIES.items():
        edition_name = edition_info["db_name"]
        edition_code = edition_info["code"]
        print(f"\n--- Scraping {edition_name} ({edition_code}) ---")

        posts = fetch_paginated("posts", {"categories": edition_cat_id})
        print(f"  Found {len(posts)} posts")

        for post in posts:
            post_id = post["id"]
            if post_id in seen_post_ids:
                continue
            seen_post_ids.add(post_id)

            categories = post.get("categories", [])
            title = post["title"]["rendered"]
            html_content = post.get("content", {}).get("rendered", "")
            html_info = parse_html_table(html_content)

            # Detect all fields
            element = detect_element(categories)
            item_type = detect_type(categories, html_info)
            variant = detect_variant(categories, html_info)
            name = build_item_name(title, categories)

            # Villain Sensei override
            if item_type == "Sensei" and is_villain_sensei(categories, html_info, name):
                item_type = "Villain Sensei"

            is_swapper = item_type == "Swapper"

            # Resolve and download image
            media_id = post.get("featured_media")
            image_url = get_media_url(media_id)
            image_path = None
            if image_url:
                image_path = download_image(image_url, edition_code)

            # Collect unique lookup values
            collected_editions[edition_name] = edition_info["release_date"]
            if element:
                collected_elements.add(element)
            collected_types.add(item_type)
            collected_variants.add(variant)

            item = {
                "name": name,
                "details": "",
                "edition": edition_name,
                "element": element,
                "type": item_type,
                "variant": variant,
                "image": image_path,
                "swapper": is_swapper,
            }
            all_items.append(item)
            print(f"  {name} | {item_type} | {element or 'no element'} | {variant}")

    # ── Build JSON output ──────────────────────────────────────────
    output = {
        "editions": [
            {"name": name, "release_date": date}
            for name, date in collected_editions.items()
        ],
        "elements": [{"name": n} for n in sorted(collected_elements)],
        "types": [{"name": n} for n in sorted(collected_types)],
        "variants": [{"name": n} for n in sorted(collected_variants)],
        "items": all_items,
    }

    with open("skylanders_data.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n=== Done ===")
    print(f"Editions: {len(output['editions'])}")
    print(f"Elements: {len(output['elements'])}")
    print(f"Types: {len(output['types'])}")
    print(f"Variants: {len(output['variants'])}")
    print(f"Items: {len(output['items'])}")
    print(f"Output written to: skylanders_data.json")


if __name__ == "__main__":
    scrape_all()
```

- [ ] **Step 2: Commit**

```bash
git add scraper.py
git commit -m "feat: add WP REST API scraper for skylanderscharacterlist.com"
```

---

### Task 4: Run scraper and verify output

**Files:**
- Generated: `skylanders_data.json`
- Generated: `react/public/assets/{SSA,SG,SSF,STT,SSC,SI}/*.png`

- [ ] **Step 1: Run the scraper**

From the project root:
```bash
python scraper.py
```

Expected: ~12 minutes runtime. Prints progress per edition, then a summary like:
```
=== Done ===
Editions: 6
Elements: 9
Types: ~14
Variants: ~10+
Items: ~646+
Output written to: skylanders_data.json
```

- [ ] **Step 2: Verify JSON structure**

```bash
python -c "
import json
with open('skylanders_data.json') as f:
    data = json.load(f)
print('Editions:', len(data['editions']))
print('Elements:', len(data['elements']))
print('Types:', len(data['types']))
print('Variants:', len(data['variants']))
print('Items:', len(data['items']))
print()
print('Sample item:', json.dumps(data['items'][0], indent=2))
print()
# Check for items with no element
no_element = [i['name'] for i in data['items'] if i['element'] is None]
print(f'Items with no element: {len(no_element)}')
if no_element[:5]:
    print('  Examples:', no_element[:5])
# Check for items with no image
no_image = [i['name'] for i in data['items'] if i['image'] is None]
print(f'Items with no image: {len(no_image)}')
if no_image[:5]:
    print('  Examples:', no_image[:5])
"
```

Expected: Counts look reasonable. Sample item has all expected fields. Review the output for obvious issues (missing names, wrong types, etc.).

- [ ] **Step 3: Verify images downloaded**

```bash
find react/public/assets -name "*.png" | head -20
ls react/public/assets/SG/ | head -10
ls react/public/assets/SSF/ | head -10
```

Expected: PNG files present in each edition directory.

- [ ] **Step 4: Spot-check data quality**

```bash
python -c "
import json
with open('skylanders_data.json') as f:
    data = json.load(f)
# Check type distribution
from collections import Counter
types = Counter(i['type'] for i in data['items'])
print('Type distribution:')
for t, c in types.most_common():
    print(f'  {t}: {c}')
print()
# Check variant distribution
variants = Counter(i['variant'] for i in data['items'])
print('Variant distribution:')
for v, c in variants.most_common():
    print(f'  {v}: {c}')
print()
# Check edition distribution
editions = Counter(i['edition'] for i in data['items'])
print('Edition distribution:')
for e, c in editions.most_common():
    print(f'  {e}: {c}')
"
```

Expected: Distributions look plausible. Most items should be "Standard" variant. All 6 editions represented. Type counts roughly match the WP category post counts from the spec.

- [ ] **Step 5: Fix any issues found in steps 2-4**

If the scraper output has problems (wrong names, missing data, bad mappings), fix them in `scraper.py`, re-run, and re-verify. Common issues to watch for:
- HTML entities in names (e.g., `&#8211;` instead of `–`) — `title.rendered` may include these
- Duplicate items across editions
- Missing types for some posts (check the "Skylander" fallback count — if unusually high, some categories may be unmapped)

- [ ] **Step 6: Commit the scraper fixes (if any) and the JSON data**

```bash
git add scraper.py skylanders_data.json
git commit -m "feat: scrape complete dataset — N items across 6 editions"
```

(Replace N with the actual item count.)

---

### Task 5: Rewrite db_maker.py to import from JSON

**Files:**
- Modify: `db_maker.py`

- [ ] **Step 1: Rewrite db_maker.py**

Replace the entire contents of `db_maker.py` with:

```python
import json
import requests

DB_URL = "http://localhost:8001/api"


def load_data():
    with open("skylanders_data.json", "r", encoding="utf-8") as f:
        return json.load(f)


def create_lookup(endpoint, items):
    """POST each entry, then GET all to build a name->id map."""
    name_to_id = {}

    # Get existing entries first
    resp = requests.get(f"{DB_URL}/{endpoint}/")
    if resp.status_code == 200:
        for entry in resp.json():
            name_to_id[entry["name"]] = entry["id"]

    # Create missing entries
    for item in items:
        if item["name"] in name_to_id:
            print(f"  {endpoint}: '{item['name']}' already exists (id={name_to_id[item['name']]})")
            continue
        resp = requests.post(f"{DB_URL}/{endpoint}/", json=item)
        if resp.status_code == 201:
            print(f"  {endpoint}: created '{item['name']}'")
        else:
            print(f"  {endpoint}: FAILED '{item['name']}': {resp.text}")

    # Refresh map after all inserts
    resp = requests.get(f"{DB_URL}/{endpoint}/")
    if resp.status_code == 200:
        name_to_id = {}
        for entry in resp.json():
            name_to_id[entry["name"]] = entry["id"]

    return name_to_id


def import_items(items, edition_map, element_map, type_map, variant_map):
    """POST each item to the API with resolved foreign key IDs."""
    created = 0
    failed = 0

    for item in items:
        edition_id = edition_map.get(item["edition"])
        type_id = type_map.get(item["type"])
        variant_id = variant_map.get(item["variant"])
        element_id = element_map.get(item["element"]) if item["element"] else None

        if not edition_id or not type_id or not variant_id:
            print(f"  SKIP: {item['name']} — missing FK "
                  f"(edition={edition_id}, type={type_id}, variant={variant_id})")
            failed += 1
            continue

        payload = {
            "name": item["name"],
            "details": item["details"],
            "type_id": type_id,
            "edition_id": edition_id,
            "image": item["image"] or "",
            "variant_id": variant_id,
            "swapper": item["swapper"],
        }
        if element_id is not None:
            payload["element_id"] = element_id

        resp = requests.post(f"{DB_URL}/items/", json=payload)
        if resp.status_code == 201:
            created += 1
        else:
            failed += 1
            print(f"  FAILED: {item['name']}: {resp.text}")

    return created, failed


def main():
    data = load_data()

    print("Creating editions...")
    edition_map = create_lookup("editions", data["editions"])
    print(f"  {len(edition_map)} editions ready\n")

    print("Creating elements...")
    element_map = create_lookup("elements", data["elements"])
    print(f"  {len(element_map)} elements ready\n")

    print("Creating types...")
    type_map = create_lookup("types", data["types"])
    print(f"  {len(type_map)} types ready\n")

    print("Creating variants...")
    variant_map = create_lookup("variants", data["variants"])
    print(f"  {len(variant_map)} variants ready\n")

    print(f"Importing {len(data['items'])} items...")
    created, failed = import_items(
        data["items"], edition_map, element_map, type_map, variant_map
    )

    print(f"\n=== Summary ===")
    print(f"Items created: {created}")
    print(f"Items failed:  {failed}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Commit**

```bash
git add db_maker.py
git commit -m "feat: rewrite db_maker.py to import from skylanders_data.json"
```

---

### Task 6: End-to-end import verification

**Files:**
- None (verification only)

**Prerequisites:** Backend running on port 8001 with a fresh database.

- [ ] **Step 1: Start the backend**

```bash
cd fastapi && uvicorn main:app --reload --port 8001
```

- [ ] **Step 2: Run the importer**

From project root (in a new terminal):
```bash
python db_maker.py
```

Expected: All lookup tables created, then items imported. Summary should show most items created, few or no failures.

- [ ] **Step 3: Verify via API**

```bash
curl http://localhost:8001/api/editions/ | python -m json.tool | head -30
curl http://localhost:8001/api/types/ | python -m json.tool
curl http://localhost:8001/api/elements/ | python -m json.tool
curl "http://localhost:8001/api/items?limit=5" | python -m json.tool | head -50
```

Expected: Editions, types, elements all present. Items have resolved nested objects (edition, element, type, variant). Items with no element should show `"element": null`.

- [ ] **Step 4: Verify frontend**

Start the dev server from `react/`:
```bash
cd react && npm run dev
```

Open `http://localhost:5173/search` in a browser. Verify:
- Items display with images
- Element icons show correctly
- Edition logos show correctly
- Filtering by search works
- Items without elements render without errors

- [ ] **Step 5: Final commit**

If any fixes were needed during verification:
```bash
git add -A
git commit -m "fix: address issues found during end-to-end verification"
```
