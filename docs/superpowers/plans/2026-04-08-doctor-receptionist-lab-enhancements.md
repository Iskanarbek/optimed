# Doctor, Receptionist & Lab Panel Enhancements — Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restructure doctor tibbiy yozuv to button-based UI, add visual acuity correction section, add Ko'z ko'rigi and Vipiska A4 printable forms, add receptionist documents section, and add lab reference values.

**Architecture:** Django models + views + templates. New models: EyeVisualAcuity, EyeExamForm, DischargeForm. Button-based modals following existing REF/KRT/IOP pattern. A4-formatted printable forms with @media print CSS. Receptionist document search via AJAX.

**Tech Stack:** Django 6.0.3, SQLite, vanilla JS, CSS

**Spec:** `docs/superpowers/specs/2026-04-08-doctor-receptionist-lab-enhancements-design.md`

---

## Chunk 1: Model Changes & Migrations

### Task 1: Update Visit model — remove shikoyatlar/solution, add 4 new fields

**Files:**
- Modify: `clinic/models.py:143-146` (Visit model fields)

- [ ] **Step 1: Remove shikoyatlar and solution fields, add 4 new fields**

In `clinic/models.py`, replace lines 143-146:
```python
    shikoyatlar = models.TextField(blank=True)
    tashxis = models.TextField(blank=True)
    tavsiya = models.TextField(blank=True)
    solution = models.TextField(blank=True)
```
With:
```python
    tashxis = models.TextField(blank=True)
    tavsiya = models.TextField(blank=True)
    gavhar = models.TextField(blank=True)
    korish_otkirligi = models.TextField(blank=True)
    shishasimon_tana = models.TextField(blank=True)
    oftalmoskopiya = models.TextField(blank=True)
```

- [ ] **Step 2: Run makemigrations**

Run: `cd /Users/iskandarodilov/Desktop/CRM && source venv/bin/activate && python manage.py makemigrations`
Expected: Migration created successfully

- [ ] **Step 3: Run migrate**

Run: `python manage.py migrate`
Expected: Migration applied successfully

- [ ] **Step 4: Commit**

```bash
git add clinic/models.py clinic/migrations/
git commit -m "feat: update Visit model — remove shikoyatlar/solution, add gavhar/korish_otkirligi/shishasimon_tana/oftalmoskopiya"
```

---

### Task 2: Add EyeVisualAcuity model

**Files:**
- Modify: `clinic/models.py` (add after EyeIOP class, around line 481)

- [ ] **Step 1: Add model definition**

Add after the EyeIOP class in `clinic/models.py`:
```python
class EyeVisualAcuity(models.Model):
    """Ko'rish o'tkirligi korreksiya bilan (Острота зрения с коррекцией)."""
    visit = models.ForeignKey(Visit, on_delete=models.CASCADE, related_name='visual_acuities')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='visual_acuities')
    # Uzoq (Вдаль)
    uzoq_od_sph = models.CharField(max_length=20, blank=True, default='')
    uzoq_od_cyl = models.CharField(max_length=20, blank=True, default='')
    uzoq_od_ax = models.CharField(max_length=20, blank=True, default='')
    uzoq_od_vis = models.CharField(max_length=20, blank=True, default='')
    uzoq_os_sph = models.CharField(max_length=20, blank=True, default='')
    uzoq_os_cyl = models.CharField(max_length=20, blank=True, default='')
    uzoq_os_ax = models.CharField(max_length=20, blank=True, default='')
    uzoq_os_vis = models.CharField(max_length=20, blank=True, default='')
    # Yaqin (Вблизи)
    yaqin_od_sph = models.CharField(max_length=20, blank=True, default='')
    yaqin_od_cyl = models.CharField(max_length=20, blank=True, default='')
    yaqin_od_ax = models.CharField(max_length=20, blank=True, default='')
    yaqin_od_vis = models.CharField(max_length=20, blank=True, default='')
    yaqin_os_sph = models.CharField(max_length=20, blank=True, default='')
    yaqin_os_cyl = models.CharField(max_length=20, blank=True, default='')
    yaqin_os_ax = models.CharField(max_length=20, blank=True, default='')
    yaqin_os_vis = models.CharField(max_length=20, blank=True, default='')
    # MKL (МКЛ)
    mkl_od_sph = models.CharField(max_length=20, blank=True, default='')
    mkl_od_cyl = models.CharField(max_length=20, blank=True, default='')
    mkl_od_ax = models.CharField(max_length=20, blank=True, default='')
    mkl_od_vis = models.CharField(max_length=20, blank=True, default='')
    mkl_os_sph = models.CharField(max_length=20, blank=True, default='')
    mkl_os_cyl = models.CharField(max_length=20, blank=True, default='')
    mkl_os_ax = models.CharField(max_length=20, blank=True, default='')
    mkl_os_vis = models.CharField(max_length=20, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"VA: {self.patient} - {self.created_at:%d.%m.%Y}"
```

- [ ] **Step 2: Run makemigrations and migrate**

Run: `python manage.py makemigrations && python manage.py migrate`

- [ ] **Step 3: Commit**

```bash
git add clinic/models.py clinic/migrations/
git commit -m "feat: add EyeVisualAcuity model for corrected visual acuity"
```

---

### Task 3: Add EyeExamForm model

**Files:**
- Modify: `clinic/models.py` (add after EyeVisualAcuity)

- [ ] **Step 1: Add model definition**

```python
class EyeExamForm(models.Model):
    """Ko'z ko'rigi — A4 printable eye examination form."""
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='eye_exam_forms')
    visit = models.ForeignKey(Visit, on_delete=models.SET_NULL, null=True, blank=True)
    doctor = models.ForeignKey(Worker, on_delete=models.SET_NULL, null=True)
    protocol_number = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # Header
    kelish_sanasi = models.DateTimeField(null=True, blank=True)
    filial = models.CharField(max_length=100, blank=True, default='Optimed')
    # Ko'z anamezi
    koz_anamezi = models.TextField(blank=True, default='')
    # Refraktsiya O'ng/Chap
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
    # Clinical findings O'ng/Chap
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
    # Oyku
    oyku = models.TextField(blank=True, default='')
    # Prescription Uzoq/Yaqin
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
    # ICD
    icd_kodi = models.CharField(max_length=20, blank=True, default='')
    icd_nomi = models.CharField(max_length=200, blank=True, default='')
    tashxis_turi = models.CharField(max_length=100, blank=True, default='')
    yonalish = models.CharField(max_length=50, blank=True, default='')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Ko'z ko'rigi #{self.protocol_number} - {self.patient}"
```

