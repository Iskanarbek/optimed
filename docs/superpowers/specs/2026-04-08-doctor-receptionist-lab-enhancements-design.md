# Doctor, Receptionist & Lab Panel Enhancements — Design Spec

**Date**: 2026-04-08
**Status**: Draft

---

## 1. Doctor Panel — Tibbiy Yozuv Restructure

### 1.1 Field Changes

**Remove permanently**: `shikoyatlar`, `solution` (delete model fields + all references in views/templates/seed_data)

**Keep legacy fields as-is** (unused but not removed to avoid data loss): `problem`, `notes`

**Keep** (original order): anamnesis_morbi, operatsiyalar, tomizilgan, koz_oynak_kontakt_linza, anamnesis_vitae, allergiya, qovoqlar_koz_yosh_yollari, koz_soqqasi, koz_olmasi, sklera, shox_parda, old_kamera, rangdor_parda_qorachiq

**Add 4 new fields** (after rangdor_parda_qorachiq, before tashxis):
- `gavhar` — label: "Gavhar" grey: *(Хрусталик)*
- `korish_otkirligi` — label: "Ko'rish o'tkirligi" grey: *(Острота зрения)*
- `shishasimon_tana` — label: "Shishasimon tana" grey: *(Стекловидное тело)*
- `oftalmoskopiya` — label: "Oftalmoskopiya" grey: *(Офтальмоскопия)*

**Move to end**: `tashxis` *(Диагноз)*, `tavsiya` *(Рекомендации)*

Final order: 13 existing + 4 new + 2 moved = 19 fields total.

### 1.2 UI Behavior

- **Button-based**: Doctor clicks "Tibbiy yozuv" button → modal opens with ALL 19 fields
- **Display**: Only non-empty fields shown in the view (skipped = hidden)
- **Edit**: Reopens modal with all fields. Clearing a field → it disappears from display on save
- **Each label**: Uzbek name + grey thinner text in brackets with Russian translation

### 1.3 Model Migration

- Remove `shikoyatlar` and `solution` from Visit model
- Add `gavhar`, `korish_otkirligi`, `shishasimon_tana`, `oftalmoskopiya` as TextField(blank=True, default='') to Visit model

### 1.4 Touch Points for Field Changes

All these locations must be updated (remove shikoyatlar/solution, add 4 new fields):
- `views.py`: `admin_patient_detail` visits_edit_data, `doctor_patient_detail` visits_edit_data, `doctor_patient_full_history` visits_edit_data, `doctor_update_visit`, `doctor_edit_done_visit` field list
- `templates/doctor/patient_detail.html`: tibbiy yozuv section, edit modal, history display
- `templates/doctor/patient_full_history.html`
- `seed_data.py`

---

## 2. Doctor Panel — Left Side Restructure

### 2.1 Layout Order

1. **KRT / REF / IOP** — existing, unchanged
2. **Ko'rish o'tkirligi korreksiya bilan** *(Острота зрения с коррекцией)* — NEW
3. **Procedures** — existing, unchanged

### 2.2 New Model: EyeVisualAcuity

