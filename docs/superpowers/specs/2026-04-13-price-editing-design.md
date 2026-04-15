# Price Editing on Details Page

## Summary

Make the price editable from the figure details page (ItemDetails). The price input replaces the read-only text inside the existing metadata grid tile.

## Current State

- Price is stored in the DB as an integer representing **cents** (e.g. `1234` = 12,34 €)
- The PATCH endpoint at `/api/items/{id}` already accepts a `price` query parameter (full replacement, not delta)
- The details page currently shows price as read-only text, only when `price > 0`
- **Bug**: the current display shows raw cents as if they were euros (`{data.price} €`)

## Design

### Prix Metadata Tile

- The **Prix** tile in the metadata grid is **always visible**, even when price is 0
- The tile contains a small text input with `€` suffix, instead of plain text
- The input displays euros with comma decimal separator (French locale): `1234` cents → `12,34`

### Interaction Flow

1. User types a value into the input (digits and comma accepted)
2. On **blur** or **Enter**:
   - Parse the input: `12,34` → `1234` cents
   - Send PATCH to `/api/items/{id}?price=1234`
   - On success: tile border briefly flashes accent/green color (~1s fade)
3. Empty input sends `price=0`; when price is 0, the input is empty with a `0,00` placeholder
4. Invalid input (non-numeric besides comma) reverts to previous value

### Conversion Logic

- **Display** (cents → euros): `(cents / 100).toFixed(2).replace('.', ',')`
- **Parse** (euros → cents): `Math.round(parseFloat(value.replace(',', '.')) * 100)`

### Visual Feedback

- On successful save: the tile border briefly flashes accent/green, then fades back (~1s CSS transition)
- When price is 0: input is empty with a `0,00` placeholder (greyed out)
- No error toast needed — invalid input simply reverts

## Scope

- **Files changed**: `react/src/ItemDetails.tsx`, `react/src/ItemDetails.css`
- **No backend changes** — the PATCH endpoint already supports the `price` parameter
- **No changes to ItemCard** — price editing is details page only
- Fix the existing cents-as-euros display bug as part of this work

## Out of Scope

- Price editing from the card/search view
- Price history or logging
- Currency selection