- [ ] **Step 2: Run makemigrations and migrate**

Run: `python manage.py makemigrations && python manage.py migrate`

- [ ] **Step 3: Commit**

```bash
git add clinic/models.py clinic/migrations/
git commit -m "feat: add EyeExamForm model for printable eye exam documents"
```

---

### Task 4: Add DischargeForm model

**Files:**
- Modify: `clinic/models.py` (add after EyeExamForm)

- [ ] **Step 1: Add model definition**

```python
class DischargeForm(models.Model):
    """Vipiska — A4 printable discharge summary form."""
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
    # Exam findings O'ng/Chap
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
    # Post-op
    muhim_tekshiruv = models.TextField(blank=True, default='')
    anesteziya_turi = models.CharField(max_length=100, blank=True, default='')
    operatsiya_izohlar = models.TextField(blank=True, default='')
    chiqish_holati = models.CharField(max_length=200, blank=True, default='')
    davolash = models.TextField(blank=True, default='')
    anesteziya_izohi = models.TextField(blank=True, default='')
    ishlatilgan_linzalar = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Vipiska #{self.protocol_number} - {self.patient}"
```

- [ ] **Step 2: Run makemigrations and migrate**

Run: `python manage.py makemigrations && python manage.py migrate`

- [ ] **Step 3: Commit**

```bash
git add clinic/models.py clinic/migrations/
git commit -m "feat: add DischargeForm model for printable discharge documents"
```

---

### Task 5: Add protocol number generator utility

**Files:**
- Create: `clinic/utils.py`

- [ ] **Step 1: Create utils.py with generate_protocol_number**

```python
import random
from datetime import date


def generate_protocol_number():
    """Generate unique protocol number: YYYYMMDD + 5 random digits."""
    from clinic.models import EyeExamForm, DischargeForm
    for _ in range(10):
        number = f"{date.today().strftime('%Y%m%d')}{random.randint(10000, 99999)}"
        if not EyeExamForm.objects.filter(protocol_number=number).exists() and \
           not DischargeForm.objects.filter(protocol_number=number).exists():
            return number
    raise ValueError("Could not generate unique protocol number after 10 attempts")
```

- [ ] **Step 2: Commit**

```bash
git add clinic/utils.py
git commit -m "feat: add protocol number generator utility"
```

---

## Chunk 2: Views — Update Existing + Add CRUD for New Models

### Task 6: Update views — remove shikoyatlar/solution references

**Files:**
- Modify: `clinic/views.py` — multiple locations

- [ ] **Step 1: Update doctor_update_visit (around line 1473)**

Remove the lines that save `shikoyatlar` and `solution` from `request.POST`. Keep all other fields. Add the 4 new fields:
```python
visit.gavhar = request.POST.get('gavhar', '')
visit.korish_otkirligi = request.POST.get('korish_otkirligi', '')
visit.shishasimon_tana = request.POST.get('shishasimon_tana', '')
visit.oftalmoskopiya = request.POST.get('oftalmoskopiya', '')
```

- [ ] **Step 2: Update doctor_edit_done_visit field list (around line 1640)**

Replace the field list:
```python
for field in ['tashxis', 'tavsiya', 'anamnesis_morbi',
              'operatsiyalar', 'tomizilgan', 'koz_oynak_kontakt_linza',
              'anamnesis_vitae', 'allergiya', 'qovoqlar_koz_yosh_yollari',
              'koz_soqqasi', 'koz_olmasi', 'sklera', 'shox_parda',
              'old_kamera', 'rangdor_parda_qorachiq',
              'gavhar', 'korish_otkirligi', 'shishasimon_tana', 'oftalmoskopiya']:
```

- [ ] **Step 3: Update visits_edit_data in doctor_patient_detail (around line 1349)**

Remove `'shikoyatlar'` and `'solution'` from the dict. Add new fields:
```python
'gavhar': v.gavhar,
'korish_otkirligi': v.korish_otkirligi,
'shishasimon_tana': v.shishasimon_tana,
'oftalmoskopiya': v.oftalmoskopiya,
```

- [ ] **Step 4: Same update in doctor_patient_full_history visits_edit_data (around line 1406)**

Same changes as step 3.

- [ ] **Step 5: Same update in doctor_panel visits_edit_data (around line 1269)**

Same changes — remove shikoyatlar/solution, add 4 new fields.

- [ ] **Step 6: Update admin_patient_detail if it references these fields**

Check and update any visits_edit_data there as well.

- [ ] **Step 7: Commit**

```bash
git add clinic/views.py
git commit -m "feat: update views to use new medical note fields, remove shikoyatlar/solution"
```

---

### Task 7: Add EyeVisualAcuity CRUD views

**Files:**
- Modify: `clinic/views.py` (add after doctor_delete_iop, around line 2615)

- [ ] **Step 1: Add import for EyeVisualAcuity at top of views.py**

Add `EyeVisualAcuity` to the model imports from `clinic.models`.

- [ ] **Step 2: Add add/edit/delete views**

Follow the exact same pattern as doctor_add_refraction/edit/delete:

```python
@login_required_custom
def doctor_add_visual_acuity(request, doctor_id, visit_id):
    visit = get_object_or_404(Visit, pk=visit_id)
    if request.method == 'POST':
        EyeVisualAcuity.objects.create(
            visit=visit, patient=visit.patient,
            uzoq_od_sph=request.POST.get('uzoq_od_sph', ''),
            uzoq_od_cyl=request.POST.get('uzoq_od_cyl', ''),
            uzoq_od_ax=request.POST.get('uzoq_od_ax', ''),
            uzoq_od_vis=request.POST.get('uzoq_od_vis', ''),
            uzoq_os_sph=request.POST.get('uzoq_os_sph', ''),
            uzoq_os_cyl=request.POST.get('uzoq_os_cyl', ''),
            uzoq_os_ax=request.POST.get('uzoq_os_ax', ''),
            uzoq_os_vis=request.POST.get('uzoq_os_vis', ''),
            yaqin_od_sph=request.POST.get('yaqin_od_sph', ''),
            yaqin_od_cyl=request.POST.get('yaqin_od_cyl', ''),
            yaqin_od_ax=request.POST.get('yaqin_od_ax', ''),
            yaqin_od_vis=request.POST.get('yaqin_od_vis', ''),
            yaqin_os_sph=request.POST.get('yaqin_os_sph', ''),
            yaqin_os_cyl=request.POST.get('yaqin_os_cyl', ''),
            yaqin_os_ax=request.POST.get('yaqin_os_ax', ''),
            yaqin_os_vis=request.POST.get('yaqin_os_vis', ''),
            mkl_od_sph=request.POST.get('mkl_od_sph', ''),
            mkl_od_cyl=request.POST.get('mkl_od_cyl', ''),
            mkl_od_ax=request.POST.get('mkl_od_ax', ''),
            mkl_od_vis=request.POST.get('mkl_od_vis', ''),
            mkl_os_sph=request.POST.get('mkl_os_sph', ''),
            mkl_os_cyl=request.POST.get('mkl_os_cyl', ''),
            mkl_os_ax=request.POST.get('mkl_os_ax', ''),
            mkl_os_vis=request.POST.get('mkl_os_vis', ''),
        )
    return redirect('doctor_patient_detail', doctor_id=doctor_id, patient_id=visit.patient_id)


@login_required_custom
def doctor_edit_visual_acuity(request, doctor_id, pk):
    va = get_object_or_404(EyeVisualAcuity, pk=pk)
    if request.method == 'POST':
        for field in ['uzoq_od_sph', 'uzoq_od_cyl', 'uzoq_od_ax', 'uzoq_od_vis',
                       'uzoq_os_sph', 'uzoq_os_cyl', 'uzoq_os_ax', 'uzoq_os_vis',
                       'yaqin_od_sph', 'yaqin_od_cyl', 'yaqin_od_ax', 'yaqin_od_vis',
                       'yaqin_os_sph', 'yaqin_os_cyl', 'yaqin_os_ax', 'yaqin_os_vis',
                       'mkl_od_sph', 'mkl_od_cyl', 'mkl_od_ax', 'mkl_od_vis',
                       'mkl_os_sph', 'mkl_os_cyl', 'mkl_os_ax', 'mkl_os_vis']:
            setattr(va, field, request.POST.get(field, ''))
        va.save()
    return redirect('doctor_patient_detail', doctor_id=doctor_id, patient_id=va.patient_id)


@login_required_custom
def doctor_delete_visual_acuity(request, doctor_id, pk):
    va = get_object_or_404(EyeVisualAcuity, pk=pk)
    patient_id = va.patient_id
    va.delete()
    return redirect('doctor_patient_detail', doctor_id=doctor_id, patient_id=patient_id)
```

- [ ] **Step 3: Commit**

```bash
git add clinic/views.py
git commit -m "feat: add EyeVisualAcuity CRUD views"
```

---

### Task 8: Add EyeExamForm CRUD views

**Files:**
- Modify: `clinic/views.py`

- [ ] **Step 1: Add imports**

Add `EyeExamForm` to model imports. Add `from clinic.utils import generate_protocol_number`.

- [ ] **Step 2: Add views**

```python
@login_required_custom
def doctor_add_eye_exam(request, doctor_id, visit_id):
    visit = get_object_or_404(Visit, pk=visit_id)
    doctor = get_object_or_404(Worker, pk=doctor_id)
    if request.method == 'POST':
        form = EyeExamForm(
            patient=visit.patient,
            visit=visit,
            doctor=doctor,
            protocol_number=generate_protocol_number(),
            kelish_sanasi=timezone.now(),
            filial='Optimed',
        )
        # Set all fields from POST
        for field in ['koz_anamezi', 'oyku',
                      'ref_ong_sph', 'ref_ong_cyl', 'ref_ong_axis',
                      'ref_chap_sph', 'ref_chap_cyl', 'ref_chap_axis',
                      'sub_ref_ong_sph', 'sub_ref_ong_cyl', 'sub_ref_ong_axis',
                      'sub_ref_chap_sph', 'sub_ref_chap_cyl', 'sub_ref_chap_axis',
                      'sik_ref_ong_sph', 'sik_ref_ong_cyl', 'sik_ref_ong_axis',
                      'sik_ref_chap_sph', 'sik_ref_chap_cyl', 'sik_ref_chap_axis',
                      'tuzatilmagan_korish_ong', 'tuzatilmagan_korish_chap',
                      'tuzatilgan_korish_ong', 'tuzatilgan_korish_chap',
                      'old_segment_ong', 'old_segment_chap',
                      'orqa_segment_ong', 'orqa_segment_chap',
                      'koz_bosimi_ong', 'koz_bosimi_chap',
                      'uzoq_ong_sph', 'uzoq_ong_cyl', 'uzoq_ong_axis',
                      'uzoq_chap_sph', 'uzoq_chap_cyl', 'uzoq_chap_axis',
                      'yaqin_ong_sph', 'yaqin_ong_cyl', 'yaqin_ong_axis',
                      'yaqin_chap_sph', 'yaqin_chap_cyl', 'yaqin_chap_axis',
                      'linza_ong', 'linza_chap', 'diametr_ong', 'diametr_chap',
                      'radius_ong', 'radius_chap', 'dioptriya_ong', 'dioptriya_chap',
                      'icd_kodi', 'icd_nomi', 'tashxis_turi', 'yonalish']:
            setattr(form, field, request.POST.get(field, ''))
        form.save()
    return redirect('doctor_patient_detail', doctor_id=doctor_id, patient_id=visit.patient_id)


@login_required_custom
def doctor_edit_eye_exam(request, doctor_id, pk):
    exam = get_object_or_404(EyeExamForm, pk=pk)
    if request.method == 'POST':
        for field in ['koz_anamezi', 'oyku',
                      'ref_ong_sph', 'ref_ong_cyl', 'ref_ong_axis',
                      'ref_chap_sph', 'ref_chap_cyl', 'ref_chap_axis',
                      'sub_ref_ong_sph', 'sub_ref_ong_cyl', 'sub_ref_ong_axis',
                      'sub_ref_chap_sph', 'sub_ref_chap_cyl', 'sub_ref_chap_axis',
                      'sik_ref_ong_sph', 'sik_ref_ong_cyl', 'sik_ref_ong_axis',
                      'sik_ref_chap_sph', 'sik_ref_chap_cyl', 'sik_ref_chap_axis',
                      'tuzatilmagan_korish_ong', 'tuzatilmagan_korish_chap',
                      'tuzatilgan_korish_ong', 'tuzatilgan_korish_chap',
                      'old_segment_ong', 'old_segment_chap',
                      'orqa_segment_ong', 'orqa_segment_chap',
                      'koz_bosimi_ong', 'koz_bosimi_chap',
                      'uzoq_ong_sph', 'uzoq_ong_cyl', 'uzoq_ong_axis',
                      'uzoq_chap_sph', 'uzoq_chap_cyl', 'uzoq_chap_axis',
                      'yaqin_ong_sph', 'yaqin_ong_cyl', 'yaqin_ong_axis',
                      'yaqin_chap_sph', 'yaqin_chap_cyl', 'yaqin_chap_axis',
                      'linza_ong', 'linza_chap', 'diametr_ong', 'diametr_chap',
                      'radius_ong', 'radius_chap', 'dioptriya_ong', 'dioptriya_chap',
                      'icd_kodi', 'icd_nomi', 'tashxis_turi', 'yonalish']:
            setattr(exam, field, request.POST.get(field, ''))
        exam.save()
    return redirect('doctor_patient_detail', doctor_id=doctor_id, patient_id=exam.patient_id)


@login_required_custom
def doctor_delete_eye_exam(request, doctor_id, pk):
    exam = get_object_or_404(EyeExamForm, pk=pk)
    patient_id = exam.patient_id
    exam.delete()
    return redirect('doctor_patient_detail', doctor_id=doctor_id, patient_id=patient_id)
```