```python
class EyeVisualAcuity(models.Model):
    visit = models.ForeignKey(Visit, on_delete=models.CASCADE, related_name='visual_acuities')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    # Uzoq (Вдаль) - Distance
    uzoq_od_sph = models.CharField(max_length=20, blank=True, default='')
    uzoq_od_cyl = models.CharField(max_length=20, blank=True, default='')
    uzoq_od_ax = models.CharField(max_length=20, blank=True, default='')
    uzoq_od_vis = models.CharField(max_length=20, blank=True, default='')
    uzoq_os_sph = models.CharField(max_length=20, blank=True, default='')
    uzoq_os_cyl = models.CharField(max_length=20, blank=True, default='')
    uzoq_os_ax = models.CharField(max_length=20, blank=True, default='')
    uzoq_os_vis = models.CharField(max_length=20, blank=True, default='')
    # Yaqin (Вблизи) - Near
    yaqin_od_sph = models.CharField(max_length=20, blank=True, default='')
    yaqin_od_cyl = models.CharField(max_length=20, blank=True, default='')
    yaqin_od_ax = models.CharField(max_length=20, blank=True, default='')
    yaqin_od_vis = models.CharField(max_length=20, blank=True, default='')
    yaqin_os_sph = models.CharField(max_length=20, blank=True, default='')
    yaqin_os_cyl = models.CharField(max_length=20, blank=True, default='')
    yaqin_os_ax = models.CharField(max_length=20, blank=True, default='')
    yaqin_os_vis = models.CharField(max_length=20, blank=True, default='')
    # MKL (МКЛ) - Soft contact lens
    mkl_od_sph = models.CharField(max_length=20, blank=True, default='')
    mkl_od_cyl = models.CharField(max_length=20, blank=True, default='')
    mkl_od_ax = models.CharField(max_length=20, blank=True, default='')
    mkl_od_vis = models.CharField(max_length=20, blank=True, default='')
    mkl_os_sph = models.CharField(max_length=20, blank=True, default='')
    mkl_os_cyl = models.CharField(max_length=20, blank=True, default='')
    mkl_os_ax = models.CharField(max_length=20, blank=True, default='')
    mkl_os_vis = models.CharField(max_length=20, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
```

### 2.3 UI

- Button "+ Korreksiya" opens modal with 3 tables (Uzoq/Yaqin/MKL), each with O'ng/Chap rows and SPH/CYL/AX/VIS columns
- Same add/edit/delete pattern as KRT/REF/IOP
- New URL endpoints: `doctor_add_visual_acuity`, `doctor_edit_visual_acuity`, `doctor_delete_visual_acuity`

### 2.4 History Compactness

- REF/KRT/IOP/Korreksiya records in history: smaller font (~11px), tighter padding, more compact layout

---

## 3. Doctor Panel — Ko'z Ko'rigi & Vipiska Forms

### 3.1 Button Layout

Three buttons in a row on the right side of the patient detail page:
`[Tibbiy yozuv]` `[Ko'z ko'rigi]` `[Vipiska]`

### 3.2 Ko'z Ko'rigi Model: EyeExamForm

