# Database Population Scraper — Design Spec

## Overview

Two-phase approach to populate the Skylanders Collector database using data from skylanderscharacterlist.com. Phase 1 scrapes the WordPress REST API and downloads images. Phase 2 imports the scraped data into the database via the FastAPI backend.

## Scope

All figures from all 6 editions, including variants, LightCore, Eon's Elite, Adventure Packs, Magic Items, Battle Packs, Creation Crystals, and Battlecast cards. Approximately 646+ entries.

## Data Source

The WordPress REST API at `skylanderscharacterlist.com/wp-json/wp/v2/`.

- **Posts endpoint:** `/wp-json/wp/v2/posts` — each post is a character/figure.
- **Categories endpoint:** `/wp-json/wp/v2/categories` — encodes edition, element, type, and variant status.
- **Media endpoint:** `/wp-json/wp/v2/media/{id}` — resolves featured image URLs.
- **Pagination:** Capped at 4 posts per page. Paginate with `?page=N` until 400 response.

### Category Taxonomy

**Edition categories:**

| ID  | Name             | DB Edition Name      | Image Code |
| --- | ---------------- | -------------------- | ---------- |
| 4   | Spyro's Adventure | Spyro's Adventures  | SSA        |
| 47  | Giants           | Giants               | SG         |
| 66  | SWAP Force       | Swap Force           | SSF        |
| 134 | Trap Team        | Trap Team            | STT        |
| 234 | SuperChargers    | Super Chargers       | SSC        |
| 276 | Imaginators      | Imaginators          | SI         |

**Element categories:**

| ID  | Name   |
| --- | ------ |
| 6   | Air    |
| 10  | Earth  |
| 16  | Fire   |
| 20  | Life   |
| 25  | Magic  |
| 30  | Tech   |
| 35  | Undead |
| 40  | Water  |
| 222 | Dark   |

**Type categories (WP category -> DB type):**

| WP Category ID | WP Name                | DB Type          |
| -------------- | ---------------------- | ---------------- |
| 3              | Series 1               | Skylander        |
| 46             | Series 2               | Skylander        |
| 48             | LightCore              | LightCore        |
| 50             | Giant                  | Giant            |
| 67             | SWAP Force Characters  | Swapper          |
| 89             | Adventure Pack         | Adventure Pack   |
| 90             | Magic Items            | Magic Item       |
| 103            | Level                  | Level            |
| 105            | Battle Pack            | Battle Pack      |
| 135            | Trap Master            | Trap Master      |
| 203            | Eons Elite             | Eon's Elite      |
| 235            | SuperCharger           | SuperCharger     |
| 277            | Sensei                 | Sensei           |
| 278            | Creation Crystal       | Creation Crystal |
| 279            | Battlecast             | Battlecast       |

**Variant detection:** Posts with category ID 78 are variants. The specific variant name (Legendary, Chrome, Dark, etc.) is parsed from the "Variant Type" field in the post's HTML content table.

## Phase 1: Scraper (`scraper.py`)

### Process

1. **Fetch all categories** from `/wp-json/wp/v2/categories` and build lookup maps (category ID -> name) for editions, elements, and types.

2. **For each edition**, fetch all posts via `/wp-json/wp/v2/posts?categories={edition_cat_id}&page=N`, paginating 4 at a time until the API returns 400.

3. **For each post**, extract:
   - **name:** from `title.rendered`, appending series info like "(Series 2)" when applicable
   - **edition:** from which edition category is present
   - **element:** from element category — `null` if none found
   - **type:** mapped from category using the type mapping table above
   - **variant:** "Standard" by default; if category 78 (Variants) is present, parse the "Variant Type" field from the HTML content table using BeautifulSoup
   - **swapper:** `true` if type is "Swapper" (category 67)
   - **image_url:** resolve `featured_media` ID via `/wp-json/wp/v2/media/{id}` to get the source URL

4. **Download images** to `react/public/assets/{EDITION_CODE}/{ImageName}.png`, following the existing naming convention (PascalCase, no spaces).

5. **Output** `skylanders_data.json`.

### Rate Limiting

0.5s delay between WP API requests. Estimated ~1450 requests total, ~12 minutes runtime.

## JSON Structure (`skylanders_data.json`)

```json
{
  "editions": [
    {"name": "Spyro's Adventures", "release_date": "2011-10-12"}
  ],
  "elements": [
    {"name": "Magic"}
  ],
  "types": [
    {"name": "Skylander"}
  ],
  "variants": [
    {"name": "Standard"}
  ],
  "items": [
    {
      "name": "Spyro (Series 1)",
      "details": "",
      "edition": "Spyro's Adventures",
      "element": "Magic",
      "type": "Skylander",
      "variant": "Standard",
      "image": "SSA/Spyro.png",
      "swapper": false
    }
  ]
}
```

Items reference lookup tables by name (not ID). The importer resolves names to IDs at import time. Element-less items have `"element": null`.

## Phase 2: Importer (`db_maker.py` rewrite)

### Process

1. **Load** `skylanders_data.json`.
2. **Create lookup tables first** — POST each edition, element, type, and variant to the API. After each POST, fetch the created entities back via GET to build a `name -> id` map.
3. **Create items** — for each item in the JSON, resolve `edition`, `element`, `type`, `variant` names to IDs using the maps, then POST to `/api/items/`.
4. **Report progress** — print counts of created entities and any failures.

### Error Handling

- If a lookup entity already exists, skip it and fetch the existing ID.
- If an item POST fails, log the error with the item name and continue.
- Print a summary at the end: X items created, Y skipped/failed.

## Schema Changes

Two minor changes to support element-less figures:

- `fastapi/models/item_model.py`: make `element` column nullable
- `fastapi/base_models.py`: make `element_id` field `Optional[int] = None` in `ItemBase`

## New Lookup Table Entries

**Types to add:** Trap Master, SuperCharger, LightCore, Eon's Elite, Creation Crystal, Magic Item, Adventure Pack, Battle Pack, Level, Battlecast

**Elements to add:** Dark

**Variants to add:** discovered dynamically during scraping from the "Variant Type" HTML field (e.g., Legendary, Chrome, Dark, etc.)

## Dependencies

- `requests` (already present)
- `beautifulsoup4` (new — for parsing variant type from HTML content)

## File Changes Summary

| File | Change |
| --- | --- |
| `scraper.py` | New — WP API scraper + image downloader |
| `skylanders_data.json` | New — generated output |
| `db_maker.py` | Rewrite — reads from JSON instead of hardcoded data |
| `fastapi/models/item_model.py` | Minor — make `element` column nullable |
| `fastapi/base_models.py` | Minor — make `element_id` optional in `ItemBase` |
| `react/public/assets/{SG,SSF,STT,SSC,SI}/` | Populated with downloaded images |

## Workflow

```bash
# 1. Scrape the website (only needed once)
python scraper.py

# 2. Start the backend
cd fastapi && uvicorn main:app --reload

# 3. Seed the database
python db_maker.py
```