- [ ] **Step 3: Commit**

```bash
git add clinic/views.py
git commit -m "feat: add EyeExamForm CRUD views"
```

---

### Task 9: Add DischargeForm CRUD views

**Files:**
- Modify: `clinic/views.py`

- [ ] **Step 1: Add DischargeForm to imports**

- [ ] **Step 2: Add views** (same pattern as EyeExamForm)

```python
@login_required_custom
def doctor_add_discharge(request, doctor_id, visit_id):
    visit = get_object_or_404(Visit, pk=visit_id)
    doctor = get_object_or_404(Worker, pk=doctor_id)
    if request.method == 'POST':
        form = DischargeForm(
            patient=visit.patient,
            visit=visit,
            doctor=doctor,
            protocol_number=generate_protocol_number(),
        )
        # Date fields
        yotish = request.POST.get('yotish_sanasi', '')
        chiqish = request.POST.get('chiqish_sanasi', '')
        form.yotish_sanasi = yotish if yotish else None
        form.chiqish_sanasi = chiqish if chiqish else None
        # Text fields
        for field in ['shikoyat_tarix', 'shaxsiy_oilaviy_tarix', 'tizimli_anamnez',
                      'koz_anamezi', 'tashxis_kodi_nomi', 'operatsiya_kodi_nomi',
                      'old_segment_ong', 'old_segment_chap',
                      'fundus_ong', 'fundus_chap',
                      'preop_ong', 'preop_chap',
                      'postop_ong', 'postop_chap',
                      'koz_bosimi_ong', 'koz_bosimi_chap',
                      'daraja_ong', 'daraja_chap',
                      'qovoq_ong', 'qovoq_chap',
                      'glob_ong', 'glob_chap',
                      'muhim_tekshiruv', 'anesteziya_turi', 'operatsiya_izohlar',
                      'chiqish_holati', 'davolash', 'anesteziya_izohi', 'ishlatilgan_linzalar']:
            setattr(form, field, request.POST.get(field, ''))
        form.save()
    return redirect('doctor_patient_detail', doctor_id=doctor_id, patient_id=visit.patient_id)


@login_required_custom
def doctor_edit_discharge(request, doctor_id, pk):
    form_obj = get_object_or_404(DischargeForm, pk=pk)
    if request.method == 'POST':
        yotish = request.POST.get('yotish_sanasi', '')
        chiqish = request.POST.get('chiqish_sanasi', '')
        form_obj.yotish_sanasi = yotish if yotish else None
        form_obj.chiqish_sanasi = chiqish if chiqish else None
        for field in ['shikoyat_tarix', 'shaxsiy_oilaviy_tarix', 'tizimli_anamnez',
                      'koz_anamezi', 'tashxis_kodi_nomi', 'operatsiya_kodi_nomi',
                      'old_segment_ong', 'old_segment_chap',
                      'fundus_ong', 'fundus_chap',
                      'preop_ong', 'preop_chap',
                      'postop_ong', 'postop_chap',
                      'koz_bosimi_ong', 'koz_bosimi_chap',
                      'daraja_ong', 'daraja_chap',
                      'qovoq_ong', 'qovoq_chap',
                      'glob_ong', 'glob_chap',
                      'muhim_tekshiruv', 'anesteziya_turi', 'operatsiya_izohlar',
                      'chiqish_holati', 'davolash', 'anesteziya_izohi', 'ishlatilgan_linzalar']:
            setattr(form_obj, field, request.POST.get(field, ''))
        form_obj.save()
    return redirect('doctor_patient_detail', doctor_id=doctor_id, patient_id=form_obj.patient_id)


@login_required_custom
def doctor_delete_discharge(request, doctor_id, pk):
    form_obj = get_object_or_404(DischargeForm, pk=pk)
    patient_id = form_obj.patient_id
    form_obj.delete()
    return redirect('doctor_patient_detail', doctor_id=doctor_id, patient_id=patient_id)
```

- [ ] **Step 3: Commit**

```bash
git add clinic/views.py
git commit -m "feat: add DischargeForm CRUD views"
```

---

### Task 10: Add receptionist documents views

**Files:**
- Modify: `clinic/views.py`

- [ ] **Step 1: Add receptionist_documents view**