```python
class EyeExamForm(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='eye_exam_forms')
    visit = models.ForeignKey(Visit, on_delete=models.SET_NULL, null=True, blank=True)
    doctor = models.ForeignKey(Worker, on_delete=models.SET_NULL, null=True)
    protocol_number = models.CharField(max_length=20, unique=True)  # auto-generated
    created_at = models.DateTimeField(auto_now_add=True)

    # Header (auto-filled)
    kelish_sanasi = models.DateTimeField()
    kelish_raqami = models.CharField(max_length=20, blank=True, default='')
    filial = models.CharField(max_length=100, blank=True, default='')

    # Ko'z anamezi
    koz_anamezi = models.TextField(blank=True, default='')

    # Refraction table: O'ng and Chap (SPH/CYL/AXIS)
    ref_ong_sph = models.CharField(max_length=20, blank=True, default='')
    ref_ong_cyl = models.CharField(max_length=20, blank=True, default='')
    ref_ong_axis = models.CharField(max_length=20, blank=True, default='')
    ref_chap_sph = models.CharField(max_length=20, blank=True, default='')
    ref_chap_cyl = models.CharField(max_length=20, blank=True, default='')
    ref_chap_axis = models.CharField(max_length=20, blank=True, default='')

    # Subyektiv refraktsiya
    sub_ref_ong_sph = models.CharField(max_length=20, blank=True, default='')
    sub_ref_ong_cyl = models.CharField(max_length=20, blank=True, default='')
    sub_ref_ong_axis = models.CharField(max_length=20, blank=True, default='')
    sub_ref_chap_sph = models.CharField(max_length=20, blank=True, default='')
    sub_ref_chap_cyl = models.CharField(max_length=20, blank=True, default='')
    sub_ref_chap_axis = models.CharField(max_length=20, blank=True, default='')

    # Sikloplejili refraktsiya
    sik_ref_ong_sph = models.CharField(max_length=20, blank=True, default='')
    sik_ref_ong_cyl = models.CharField(max_length=20, blank=True, default='')
    sik_ref_ong_axis = models.CharField(max_length=20, blank=True, default='')
    sik_ref_chap_sph = models.CharField(max_length=20, blank=True, default='')
    sik_ref_chap_cyl = models.CharField(max_length=20, blank=True, default='')
    sik_ref_chap_axis = models.CharField(max_length=20, blank=True, default='')

    # Clinical findings — O'ng / Chap
    tuzatilmagan_korish_ong = models.CharField(max_length=50, blank=True, default='')
    tuzatilmagan_korish_chap = models.CharField(max_length=50, blank=True, default='')
    tuzatilgan_korish_ong = models.CharField(max_length=50, blank=True, default='')
    tuzatilgan_korish_chap = models.CharField(max_length=50, blank=True, default='')
    old_segment_ong = models.CharField(max_length=100, blank=True, default='')
    old_segment_chap = models.CharField(max_length=100, blank=True, default='')
    orqa_segment_ong = models.CharField(max_length=100, blank=True, default='')
    orqa_segment_chap = models.CharField(max_length=100, blank=True, default='')
    koz_bosimi_ong = models.CharField(max_length=50, blank=True, default='')
    koz_bosimi_chap = models.CharField(max_length=50, blank=True, default='')

    # Oyku (history notes)
    oyku = models.TextField(blank=True, default='')

    # Prescription table: Uzoq/Yaqin with O'ng/Chap (SPH/CYL/AXIS)
    uzoq_ong_sph = models.CharField(max_length=20, blank=True, default='')
    uzoq_ong_cyl = models.CharField(max_length=20, blank=True, default='')
    uzoq_ong_axis = models.CharField(max_length=20, blank=True, default='')
    uzoq_chap_sph = models.CharField(max_length=20, blank=True, default='')
    uzoq_chap_cyl = models.CharField(max_length=20, blank=True, default='')
    uzoq_chap_axis = models.CharField(max_length=20, blank=True, default='')
    yaqin_ong_sph = models.CharField(max_length=20, blank=True, default='')
    yaqin_ong_cyl = models.CharField(max_length=20, blank=True, default='')
    yaqin_ong_axis = models.CharField(max_length=20, blank=True, default='')
    yaqin_chap_sph = models.CharField(max_length=20, blank=True, default='')
    yaqin_chap_cyl = models.CharField(max_length=20, blank=True, default='')
    yaqin_chap_axis = models.CharField(max_length=20, blank=True, default='')

    # Lens table
    linza_ong = models.CharField(max_length=50, blank=True, default='')
    linza_chap = models.CharField(max_length=50, blank=True, default='')
    diametr_ong = models.CharField(max_length=50, blank=True, default='')
    diametr_chap = models.CharField(max_length=50, blank=True, default='')
    radius_ong = models.CharField(max_length=50, blank=True, default='')
    radius_chap = models.CharField(max_length=50, blank=True, default='')
    dioptriya_ong = models.CharField(max_length=50, blank=True, default='')
    dioptriya_chap = models.CharField(max_length=50, blank=True, default='')

    # ICD diagnosis
    icd_kodi = models.CharField(max_length=20, blank=True, default='')
    icd_nomi = models.CharField(max_length=200, blank=True, default='')
    tashxis_turi = models.CharField(max_length=100, blank=True, default='')
    yonalish = models.CharField(max_length=50, blank=True, default='')
```

### 3.3 Vipiska Model: DischargeForm

