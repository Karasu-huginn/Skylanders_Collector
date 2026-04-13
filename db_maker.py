import json
import os
import requests

DB_URL = os.getenv("API_URL", "http://localhost:8001/api")


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