```python
@login_required_custom
@role_required('receptionist')
def receptionist_documents(request):
    badge_counts = _get_receptionist_badge_counts()
    return render(request, 'receptionist/documents.html', {
        **badge_counts,
    })


@login_required_custom
@role_required('receptionist')
def receptionist_documents_search(request):
    query = request.GET.get('q', '').strip()
    results = []
    if query:
        from clinic.utils import generate_protocol_number  # just to ensure import path
        # Try protocol number search first
        exam = EyeExamForm.objects.filter(protocol_number=query).first()
        discharge = DischargeForm.objects.filter(protocol_number=query).first()
        if exam:
            results.append({'type': 'eye_exam', 'id': exam.pk, 'protocol': exam.protocol_number,
                           'patient_name': f"{exam.patient.name} {exam.patient.surname}",
                           'doctor_name': exam.doctor.surname if exam.doctor else '',
                           'date': exam.created_at.strftime('%d.%m.%Y %H:%M')})
        if discharge:
            results.append({'type': 'discharge', 'id': discharge.pk, 'protocol': discharge.protocol_number,
                           'patient_name': f"{discharge.patient.name} {discharge.patient.surname}",
                           'doctor_name': discharge.doctor.surname if discharge.doctor else '',
                           'date': discharge.created_at.strftime('%d.%m.%Y %H:%M')})
        # If no protocol match, try phone search
        if not results:
            from clinic.views import normalize_phone
            phone = normalize_phone(query)
            patients = Patient.objects.filter(phone=phone)
            for patient in patients:
                for e in patient.eye_exam_forms.all():
                    results.append({'type': 'eye_exam', 'id': e.pk, 'protocol': e.protocol_number,
                                   'patient_name': f"{e.patient.name} {e.patient.surname}",
                                   'doctor_name': e.doctor.surname if e.doctor else '',
                                   'date': e.created_at.strftime('%d.%m.%Y %H:%M')})
                for d in patient.discharge_forms.all():
                    results.append({'type': 'discharge', 'id': d.pk, 'protocol': d.protocol_number,
                                   'patient_name': f"{d.patient.name} {d.patient.surname}",
                                   'doctor_name': d.doctor.surname if d.doctor else '',
                                   'date': d.created_at.strftime('%d.%m.%Y %H:%M')})
    return JsonResponse({'results': results})


@login_required_custom
@role_required('receptionist')
def receptionist_document_view(request, form_type, pk):
    badge_counts = _get_receptionist_badge_counts()
    if form_type == 'eye_exam':
        doc = get_object_or_404(EyeExamForm, pk=pk)
        template = 'receptionist/document_eye_exam.html'
    else:
        doc = get_object_or_404(DischargeForm, pk=pk)
        template = 'receptionist/document_discharge.html'
    return render(request, template, {'doc': doc, **badge_counts})
```

- [ ] **Step 2: Commit**

```bash
git add clinic/views.py
git commit -m "feat: add receptionist documents search and view"
```

---

### Task 11: Update doctor_patient_detail view to include new data

**Files:**
- Modify: `clinic/views.py` (doctor_patient_detail function)

- [ ] **Step 1: Add prefetch for visual_acuities, eye_exam_forms, discharge_forms**

In the queryset for visits, add prefetch:
```python
.prefetch_related('refractions', 'krts', 'iops', 'visual_acuities', 'visit_services__service')
```

Also fetch patient-level forms:
```python
eye_exam_forms = patient.eye_exam_forms.select_related('doctor')
discharge_forms = patient.discharge_forms.select_related('doctor')
```

Pass to template context: `eye_exam_forms`, `discharge_forms`.

- [ ] **Step 2: Commit**

```bash
git add clinic/views.py
git commit -m "feat: include visual acuity, eye exam, discharge data in doctor patient detail"
```

---

## Chunk 3: URL Configuration

### Task 12: Add all new URL patterns

**Files:**
- Modify: `clinic/urls.py`

- [ ] **Step 1: Add visual acuity URLs** (after IOP URLs, around line 97)

```python
path('doctor/<int:doctor_id>/visit/<int:visit_id>/visual-acuity/add/', views.doctor_add_visual_acuity, name='doctor_add_visual_acuity'),
path('doctor/<int:doctor_id>/visual-acuity/<int:pk>/edit/', views.doctor_edit_visual_acuity, name='doctor_edit_visual_acuity'),
path('doctor/<int:doctor_id>/visual-acuity/<int:pk>/delete/', views.doctor_delete_visual_acuity, name='doctor_delete_visual_acuity'),
```

- [ ] **Step 2: Add eye exam URLs**

```python
path('doctor/<int:doctor_id>/visit/<int:visit_id>/eye-exam/add/', views.doctor_add_eye_exam, name='doctor_add_eye_exam'),
path('doctor/<int:doctor_id>/eye-exam/<int:pk>/edit/', views.doctor_edit_eye_exam, name='doctor_edit_eye_exam'),
path('doctor/<int:doctor_id>/eye-exam/<int:pk>/delete/', views.doctor_delete_eye_exam, name='doctor_delete_eye_exam'),
```

- [ ] **Step 3: Add discharge URLs**

```python
path('doctor/<int:doctor_id>/visit/<int:visit_id>/discharge/add/', views.doctor_add_discharge, name='doctor_add_discharge'),
path('doctor/<int:doctor_id>/discharge/<int:pk>/edit/', views.doctor_edit_discharge, name='doctor_edit_discharge'),
path('doctor/<int:doctor_id>/discharge/<int:pk>/delete/', views.doctor_delete_discharge, name='doctor_delete_discharge'),
```

- [ ] **Step 4: Add receptionist document URLs**

```python
path('receptionist/documents/', views.receptionist_documents, name='receptionist_documents'),
path('receptionist/documents/search/', views.receptionist_documents_search, name='receptionist_documents_search'),
path('receptionist/documents/<str:form_type>/<int:pk>/', views.receptionist_document_view, name='receptionist_document_view'),
```

- [ ] **Step 5: Commit**

```bash
git add clinic/urls.py
git commit -m "feat: add URL patterns for visual acuity, eye exam, discharge, and documents"
```

---

## Chunk 4: Doctor Templates — Tibbiy Yozuv & Visual Acuity

### Task 13: Update patient_detail.html — tibbiy yozuv to button-based

**Files:**
- Modify: `templates/doctor/patient_detail.html`

- [ ] **Step 1: Replace direct tibbiy yozuv form fields with button**

Replace the tibbiy yozuv section (around lines 97-115) — remove all 16 textarea fields. Replace with:
1. A row of 3 buttons: `[Tibbiy yozuv]` `[Ko'z ko'rigi]` `[Vipiska]`
2. Below buttons: display only non-empty tibbiy yozuv fields from the active visit, each with label (Uz + grey Russian) and value

Each field label format:
```html
<span class="field-label">Anamnesis morbi <span style="color:var(--text-muted);font-weight:400;font-size:11px;">(Анамнез заболевания)</span></span>
```

Russian translations for each field:
- anamnesis_morbi → Анамнез заболевания
- operatsiyalar → Операции
- tomizilgan → Назначения
- koz_oynak_kontakt_linza → Очки/Контактные линзы
- anamnesis_vitae → Анамнез жизни
- allergiya → Аллергия
- qovoqlar_koz_yosh_yollari → Веки/Слёзные пути
- koz_soqqasi → Глазница
- koz_olmasi → Глазное яблоко
- sklera → Склера
- shox_parda → Роговица
- old_kamera → Передняя камера
- rangdor_parda_qorachiq → Радужка/Зрачок
- gavhar → Хрусталик
- korish_otkirligi → Острота зрения
- shishasimon_tana → Стекловидное тело
- oftalmoskopiya → Офтальмоскопия
- tashxis → Диагноз
- tavsiya → Рекомендации