```python
class DischargeForm(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='discharge_forms')
    visit = models.ForeignKey(Visit, on_delete=models.SET_NULL, null=True, blank=True)
    doctor = models.ForeignKey(Worker, on_delete=models.SET_NULL, null=True)
    protocol_number = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Dates
    yotish_sanasi = models.DateField(null=True, blank=True)
    chiqish_sanasi = models.DateField(null=True, blank=True)

    # History
    shikoyat_tarix = models.TextField(blank=True, default='')
    shaxsiy_oilaviy_tarix = models.TextField(blank=True, default='')
    tizimli_anamnez = models.TextField(blank=True, default='')
    koz_anamezi = models.TextField(blank=True, default='')

    # Diagnosis & operation
    tashxis_kodi_nomi = models.TextField(blank=True, default='')
    operatsiya_kodi_nomi = models.TextField(blank=True, default='')

    # Exam findings — O'ng / Chap
    old_segment_ong = models.CharField(max_length=200, blank=True, default='')
    old_segment_chap = models.CharField(max_length=200, blank=True, default='')
    fundus_ong = models.CharField(max_length=200, blank=True, default='')
    fundus_chap = models.CharField(max_length=200, blank=True, default='')
    preop_ong = models.CharField(max_length=200, blank=True, default='')
    preop_chap = models.CharField(max_length=200, blank=True, default='')
    postop_ong = models.CharField(max_length=200, blank=True, default='')
    postop_chap = models.CharField(max_length=200, blank=True, default='')
    koz_bosimi_ong = models.CharField(max_length=100, blank=True, default='')
    koz_bosimi_chap = models.CharField(max_length=100, blank=True, default='')
    daraja_ong = models.CharField(max_length=100, blank=True, default='')
    daraja_chap = models.CharField(max_length=100, blank=True, default='')
    qovoq_ong = models.CharField(max_length=100, blank=True, default='')
    qovoq_chap = models.CharField(max_length=100, blank=True, default='')
    glob_ong = models.CharField(max_length=100, blank=True, default='')
    glob_chap = models.CharField(max_length=100, blank=True, default='')

    # Post-op notes
    muhim_tekshiruv = models.TextField(blank=True, default='')
    anesteziya_turi = models.CharField(max_length=100, blank=True, default='')
    operatsiya_izohlar = models.TextField(blank=True, default='')
    chiqish_holati = models.CharField(max_length=200, blank=True, default='')
    davolash = models.TextField(blank=True, default='')
    anesteziya_izohi = models.TextField(blank=True, default='')
    ishlatilgan_linzalar = models.TextField(blank=True, default='')
```

### 3.4 Protocol Number Generation

`generate_protocol_number()` in `clinic/utils.py`:
- Format: `YYYYMMDD` + 5 random digits (e.g., `2026040812345`)
- Checks both EyeExamForm and DischargeForm tables for uniqueness
- Retries up to 10 times on collision, raises ValueError if all fail
- Called at form creation time (in the view, before save)

### 3.5 History Display

- Both form types appear in patient history section as collapsed cards
- Card shows: type badge, protocol number, date, doctor name
- Click → overlay panel with blurred background showing full A4 form
- A4 layout with proper tables, lines, borders matching reference images

### 3.6 Design Notes

- **Snapshot model**: EyeExamForm and DischargeForm store snapshot copies of data, not references to EyeRefraction/EyeIOP etc. This ensures the printed document reflects what was entered at that time.
- **on_delete=SET_NULL for visit**: Forms survive visit deletion — they are standalone documents.
- **on_delete=CASCADE for EyeVisualAcuity**: Consistent with EyeRefraction/KRT/IOP pattern — these are visit-specific measurements.
- **Authorization**: Any doctor can create forms for visits assigned to them (same pattern as REF/KRT/IOP).
- **Ko'z ko'rigi/Vipiska buttons**: Only visible when there is an active visit (visit_id in URL).
- **Doctor can also print**: The A4 overlay in patient history includes a print button.
- **filial field**: Hardcoded clinic name for print output, not multi-branch.

### 3.7 URLs

