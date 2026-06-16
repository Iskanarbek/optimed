# Panel Fixes Design — 2026-04-10

## Scope
Seven targeted fixes across Receptionist, Doctor, and Optika (Seller) panels.

---

## Receptionist Panel

### Fix 1 — Hujjatlar: Recent Documents on Load
**Problem:** Hujjatlar page is empty until the user types a search query.  
**Solution:**  
- `receptionist_documents` view fetches the 10 most recent `EyeExamForm` + 10 most recent `DischargeForm` records, sorted by `created_at` desc, merged and re-sorted.  
- Template renders these as cards by default under a "So'nggi hujjatlar" heading.  
- When user types in the search box and submits, the AJAX call replaces the default list with search results. Clearing the input and submitting again restores recents.

### Fix 2 — Lab Search: Broken 4-tuple Unpacking
**Problem:** `api_lab_services_search` unpacks `for num, name, price in results` but `LAB_SERVICES` now returns 4-tuples `(num, name, price, ref_value)`.  
**Solution:** Change unpacking to `for num, name, price, *rest in results`. Single-line fix in `clinic/views.py`.

---

## Doctor Panel

### Fix 3 — Ko'z Ko'rigi & Vipiska: Inline View + Edit (No A4)
**Problem:** Forms open in a full-screen A4 print overlay, which is too heavy for daily doctor use.  
**Solution:**  
- Each form history card is collapsible (click header to expand).  
- Expanded state shows all form fields in a clean 2-column card layout — no A4 borders, no print formatting.  
- An **"Tahrirlash"** button at the bottom of the expanded content switches the card into edit mode: all fields become inputs/textareas in place.  
- **"Saqlash"** POSTs to `doctor_edit_eye_exam` or `doctor_edit_discharge` URL (already exists), updating the original record.  
- No print button visible to doctors. The existing A4 overlay + print functionality is only available to receptionists via Hujjatlar.

### Fix 4 — Russian Text: Replace Transliteration with Cyrillic
**Problem:** Russian hint text in `a4-ru` spans uses Latin transliteration (e.g., `Osmotr glaz`) instead of Cyrillic (`Осмотр глаз`).  
**Solution:** Template-only change. Replace all transliterated Russian in `a4-ru` spans throughout `patient_detail.html` (Ko'z ko'rigi modal, Vipiska modal, and form overlays) with proper Cyrillic. Also fix the Ko'z ko'rigi and Vipiska input modals if they have the same issue.

### Fix 5 — Patient Full History: Show Ko'z Ko'rigi & Vipiska
**Problem:** `patient_full_history.html` only shows visit cards; Ko'z ko'rigi and Vipiska records are invisible to doctors when reviewing a patient's full history.  
**Solution:**  
- `doctor_patient_full_history` view adds `eye_exam_forms` and `discharge_forms` to context (queried by patient).  
- Template adds a "Tibbiy hujjatlar" section below the visit list.  
- Each form shows as a collapsed card. Clicking expands to show all fields in the same inline card format as Fix 3 (no A4, with edit button, no print).

---

## Optika (Seller) Panel

### Fix 6 — Sotuvlar as Landing Page
**Problem:** Seller login redirects to `seller_panel` (inventory management), but the seller's primary task is selling.  
**Solution:**  
- Both login redirect paths for role `seller` changed from `seller_panel` to `seller_sales`.  
- Sidebar nav: "Sotuvlar" link moved to first position, "Ko'zoynaklar" second, "Statistika" third.

### Fix 7 — Sotuvlar Page Redesign
**Problem:** Sotuvlar currently shows a log of past sales (with cost price and profit). Seller needs an inventory-based sell interface.  
**Solution:**

**Model change:** Add `discount_amount = IntegerField(default=0)` to `GlassSale`. Update `total_revenue` property to `(sell_price - discount_amount) * quantity`. New migration `0016_glasssale_discount_amount`.

**`seller_sales` view changes:**  
- Passes `glasses` = all `Glasses` with `quantity > 0` (available stock).  
- Removes `sales` queryset from this view (sales log moved to analytics or separate admin view).

**Template redesign (`seller/sales.html`):**  
- **Search bar** at top: text input filtering by model or brand (client-side JS on `input` event — no page reload).  
- **Table columns:** Model, Brand, Linza turi, Narx (sell price only — no cost, no profit), Miqdori (quantity badge), Amallar.  
- **"Sotish" button** per row: opens a small modal pre-filled with the glass name and sell price. Modal fields: Chegirma (discount in so'm, default 0), final price display (computed live). Submit button "Sotish" POSTs to `seller_sell_glasses`.  
- **`seller_sell_glasses` view:** quantity is always 1 (no quantity input), reads `discount_amount` from POST, creates `GlassSale` with `quantity=1, sell_price=g.sell_price, cost_price=g.cost_price, discount_amount=discount`. Decrements `g.quantity` by 1. Redirects to `seller_sales`.

---

## Files Affected

| File | Changes |
|------|---------|
| `clinic/views.py` | Fix 2 (lab search), Fix 5 (full history context), Fix 6 (login redirects), Fix 7 (seller_sales + seller_sell_glasses views) |
| `clinic/models.py` | Fix 7 (GlassSale.discount_amount field) |
| `clinic/migrations/0016_*.py` | Fix 7 (new migration) |
| `templates/receptionist/documents.html` | Fix 1 (show recent docs) |
| `templates/doctor/patient_detail.html` | Fix 3 (inline view/edit), Fix 4 (Cyrillic text) |
| `templates/doctor/patient_full_history.html` | Fix 5 (add forms section) |
| `templates/seller/sales.html` | Fix 7 (full redesign) |
| `templates/base.html` | Fix 6 (nav order for seller) |
