import html
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

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}


# ── API helpers ────────────────────────────────────────────────────


def fetch_paginated(endpoint, params=None):
    """Fetch all pages from a WP REST API endpoint (4 results/page cap)."""
    all_results = []
    page = 1
    while True:
        p = {**(params or {}), "page": page, "per_page": 100}
        time.sleep(DELAY)
        resp = requests.get(f"{WP_API}/{endpoint}", params=p, headers=HEADERS)
        if resp.status_code in (400, 403):
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
    resp = requests.get(f"{WP_API}/media/{media_id}", headers=HEADERS)
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
    name = html.unescape(title).strip()
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
    resp = requests.get(url, headers=HEADERS)
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
