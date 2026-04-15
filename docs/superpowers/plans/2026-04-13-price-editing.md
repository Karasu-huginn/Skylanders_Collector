# Price Editing on Details Page — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the price editable from the figure details page, with cents↔euros conversion and save feedback.

**Architecture:** Fix the backend PATCH endpoint to support setting price to 0, then replace the read-only price display in the metadata grid with an always-visible input. On blur/Enter, parse the euro string to cents and PATCH. Flash the tile border on success.

**Tech Stack:** React 19, TypeScript, TanStack React Query (useMutation), CSS transitions, FastAPI/Python

---

## File Map

- **Modify:** `fastapi/routers/item_router.py` — fix price=0 bug in PATCH endpoint
- **Modify:** `react/src/ItemDetails.tsx` — add price state, input, mutation, conversion helpers
- **Modify:** `react/src/ItemDetails.css` — add price input styles and save-flash animation

---

### Task 1: Fix backend PATCH endpoint to allow setting price to 0

**Files:**
- Modify: `fastapi/routers/item_router.py:85-117`

The current endpoint uses `price if price else Item.price` — since `0` is falsy in Python, sending `price=0` silently keeps the old price. Fix by using `Optional[int]` with `None` as the default.

- [ ] **Step 1: Update the endpoint signature and logic**

In `fastapi/routers/item_router.py`, change the endpoint:

Change the import at top of file:
```python
from typing import Annotated, Optional
```

Change the function signature parameter:
```python
    price: Optional[int] = None,
```

Change both occurrences of the price line in update_dict:
```python
            "price": price if price is not None else Item.price,
```

(This appears twice — once in the `if bot_count_add or top_count_add` branch and once in the `else` branch.)

- [ ] **Step 2: Commit**

```bash
git add fastapi/routers/item_router.py
git commit -m "fix: allow setting price to 0 in PATCH endpoint"
```

---

### Task 2: Add price input to the metadata grid

**Files:**
- Modify: `react/src/ItemDetails.tsx:126-131` (replace read-only price display)
- Modify: `react/src/ItemDetails.css` (add price input styles)

- [ ] **Step 1: Add conversion helpers and price state in ItemDetails.tsx**

Add the conversion helpers **outside** the component (before `export function ItemDetails()`), after the `PatchRequest` interface:

```typescript
const centsToEuros = (cents: number): string => {
    if (cents === 0) return "";
    return (cents / 100).toFixed(2).replace(".", ",");
};

const eurosToCents = (value: string): number | null => {
    const trimmed = value.trim();
    if (trimmed === "") return 0;
    const parsed = parseFloat(trimmed.replace(",", "."));
    if (isNaN(parsed) || parsed < 0) return null;
    return Math.round(parsed * 100);
};
```

Then add state inside the component, after the existing `displayCount` line (line 55):

```typescript
const [priceInput, setPriceInput] = useState<string>("");
const [priceSaved, setPriceSaved] = useState(false);
```

- [ ] **Step 2: Initialize priceInput from fetched data**

Add the `useEffect` import to the existing import line:

```typescript
import { useState, useEffect } from "react";
```

Add after the `priceSaved` state line:

```typescript
useEffect(() => {
    if (data) {
        setPriceInput(centsToEuros(data.price));
    }
}, [data]);
```

- [ ] **Step 3: Add price PATCH mutation**

Add after the existing `useMutation` call (line 53):

```typescript
const patchPrice = async (params: { itemId: number; price: number }) => {
    const response = await fetch(`/api/items/${params.itemId}?price=${params.price}`, {
        method: "PATCH",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        },
    });
    return response;
};

const { mutate: mutatePrice } = useMutation({
    mutationFn: patchPrice,
    onSuccess: () => {
        setPriceSaved(true);
        setTimeout(() => setPriceSaved(false), 1000);
    },
});
```

- [ ] **Step 4: Add savePrice handler**

Add after the `updateCount` function:

```typescript
const savePrice = () => {
    if (!data) return;
    const cents = eurosToCents(priceInput);
    if (cents === null) {
        // Invalid input — revert
        setPriceInput(centsToEuros(data.price));
        return;
    }
    mutatePrice({ itemId: data.id, price: cents });
};
```

- [ ] **Step 5: Replace the read-only price JSX with the editable input**

Replace the current price block (lines 126-131):

```tsx
{data.price > 0 && (
    <div className="detail-meta-item">
        <span className="detail-meta-label">Prix</span>
        <span className="detail-meta-value">{data.price} €</span>
    </div>
)}
```

With:

```tsx
<div className={`detail-meta-item detail-price-tile${priceSaved ? " detail-price-saved" : ""}`}>
    <span className="detail-meta-label">Prix</span>
    <div className="detail-price-input-wrap">
        <input
            type="text"
            inputMode="decimal"
            className="detail-price-input"
            value={priceInput}
            placeholder="0,00"
            onChange={(e) => setPriceInput(e.target.value)}
            onBlur={savePrice}
            onKeyDown={(e) => {
                if (e.key === "Enter") {
                    e.currentTarget.blur();
                }
            }}
        />
        <span className="detail-price-suffix">€</span>
    </div>
</div>
```

- [ ] **Step 6: Commit**

```bash
git add react/src/ItemDetails.tsx
git commit -m "feat: add editable price input to details page"
```

---

### Task 3: Style the price input and save-flash animation

**Files:**
- Modify: `react/src/ItemDetails.css` (add styles at end of file, before the `@media` query)

- [ ] **Step 1: Add price input CSS**

Add before the `/* Responsive */` comment (line 200):

```css
/* Price input */
.detail-price-tile {
  transition: border-color 0.3s ease;
}

.detail-price-saved {
  border-color: #4ade80;
}

.detail-price-input-wrap {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.detail-price-input {
  font-family: var(--font-display);
  font-size: 1.1rem;
  font-weight: 500;
  color: var(--text-primary);
  background: transparent;
  border: none;
  outline: none;
  width: 5rem;
  padding: 0;
}

.detail-price-input::placeholder {
  color: var(--text-muted);
}

.detail-price-suffix {
  font-family: var(--font-display);
  font-size: 1.1rem;
  font-weight: 500;
  color: var(--text-muted);
}
```

- [ ] **Step 2: Commit**

```bash
git add react/src/ItemDetails.css
git commit -m "style: add price input and save-flash styles"
```

---

### Task 4: Manual verification

**Files:** None (testing only)

- [ ] **Step 1: Start the dev servers**

Make sure both backend and frontend are running:

```bash
cd react && npm run dev
```

(Backend should already be running on port 8000)

- [ ] **Step 2: Verify the price tile is always visible**

Navigate to any item detail page (e.g. `http://localhost:5173/item/1`). The Prix tile should appear in the metadata grid even if the item has price 0. The input should be empty with a `0,00` placeholder.

- [ ] **Step 3: Verify editing and saving**

1. Type `12,50` into the price input
2. Press Enter or click away
3. The tile border should flash green briefly (~1s)
4. Refresh the page — the price should persist as `12,50`

- [ ] **Step 4: Verify invalid input reverts**

1. Type `abc` into the price input
2. Click away
3. The input should revert to the previous value (not send a PATCH)

- [ ] **Step 5: Verify empty input sets price to 0**

1. Clear the price input completely
2. Click away
3. The input should be empty with the `0,00` placeholder
4. Refresh — price should be 0

- [ ] **Step 6: Commit all work if any final adjustments were needed**

```bash
git add react/src/ItemDetails.tsx react/src/ItemDetails.css
git commit -m "fix: adjustments from manual testing"
```

(Skip this step if no adjustments were needed)
