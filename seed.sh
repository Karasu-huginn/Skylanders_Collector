#!/bin/sh
set -e

API_URL="${API_URL:-http://api:8080/api}"

echo "Waiting for API at $API_URL ..."
until curl -sf "$API_URL/editions/" > /dev/null 2>&1; do
  sleep 2
done
echo "API is ready."

# Check if data already exists
ITEM_COUNT=$(curl -sf "$API_URL/items" | python -c "import sys,json; print(len(json.load(sys.stdin).get('items',[])))" 2>/dev/null || echo "0")

if [ "$ITEM_COUNT" -gt "0" ]; then
  echo "Database already has $ITEM_COUNT items. Skipping seed."
  exit 0
fi

echo "Database is empty. Seeding..."
python db_maker.py
echo "Seeding complete."