- [ ] **Step 2: Add tibbiy yozuv modal**

Add a modal `#tibbiyYozuvModal` with ALL 19 fields (always shown). Pre-fill from active visit data. Form POSTs to `doctor_update_visit`.

- [ ] **Step 3: Add ko'z ko'rigi modal**

Add `#kozKorigiModal` — full A4 form from the HTML reference. Pre-fill header fields (patient name, DOB, doctor). Form POSTs to `doctor_add_eye_exam`.

- [ ] **Step 4: Add vipiska modal**

Add `#vipiskaModal` — full discharge form from the HTML reference. Pre-fill header. Form POSTs to `doctor_add_discharge`.

- [ ] **Step 5: Commit**

```bash
git add templates/doctor/patient_detail.html
git commit -m "feat: convert tibbiy yozuv to button-based modal, add ko'z ko'rigi and vipiska modals"
```

---

### Task 14: Add visual acuity section to left column

**Files:**
- Modify: `templates/doctor/patient_detail.html`

- [ ] **Step 1: Add visual acuity button and display section**

Between the KRT/REF/IOP section and procedures section, add:
- `+ Korreksiya` button (opens `#addVaModal`)
- Display existing visual acuity records (compact, smaller font ~11px)
- Each record shows 3 tables: Uzoq/Yaqin/MKL with O'ng/Chap rows and SPH/CYL/AX/VIS columns
- Edit/delete buttons per record

- [ ] **Step 2: Add visual acuity add modal**

```html
<div class="modal-backdrop" id="addVaModal">
  <div class="modal" style="max-width:620px;">
    <h3>Ko'rish o'tkirligi korreksiya bilan <span style="color:var(--text-muted);font-size:12px;">(Острота зрения с коррекцией)</span></h3>
    <form method="post" action="{% url 'doctor_add_visual_acuity' doctor_id=doctor.id visit_id=active_visit.id %}">
      {% csrf_token %}
      <!-- 3 tables: Uzoq, Yaqin, MKL — each with header row + OD/OS rows + 4 columns -->
      <!-- Table: Uzoq (Вдаль) -->
      <h4 style="margin:12px 0 4px;font-size:12px;">Uzoq <span style="color:var(--text-muted);">(Вдаль)</span></h4>
      <div class="ref-krt-row" style="grid-template-columns:50px 1fr 1fr 1fr 1fr;">
        <span></span><span class="ref-krt-label">SPH</span><span class="ref-krt-label">CYL</span><span class="ref-krt-label">AX</span><span class="ref-krt-label">VIS</span>
      </div>
      <div class="ref-krt-row" style="grid-template-columns:50px 1fr 1fr 1fr 1fr;">
        <span class="ref-krt-label">OD</span>
        <input class="form-control" name="uzoq_od_sph">
        <input class="form-control" name="uzoq_od_cyl">
        <input class="form-control" name="uzoq_od_ax">
        <input class="form-control" name="uzoq_od_vis">
      </div>
      <div class="ref-krt-row" style="grid-template-columns:50px 1fr 1fr 1fr 1fr;">
        <span class="ref-krt-label">OS</span>
        <input class="form-control" name="uzoq_os_sph">
        <input class="form-control" name="uzoq_os_cyl">
        <input class="form-control" name="uzoq_os_ax">
        <input class="form-control" name="uzoq_os_vis">
      </div>
      <!-- Repeat for Yaqin and MKL with same structure -->
      <button type="submit" class="btn btn-primary" style="margin-top:16px;">Saqlash</button>
    </form>
  </div>
</div>
```

- [ ] **Step 3: Add edit modal (same structure, pre-filled via JS)**

- [ ] **Step 4: Make REF/KRT/IOP history items more compact**

Reduce font-size to 11px, tighter padding for the data display sections in the right column.

- [ ] **Step 5: Commit**

```bash
git add templates/doctor/patient_detail.html
git commit -m "feat: add visual acuity section with modal, compact history items"
```

---

### Task 15: Add history display for eye exam and discharge forms

**Files:**
- Modify: `templates/doctor/patient_detail.html`

- [ ] **Step 1: Add collapsed cards in history section**

After the existing visit history, add sections for eye_exam_forms and discharge_forms:
```html
{% for exam in eye_exam_forms %}
<div class="card" style="margin-bottom:8px;padding:12px;">
  <div style="display:flex;justify-content:space-between;align-items:center;cursor:pointer;" onclick="toggleFormCard(this)">
    <div>
      <span class="badge badge-info">Ko'z ko'rigi</span>
      <span style="font-size:12px;margin-left:8px;">#{{ exam.protocol_number }}</span>
      <span style="font-size:11px;color:var(--text-muted);margin-left:8px;">{{ exam.created_at|date:"d.m.Y" }}</span>
      <span style="font-size:11px;color:var(--text-muted);margin-left:8px;">{{ exam.doctor.surname }}</span>
    </div>
    <span style="font-size:11px;">&#9660;</span>
  </div>
</div>
{% endfor %}
```

- [ ] **Step 2: Add overlay panel for full A4 view**

When card is clicked, open overlay with blurred background showing the full A4-formatted form. Include print button.

```html
<div id="formOverlay" style="display:none;position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.5);backdrop-filter:blur(4px);z-index:1000;overflow-y:auto;padding:32px;">
  <div style="max-width:210mm;margin:0 auto;background:white;padding:20mm;position:relative;" id="formContent">
    <button onclick="window.print()" class="btn btn-primary btn-sm" style="position:absolute;top:8px;right:8px;">Chop etish</button>
    <!-- A4 content injected by JS -->
  </div>
  <button onclick="closeFormOverlay()" style="position:fixed;top:16px;right:16px;z-index:1001;" class="btn btn-secondary">✕</button>
</div>
```

- [ ] **Step 3: Add @media print CSS**

```css
@media print {
  body * { visibility: hidden; }
  #formContent, #formContent * { visibility: visible; }
  #formContent { position: absolute; left: 0; top: 0; width: 210mm; }
}
```

- [ ] **Step 4: Commit**