```
/doctor/<doctor_id>/visit/<visit_id>/eye-exam/add/
/doctor/<doctor_id>/eye-exam/<pk>/edit/
/doctor/<doctor_id>/eye-exam/<pk>/delete/
/doctor/<doctor_id>/visit/<visit_id>/discharge/add/
/doctor/<doctor_id>/discharge/<pk>/edit/
/doctor/<doctor_id>/discharge/<pk>/delete/
```

---

## 4. Receptionist Panel Changes

### 4.1 Tarix → Shifokorlar

- Rename "Tarix" to "Shifokorlar" (display label only — URL `/receptionist/history/` and view name stay unchanged)
- Remove "Bemorlar" tab entirely — only doctors list remains
- Keep orphan doctors section

### 4.2 New Section: "Hujjatlar" *(Документы)*

New sidebar item + page at `/receptionist/documents/`.

**Search**: Input field for phone number OR protocol number.
- Phone search → all EyeExamForm + DischargeForm for that patient, newest first, as cards
- Protocol search → single matching form

**Card display**: Type badge (Ko'z ko'rigi / Vipiska), patient name, doctor, date, protocol number.

**Full view**: Click card → overlay with blurred bg, A4 form rendered, Print button.

**Print**: `window.print()` with `@media print` CSS — only the A4 form content prints.

**Pagination**: Not needed — clinic volume is low, unlikely to exceed ~50 forms per patient.

### 4.3 URLs

```
/receptionist/documents/
/receptionist/documents/search/   (AJAX)
/receptionist/documents/<form_type>/<pk>/view/
```

---

## 5. Laboratory — Reference Values

### 5.1 Data Changes

Extend `LAB_SERVICES` in `lab_services.py` from 3-tuples to 4-tuples:
```python
(number, name_ru, price, reference_value)
```

Standard medical reference values for all ~200 tests. Example:
```python
(1, "Гемоглобин (HGB)", 35000, "Э: 130-170 г/л, А: 120-150 г/л"),
(2, "Глюкоза", 40000, "3.9-6.1 ммоль/л"),
```

### 5.2 UI Changes

- **Compact rows**: Reduced padding, single-line layout per test
- **New column**: "Referens qiymatlari" between service name/price and result textarea
- Auto-populated from the 4th element of LAB_SERVICES tuples, looked up by `service_number` at render time
- Read-only display, grey text
- **No DB change**: Reference values are display-only from the hardcoded list, not stored per-LabVisitService

### 5.3 Template Changes

Lab visit detail table columns: `# | Xizmat nomi | Narx | Referens qiymatlari | Natija`

---

## Summary of New Models

| Model | Purpose |
|-------|---------|
| `EyeVisualAcuity` | Ko'rish o'tkirligi korreksiya bilan (SPH/CYL/AX/VIS for Uzoq/Yaqin/MKL) |
| `EyeExamForm` | Ko'z ko'rigi A4 form (full eye exam document) |
| `DischargeForm` | Vipiska A4 form (discharge summary document) |

## Summary of Removed

| Item | Reason |
|------|--------|
| `Visit.shikoyatlar` field | Replaced by structured fields |
| `Visit.solution` field | No longer needed |
| Receptionist "Bemorlar" tab in Tarix | Only doctors shown now |

## Summary of New URLs

| URL | Purpose |
|-----|---------|
| `doctor_add_visual_acuity` | Add korreksiya record |
| `doctor_edit_visual_acuity` | Edit korreksiya record |
| `doctor_delete_visual_acuity` | Delete korreksiya record |
| `doctor_add_eye_exam` | Create ko'z ko'rigi form |
| `doctor_edit_eye_exam` | Edit ko'z ko'rigi form |
| `doctor_delete_eye_exam` | Delete ko'z ko'rigi form |
| `doctor_add_discharge` | Create vipiska form |
| `doctor_edit_discharge` | Edit vipiska form |
| `doctor_delete_discharge` | Delete vipiska form |
| `receptionist_documents` | Hujjatlar page |
| `receptionist_documents_search` | AJAX search endpoint |
| `receptionist_document_view` | Full form view |