```bash
git add templates/doctor/patient_detail.html static/css/style.css
git commit -m "feat: add history cards and A4 overlay for eye exam and discharge forms"
```

---

## Chunk 5: Doctor Full History & Edit Modal Updates

### Task 16: Update patient_full_history.html

**Files:**
- Modify: `templates/doctor/patient_full_history.html`

- [ ] **Step 1: Remove shikoyatlar from display and edit modal**

Remove lines referencing `shikoyatlar` and `solution`. Add the 4 new fields (gavhar, korish_otkirligi, shishasimon_tana, oftalmoskopiya) with Russian labels in the same pattern.

- [ ] **Step 2: Add eye exam and discharge form cards in history**

Same collapsed card pattern as in patient_detail.html.

- [ ] **Step 3: Commit**

```bash
git add templates/doctor/patient_full_history.html
git commit -m "feat: update full history template with new fields and form cards"
```

---

### Task 17: Update edit visit modal in patient_detail.html

**Files:**
- Modify: `templates/doctor/patient_detail.html` (edit modal around line 257)

- [ ] **Step 1: Update editVisitBackdrop modal fields**

Remove shikoyatlar/solution textareas. Add the 4 new field textareas with labels:
```html
<div class="form-group">
  <label>Gavhar <span style="color:var(--text-muted);font-weight:400;font-size:10px;">(Хрусталик)</span></label>
  <textarea class="form-control" name="gavhar" rows="2"></textarea>
</div>
```

- [ ] **Step 2: Update the JS that populates edit modal from visits_edit_json**

Remove references to `shikoyatlar` and `solution` in the JavaScript that reads `visits_edit_json` and populates modal fields. Add the 4 new fields.

- [ ] **Step 3: Commit**

```bash
git add templates/doctor/patient_detail.html
git commit -m "feat: update edit visit modal with new fields"
```

---

## Chunk 6: Receptionist Panel Changes

### Task 18: Rename Tarix to Shifokorlar, remove Bemorlar tab

**Files:**
- Modify: `templates/base.html:79-82` (sidebar nav)
- Modify: `templates/receptionist/history.html`

- [ ] **Step 1: Update sidebar label**

In `templates/base.html`, change the "Tarix" nav link text to "Shifokorlar".

- [ ] **Step 2: Update history.html — remove patient tab**

Remove the tab navigation and "Bemorlar" tab content. Keep only the doctor list table. Update the page title to "Shifokorlar".

- [ ] **Step 3: Commit**

```bash
git add templates/base.html templates/receptionist/history.html
git commit -m "feat: rename Tarix to Shifokorlar, remove patient tab"
```

---

### Task 19: Add Hujjatlar nav item and page

**Files:**
- Modify: `templates/base.html` (add nav item after Tarix/Shifokorlar)
- Create: `templates/receptionist/documents.html`

- [ ] **Step 1: Add sidebar nav item**

In `templates/base.html`, after the Shifokorlar link, add:
```html
<a href="{% url 'receptionist_documents' %}" class="nav-link {% if request.path == '/receptionist/documents/' %}active{% endif %}">
  <span>Hujjatlar</span>
</a>
```

- [ ] **Step 2: Create documents.html template**

```html
{% extends "base.html" %}
{% block title %}Hujjatlar{% endblock %}
{% block content %}
<div class="page-header">
  <h1>Hujjatlar</h1>
</div>

<div class="card">
  <div style="display:flex;gap:12px;margin-bottom:20px;">
    <input type="text" id="docSearch" class="form-control" placeholder="Telefon raqami yoki protokol raqami..." style="max-width:400px;">
    <button class="btn btn-primary" onclick="searchDocuments()">Qidirish</button>
  </div>
  <div id="docResults"></div>
</div>

<!-- Full form overlay -->
<div id="docOverlay" style="display:none;position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.5);backdrop-filter:blur(4px);z-index:1000;overflow-y:auto;padding:32px;">
  <div style="max-width:210mm;margin:0 auto;background:white;position:relative;" id="docContent">
  </div>
  <button onclick="closeDocOverlay()" style="position:fixed;top:16px;right:16px;z-index:1001;" class="btn btn-secondary">✕</button>
</div>

<script>
function searchDocuments() {
  const q = document.getElementById('docSearch').value.trim();
  if (!q) return;
  fetch(`{% url 'receptionist_documents_search' %}?q=${encodeURIComponent(q)}`)
    .then(r => r.json())
    .then(data => {
      const container = document.getElementById('docResults');
      if (!data.results.length) {
        container.innerHTML = '<p style="color:var(--text-muted);">Hujjat topilmadi</p>';
        return;
      }
      container.innerHTML = data.results.map(r => `
        <div class="card" style="margin-bottom:8px;padding:12px;cursor:pointer;" onclick="viewDocument('${r.type}', ${r.id})">
          <div style="display:flex;justify-content:space-between;align-items:center;">
            <div>
              <span class="badge ${r.type === 'eye_exam' ? 'badge-info' : 'badge-success'}">${r.type === 'eye_exam' ? "Ko'z ko'rigi" : 'Vipiska'}</span>
              <span style="font-size:12px;margin-left:8px;">#${r.protocol}</span>
              <span style="font-size:12px;margin-left:8px;">${r.patient_name}</span>
              <span style="font-size:11px;color:var(--text-muted);margin-left:8px;">${r.doctor_name}</span>
            </div>
            <span style="font-size:11px;color:var(--text-muted);">${r.date}</span>
          </div>
        </div>
      `).join('');
    });
}

function viewDocument(type, id) {
  fetch(`/receptionist/documents/${type}/${id}/`)
    .then(r => r.text())
    .then(html => {
      document.getElementById('docContent').innerHTML = html;
      document.getElementById('docOverlay').style.display = 'block';
      document.body.style.overflow = 'hidden';
    });
}

function closeDocOverlay() {
  document.getElementById('docOverlay').style.display = 'none';
  document.body.style.overflow = '';
}

document.getElementById('docSearch').addEventListener('keydown', e => {
  if (e.key === 'Enter') searchDocuments();
});
</script>
{% endblock %}
```

- [ ] **Step 3: Commit**

```bash
git add templates/base.html templates/receptionist/documents.html
git commit -m "feat: add Hujjatlar page for receptionist document search"
```

---

### Task 20: Create A4 document templates for receptionist

**Files:**
- Create: `templates/receptionist/document_eye_exam.html`
- Create: `templates/receptionist/document_discharge.html`

- [ ] **Step 1: Create eye exam A4 template**

This should be a standalone HTML fragment (not extending base.html — loaded via fetch). A4 format with proper tables matching the reference in `uzbek_translations_only.html` (Page 3). Include print button and @media print styles.

Key sections:
- Header: protocol number, patient name, DOB, age, doctor, date, filial
- Ko'z anamezi
- Refraction table (O'ng/Chap × SPH/CYL/AXIS for refraktsiya, subyektiv, sikloplejili)
- Clinical findings grid (tuzatilmagan/tuzatilgan ko'rish, old/orqa segment, ko'z bosimi)
- Oyku note
- Prescription table (Uzoq/Yaqin × SPH/CYL/AXIS)
- Lens table (Linza/Diametr/Radius/Dioptriya × O'ng/Chap)
- ICD table
- Doctor signature

All labels bilingual: Uzbek + grey Russian in brackets.

- [ ] **Step 2: Create discharge A4 template**

Same standalone HTML fragment. A4 format matching reference (Page 4). Title: "Vipiska" / "Выписка".

Key sections:
- Header: protocol, patient info, doctor, dates
- History section (shikoyat, shaxsiy/oilaviy tarix, tizimli anamnez, ko'z anamezi)
- Diagnosis & operation codes
- Exam findings table (Old segment, Fundus, Preop, Postop, TO, Daraja, Qovoq, Glob × O'ng/Chap)
- Muhim tekshiruv, Anesteziya turi
- Operatsiya izohlar
- Chiqish holati, Davolash, Anesteziya izohi, Ishlatilgan linzalar
- Doctor signature

- [ ] **Step 3: Commit**

```bash
git add templates/receptionist/document_eye_exam.html templates/receptionist/document_discharge.html
git commit -m "feat: add A4 document templates for eye exam and discharge"
```

---

## Chunk 7: Laboratory Reference Values

### Task 21: Add reference values to LAB_SERVICES

**Files:**
- Modify: `clinic/lab_services.py`

- [ ] **Step 1: Convert 3-tuples to 4-tuples with reference values**

Research standard medical reference ranges. Update each entry from:
```python
(1, "Время свертываемости", 20000),
```
To:
```python
(1, "Время свертываемости", 20000, "5-10 мин"),
```

Key reference values to add (standard ranges):
- Гематология: Гемоглобин (М: 130-170 г/л, Ж: 120-150 г/л), Эритроциты (М: 4.0-5.5, Ж: 3.5-5.0 ×10¹²/л), Лейкоциты (4.0-9.0 ×10⁹/л), Тромбоциты (150-400 ×10⁹/л), СОЭ (М: 2-10 мм/ч, Ж: 2-15 мм/ч), etc.
- Биохимия: Глюкоза (3.9-6.1 ммоль/л), АЛТ (до 40 Ед/л), АСТ (до 40 Ед/л), Билирубин общий (3.4-20.5 мкмоль/л), Креатинин (М: 62-115 мкмоль/л, Ж: 53-97 мкмоль/л), etc.
- Гормоны: ТТГ (0.4-4.0 мМЕ/л), Т3 (1.2-2.7 нмоль/л), Т4 (62-141 нмоль/л), etc.
- Use empty string `""` for tests where reference values don't apply (e.g., blood type)

- [ ] **Step 2: Commit**

```bash
git add clinic/lab_services.py
git commit -m "feat: add standard reference values to all lab services"
```

---

### Task 22: Update lab visit detail template

**Files:**
- Modify: `templates/lab/visit_detail.html`

- [ ] **Step 1: Add reference values column and compact layout**

Add a new `<th>` for "Referens qiymatlari" between price and result columns. Build a lookup dict in the view or use a template tag to map service_number → reference_value.

Update the table row to include:
```html
<td style="font-size:11px;color:var(--text-muted);white-space:nowrap;">{{ ref_value }}</td>
```

Reduce padding on all `td` elements to make rows more compact:
```css
td, th { padding: 4px 8px; font-size: 12px; }
```

- [ ] **Step 2: Update lab_visit_detail view to pass reference values**

In `clinic/views.py`, in `lab_visit_detail`, build a dict of service_number → reference_value from LAB_SERVICES:

```python
from clinic.lab_services import LAB_SERVICES
ref_values = {s[0]: s[3] if len(s) > 3 else '' for s in LAB_SERVICES}
```

Pass `ref_values` to template. In template, access via `{{ ref_values|dict_lookup:ls.service_number }}` (or annotate each service in the view).

Simpler approach: annotate in the view:
```python
for ls in lab_visit.lab_services.all():
    ls.ref_value = ref_values.get(ls.service_number, '')
```

- [ ] **Step 3: Commit**

```bash
git add templates/lab/visit_detail.html clinic/views.py
git commit -m "feat: add reference values column to lab visit detail, compact layout"
```

---

## Chunk 8: Seed Data & Final Cleanup

### Task 23: Update seed_data.py

**Files:**
- Modify: `seed_data.py`

- [ ] **Step 1: Remove shikoyatlar/solution usage**

Find and remove any references to `shikoyatlar` and `solution` fields. Add seed data for the 4 new fields (gavhar, korish_otkirligi, shishasimon_tana, oftalmoskopiya) in the same pattern as existing medical note fields.

- [ ] **Step 2: Add sample EyeVisualAcuity, EyeExamForm, DischargeForm records**

Add a few sample records in seed_data.py so the features are testable after reseed.

- [ ] **Step 3: Commit**

```bash
git add seed_data.py
git commit -m "feat: update seed data for new models and fields"
```

---

### Task 24: Reseed and verify

- [ ] **Step 1: Reseed database**

```bash
cd /Users/iskandarodilov/Desktop/CRM
source venv/bin/activate
rm -f db.sqlite3
python manage.py migrate
python seed_data.py
```

- [ ] **Step 2: Start server and verify**

```bash
python manage.py runserver 8000
```

Verify:
1. Login as doctor → patient detail → tibbiy yozuv button opens modal with 19 fields
2. Ko'z ko'rigi button → A4 form modal
3. Vipiska button → discharge form modal
4. Visual acuity section with add/edit/delete
5. History shows collapsed eye exam and discharge cards
6. Login as receptionist → Shifokorlar tab (no Bemorlar)
7. Hujjatlar page → search by phone/protocol → card results → overlay with print
8. Login as lab → visit detail shows reference values column

- [ ] **Step 3: Final commit**

```bash
git add -A
git commit -m "feat: complete doctor/receptionist/lab panel enhancements"
```
