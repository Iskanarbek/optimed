# Panel Fixes Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix 7 issues across Receptionist, Doctor, and Optika panels — broken lab search, missing recent docs, A4-only form views, transliterated Russian text, missing forms in full history, wrong seller landing page, and redesigned sell UI with discount.

**Architecture:** All changes are in `clinic/views.py`, `clinic/models.py`, and existing templates. One new migration for `GlassSale.discount_amount`. No new URLs needed. The doctor form cards switch from A4 overlay to collapsible inline cards with in-place edit mode.

**Tech Stack:** Django 6.0.3, SQLite, vanilla JS, existing CSS variables.

---

## Chunk 1: Quick Backend Fixes

### Task 1: Fix broken lab search (4-tuple unpacking)

**Files:**
- Modify: `clinic/views.py` — `api_lab_services_search` function (~line 2484)

**Root cause:** `LAB_SERVICES` now has 4-tuples `(num, name, price, ref_value)` but the view still unpacks as 3-tuples.

- [ ] **Open `clinic/views.py` and find `api_lab_services_search`** (grep: `def api_lab_services_search`)

- [ ] **Fix the unpacking line in the JsonResponse:**

Change:
```python
return JsonResponse({'results': [
    {'number': num, 'name': name, 'price': price}
    for num, name, price in results
]})
```
To:
```python
return JsonResponse({'results': [
    {'number': num, 'name': name, 'price': price}
    for num, name, price, *rest in results
]})
```

- [ ] **Verify the server starts without error:**
```bash
cd /Users/iskandarodilov/Desktop/CRM
source venv/bin/activate
python manage.py check
```
Expected: `System check identified no issues (0 silenced).`

---

### Task 2: Receptionist Hujjatlar — show recent documents on load

**Files:**
- Modify: `clinic/views.py` — `receptionist_documents` function
- Modify: `templates/receptionist/documents.html`

- [ ] **Update `receptionist_documents` view** to load recent records.

Find `def receptionist_documents` and replace:
```python
def receptionist_documents(request):
    notif_count, proc_count = _get_receptionist_badge_counts()
    return render(request, 'receptionist/documents.html', {
        'notif_count': notif_count,
        'proc_count': proc_count,
    })
```
With:
```python
def receptionist_documents(request):
    notif_count, proc_count = _get_receptionist_badge_counts()
    # Recent documents for initial display
    recent_exams = EyeExamForm.objects.select_related('patient', 'doctor').order_by('-created_at')[:10]
    recent_discharges = DischargeForm.objects.select_related('patient', 'doctor').order_by('-created_at')[:10]
    # Merge and sort by created_at descending
    recent_docs = sorted(
        [{'type': 'eye_exam', 'id': e.pk, 'protocol': e.protocol_number,
          'patient_name': f"{e.patient.name} {e.patient.surname}",
          'doctor_name': e.doctor.full_name if e.doctor else '—',
          'date': e.created_at.strftime('%d.%m.%Y %H:%M')} for e in recent_exams] +
        [{'type': 'discharge', 'id': d.pk, 'protocol': d.protocol_number,
          'patient_name': f"{d.patient.name} {d.patient.surname}",
          'doctor_name': d.doctor.full_name if d.doctor else '—',
          'date': d.created_at.strftime('%d.%m.%Y %H:%M')} for d in recent_discharges],
        key=lambda x: x['date'], reverse=True
    )[:10]
    return render(request, 'receptionist/documents.html', {
        'notif_count': notif_count,
        'proc_count': proc_count,
        'recent_docs': recent_docs,
    })
```

- [ ] **Update `templates/receptionist/documents.html`** to show recent docs by default.

Replace the `<div id="docInitial">` section and add a recent-docs section. The full updated template:

```html
{% extends 'base.html' %}
{% block title %}Hujjatlar — Optimed CRM{% endblock %}
{% block nav_documents %}active{% endblock %}

{% block content %}
<div class="page-header">
    <div>
        <h1>Hujjatlar</h1>
        <p>Ko'z ko'rigi va Vipiska hujjatlarini qidirish</p>
    </div>
</div>

<div class="search-bar" style="margin-bottom:20px;">
    <input type="text" id="docSearchInput" placeholder="Telefon raqami yoki protokol raqami bo'yicha qidirish..." onkeydown="if(event.key==='Enter')searchDocuments()">
    <button class="btn btn-primary" onclick="searchDocuments()">Qidirish</button>
    <button class="btn btn-secondary" id="clearSearchBtn" style="display:none;" onclick="clearSearch()">Tozalash</button>
</div>

<div id="docResults"></div>
<div id="docEmpty" style="display:none;" class="empty-state"><p>Hujjatlar topilmadi</p></div>

<!-- Recent docs shown by default -->
<div id="docRecent">
    <div style="font-size:12px;color:var(--text-muted);margin-bottom:10px;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;">So'nggi hujjatlar</div>
    {% for item in recent_docs %}
    <div class="doc-card">
        <div class="doc-card-info">
            <h4><span class="doc-card-type {{ item.type }}">{% if item.type == 'eye_exam' %}Ko'z ko'rigi{% else %}Vipiska{% endif %}</span>{{ item.patient_name }}</h4>
            <p>Protokol: {{ item.protocol }} &middot; Doktor: {{ item.doctor_name }} &middot; {{ item.date }}</p>
        </div>
        <div class="doc-card-actions">
            <button class="btn btn-secondary btn-sm" onclick="viewDocument('{{ item.type }}', {{ item.id }})">Ko'rish</button>
        </div>
    </div>
    {% empty %}
    <div class="empty-state"><p>Hali hujjatlar yaratilmagan</p></div>
    {% endfor %}
</div>

<!-- A4 OVERLAY -->
<div class="form-overlay" id="formOverlay" style="display:none;">
    <div class="form-overlay-header">
        <button class="btn btn-secondary btn-sm" onclick="closeOverlay()">Yopish</button>
        <button class="btn btn-primary btn-sm" onclick="window.print()">Chop etish</button>
    </div>
    <div class="form-overlay-body" id="overlayBody"></div>
</div>

<style>
.doc-card { background:var(--card-bg,#fff); border:1px solid var(--border); border-radius:var(--radius); padding:14px 16px; margin-bottom:10px; display:flex; justify-content:space-between; align-items:center; }
.doc-card-info { flex:1; }
.doc-card-info h4 { margin:0 0 4px; font-size:14px; }
.doc-card-info p { margin:0; font-size:12px; color:var(--text-muted); }
.doc-card-type { display:inline-block; padding:2px 8px; border-radius:4px; font-size:11px; font-weight:600; margin-right:8px; }
.doc-card-type.eye_exam { background:#e8f5e9; color:#2e7d32; }
.doc-card-type.discharge { background:#e3f2fd; color:#1565c0; }
.doc-card-actions { display:flex; gap:8px; }
.form-overlay { position:fixed; top:0; left:0; right:0; bottom:0; background:#f0f0f0; z-index:1000; overflow-y:auto; }
.form-overlay-header { position:sticky; top:0; background:var(--dark); padding:12px 24px; display:flex; gap:8px; justify-content:flex-end; z-index:1001; }
.form-overlay-body { max-width:210mm; margin:20px auto; background:#fff; padding:20mm; min-height:297mm; box-shadow:0 2px 8px rgba(0,0,0,0.15); }
@media print {
    body * { visibility:hidden; }
    .form-overlay, .form-overlay * { visibility:visible; }
    .form-overlay { position:absolute; top:0; left:0; background:#fff; }
    .form-overlay-header { display:none; }
    .form-overlay-body { box-shadow:none; margin:0; padding:10mm; }
}
</style>

<script>
function searchDocuments() {
    var q = document.getElementById('docSearchInput').value.trim();
    if (!q) return;
    document.getElementById('docRecent').style.display = 'none';
    document.getElementById('docEmpty').style.display = 'none';
    document.getElementById('clearSearchBtn').style.display = '';
    document.getElementById('docResults').innerHTML = '<p style="color:var(--text-muted);padding:12px;">Qidirilmoqda...</p>';

    fetch('{% url "receptionist_documents_search" %}?q=' + encodeURIComponent(q))
        .then(function(r) { return r.json(); })
        .then(function(data) {
            if (!data.results || data.results.length === 0) {
                document.getElementById('docResults').innerHTML = '';
                document.getElementById('docEmpty').style.display = 'block';
                return;
            }
            var html = '';
            data.results.forEach(function(item) {
                var typeLabel = item.type === 'eye_exam' ? "Ko'z ko'rigi" : 'Vipiska';
                var typeClass = item.type;
                html += '<div class="doc-card">' +
                    '<div class="doc-card-info">' +
                    '<h4><span class="doc-card-type ' + typeClass + '">' + typeLabel + '</span>' + item.patient_name + '</h4>' +
                    '<p>Protokol: ' + item.protocol + ' &middot; Doktor: ' + item.doctor_name + ' &middot; ' + item.date + '</p>' +
                    '</div>' +
                    '<div class="doc-card-actions">' +
                    '<button class="btn btn-secondary btn-sm" onclick="viewDocument(\'' + item.type + '\',' + item.id + ')">Ko\'rish</button>' +
                    '</div></div>';
            });
            document.getElementById('docResults').innerHTML = html;
        });
}

function clearSearch() {
    document.getElementById('docSearchInput').value = '';
    document.getElementById('docResults').innerHTML = '';
    document.getElementById('docEmpty').style.display = 'none';
    document.getElementById('clearSearchBtn').style.display = 'none';
    document.getElementById('docRecent').style.display = 'block';
}

function viewDocument(type, id) {
    fetch('{% url "receptionist_document_view" "eye_exam" 0 %}'.replace('eye_exam', type).replace('/0/', '/' + id + '/'))
        .then(function(r) { return r.text(); })
        .then(function(html) {
            document.getElementById('overlayBody').innerHTML = html;
            document.getElementById('formOverlay').style.display = 'block';
            document.body.style.overflow = 'hidden';
        });
}

function closeOverlay() {
    document.getElementById('formOverlay').style.display = 'none';
    document.body.style.overflow = '';
}
</script>
{% endblock %}
```

- [ ] **Run Django check:**
```bash
python manage.py check
```
Expected: no issues.

---

## Chunk 2: Doctor Panel — Cyrillic Text

### Task 3: Fix Russian text transliteration → proper Cyrillic in patient_detail.html

**Files:**
- Modify: `templates/doctor/patient_detail.html` — all `.a4-ru` span contents

**Problem:** Russian hints written in Latin (e.g., `Osmotr glaz`) instead of Cyrillic (`Осмотр глаз`).

- [ ] **In `templates/doctor/patient_detail.html`, do a bulk find-and-replace** of all transliterated Russian texts inside `a4-ru` spans. The full replacement map:

| Find (transliterated) | Replace (Cyrillic) |
|---|---|
| `(Osmotr glaz)` | `(Осмотр глаз)` |
| `(Protokol No)` | `(Протокол №)` |
| `(Imya patsienta)` | `(Имя пациента)` |
| `(Data rozhd.)` | `(Дата рождения)` |
| `(Vrach)` | `(Врач)` |
| `(Data postupl.)` | `(Дата поступления)` |
| `(Filial)` | `(Филиал)` |
| `(Glaznoy anamnez)` | `(Глазной анамнез)` |
| `(Pravyy)` | `(Правый)` |
| `(Levyy)` | `(Левый)` |
| `(Refraktsiya)` | `(Рефракция)` |
| `(Sub. refraktsiya)` | `(Суб. рефракция)` |
| `(Tsiklopleg. refraktsiya)` | `(Циклопл. рефракция)` |
| `(Nekorr. zreniye)` | `(Некорр. зрение)` |
| `(Korr. zreniye)` | `(Корр. зрение)` |
| `(Peredn. segm.)` | `(Перед. сегмент)` |
| `(Zadn. segm.)` | `(Задн. сегмент)` |
| `(VGD)` | `(ВГД)` |
| `(Istoriya bolezni)` | `(История болезни)` |
| `(Daleko)` | `(Вдаль)` |
| `(Blizko)` | `(Вблизи)` |
| `(Pr.)` | `(Пр.)` |
| `(Lev.)` | `(Лев.)` |
| `(Linza)` | `(Линза)` |
| `(Diametr)` | `(Диаметр)` |
| `(Radius)` | `(Радиус)` |
| `(Dioptriya)` | `(Диоптрия)` |
| `(Kod MKB)` | `(Код МКБ)` |
| `(Nazvaniye MKB)` | `(Название МКБ)` |
| `(Tip diagnoza)` | `(Тип диагноза)` |
| `(Storona)` | `(Сторона)` |
| `(Oftalmologiya)` | `(Офтальмология)` |
| `(Imya i familiya)` | `(Имя и фамилия)` |
| `(Data rozhd. – Pol)` | `(Дата рожд. – Пол)` |
| `(Adres patsienta)` | `(Адрес пациента)` |
| `(Telefon)` | `(Телефон)` |
| `(Data post.–vypiski)` | `(Дата пост.–выписки)` |
| `(Zhaloby / Istoriya)` | `(Жалобы / История)` |
| `(Lich./Sem. anamnez)` | `(Личн./Сем. анамнез)` |
| `(Sistemnyy anamnez)` | `(Системный анамнез)` |
| `(Glaznoy anamnez)` | `(Глазной анамнез)` |
| `(Kod–nazv. diagnoza)` | `(Код–назв. диагноза)` |
| `(Kod–nazv. operatsii)` | `(Код–назв. операции)` |
| `(Dannyye osmotra)` | `(Данные осмотра)` |
| `(Peredn. segm.)` | `(Перед. сегмент)` |
| `(Glaznoye dno)` | `(Глазное дно)` |
| `(Do operatsii)` | `(До операции)` |
| `(Posle operatsii)` | `(После операции)` |
| `(VGD)` | `(ВГД)` |
| `(Stepen)` | `(Степень)` |
| `(Veki)` | `(Веки)` |
| `(Glob)` | `(Глоб)` |
| `(Vazhn. isslед.)` | `(Важн. исслед.)` |
| `(Anesteziya)` | `(Анестезия)` |
| `(Zamechaniya)` | `(Замечания)` |
| `(Sost. pri vypiski)` | `(Сост. при выписке)` |
| `(Lecheniye)` | `(Лечение)` |
| `(Linzy)` | `(Линзы)` |
| `(Anesteziya izoh)` | `(Примечание анест.)` |

Use the Edit tool to replace these one by one, or use a Bash sed script for the bulk replacements:

```bash
cd /Users/iskandarodilov/Desktop/CRM
sed -i '' \
  -e 's/(Osmotr glaz)/(Осмотр глаз)/g' \
  -e 's/(Protokol No)/(Протокол №)/g' \
  -e 's/(Imya patsienta)/(Имя пациента)/g' \
  -e 's/(Data rozhd\.)/(Дата рождения)/g' \
  -e 's/(Vrach)/(Врач)/g' \
  -e 's/(Data postupl\.)/(Дата поступления)/g' \
  -e 's/(Filial)/(Филиал)/g' \
  -e 's/(Glaznoy anamnez)/(Глазной анамнез)/g' \
  -e 's/(Pravyy)/(Правый)/g' \
  -e 's/(Levyy)/(Левый)/g' \
  -e 's/(Refraktsiya)/(Рефракция)/g' \
  -e 's/(Sub\. refraktsiya)/(Суб. рефракция)/g' \
  -e 's/(Tsiklopleg\. refraktsiya)/(Циклопл. рефракция)/g' \
  -e 's/(Nekorr\. zreniye)/(Некорр. зрение)/g' \
  -e 's/(Korr\. zreniye)/(Корр. зрение)/g' \
  -e 's/(Peredn\. segm\.)/(Перед. сегмент)/g' \
  -e 's/(Zadn\. segm\.)/(Задн. сегмент)/g' \
  -e 's/(VGD)/(ВГД)/g' \
  -e 's/(Istoriya bolezni)/(История болезни)/g' \
  -e 's/(Daleko)/(Вдаль)/g' \
  -e 's/(Blizko)/(Вблизи)/g' \
  -e 's/(Pr\.)/(Пр.)/g' \
  -e 's/(Lev\.)/(Лев.)/g' \
  -e 's/(Linza)/(Линза)/g' \
  -e 's/(Diametr)/(Диаметр)/g' \
  -e 's/(Radius)/(Радиус)/g' \
  -e 's/(Dioptriya)/(Диоптрия)/g' \
  -e 's/(Kod MKB)/(Код МКБ)/g' \
  -e 's/(Nazvaniye MKB)/(Название МКБ)/g' \
  -e 's/(Tip diagnoza)/(Тип диагноза)/g' \
  -e 's/(Storona)/(Сторона)/g' \
  -e 's/(Oftalmologiya)/(Офтальмология)/g' \
  -e 's/(Imya i familiya)/(Имя и фамилия)/g' \
  -e 's/(Data rozhd\. – Pol)/(Дата рожд. – Пол)/g' \
  -e 's/(Adres patsienta)/(Адрес пациента)/g' \
  -e 's/(Telefon)/(Телефон)/g' \
  -e 's/(Data post\.–vypiski)/(Дата пост.–выписки)/g' \
  -e 's/(Zhaloby \/ Istoriya)/(Жалобы \/ История)/g' \
  -e 's/(Lich\.\/Sem\. anamnez)/(Личн.\/Сем. анамнез)/g' \
  -e 's/(Sistemnyy anamnez)/(Системный анамнез)/g' \
  -e 's/(Kod–nazv\. diagnoza)/(Код–назв. диагноза)/g' \
  -e 's/(Kod–nazv\. operatsii)/(Код–назв. операции)/g' \
  -e 's/(Dannyye osmotra)/(Данные осмотра)/g' \
  -e 's/(Glaznoye dno)/(Глазное дно)/g' \
  -e 's/(Do operatsii)/(До операции)/g' \
  -e 's/(Posle operatsii)/(После операции)/g' \
  templates/doctor/patient_detail.html
```

- [ ] **Verify** by grepping for remaining transliterated patterns:
```bash
grep -c "Osmotr\|Protokol No\|Imya\|rozhd\." templates/doctor/patient_detail.html
```
Expected: `0`

- [ ] **Run Django check:** `python manage.py check` — no issues.

---

## Chunk 3: Doctor Panel — Ko'z Ko'rigi & Vipiska Inline Cards

### Task 4: Replace A4 overlay with collapsible inline card + edit mode in patient_detail.html

**Files:**
- Modify: `templates/doctor/patient_detail.html` — the `<!-- EYE EXAM & DISCHARGE FORM HISTORY -->` section (lines ~216–385)

**Behaviour:**
- Card header: click → expand/collapse content inline (no full-screen overlay)
- Expanded content: clean 2-column view of all fields, no A4 borders
- "Tahrirlash" button at bottom of expanded view → switches same card to edit mode (form inputs)
- "Saqlash" submits to `doctor_edit_eye_exam` / `doctor_edit_discharge` (existing URLs, already work)
- "Bekor qilish" in edit mode switches back to view mode
- NO print button for doctors

- [ ] **Find and replace** the entire `<!-- EYE EXAM & DISCHARGE FORM HISTORY -->` block in `patient_detail.html` (from `{% if eye_exam_forms or discharge_forms %}` down to the closing `{% endif %}`) with the new implementation below.

Add CSS to the `<style>` block at the top (after existing `.form-history-header` styles):
```css
/* Inline form card expanded styles */
.form-card-body { display:none; padding:14px 16px; border-top:1px solid var(--border); }
.form-card-body.open { display:block; }
.form-card-view { font-size:12px; line-height:1.6; }
.form-card-view .fv-section { font-size:10px; font-weight:700; text-transform:uppercase; color:var(--text-muted); letter-spacing:0.5px; margin:10px 0 4px; border-bottom:1px solid var(--border); padding-bottom:2px; }
.form-card-view .fv-grid { display:grid; grid-template-columns:1fr 1fr; gap:4px 16px; }
.form-card-view .fv-row { margin-bottom:3px; }
.form-card-view .fv-lbl { font-size:10px; color:var(--text-muted); font-weight:600; }
.form-card-view .fv-val { font-size:12px; }
.form-card-edit { display:none; }
.form-card-edit.active { display:block; }
.form-card-edit .form-group { margin-bottom:8px; }
.form-card-edit label { font-size:11px; color:var(--text-muted); font-weight:600; display:block; margin-bottom:2px; }
.form-card-edit input, .form-card-edit textarea { width:100%; padding:5px 8px; border:1px solid var(--border); border-radius:4px; font-size:12px; background:var(--input-bg,#fff); }
.form-card-edit textarea { resize:vertical; rows:2; }
.form-card-actions { display:flex; gap:8px; margin-top:10px; padding-top:8px; border-top:1px solid var(--border); }
```

Replace the form history section with:
```html
{% if eye_exam_forms or discharge_forms %}
<div class="card animate-in" style="margin-top:16px;">
    <div class="card-header"><h3>Tibbiy hujjatlar</h3></div>

    {% for exam in eye_exam_forms %}
    <div class="form-history-card">
        <div class="form-history-header" onclick="toggleFormCard('examCard{{ exam.pk }}')">
            <div>
                <span class="form-type-badge eye-exam">Ko'z ko'rigi</span>
                <span style="margin-left:8px;font-size:12px;color:var(--text-muted);">#{{ exam.protocol_number }} &middot; {{ exam.created_at|date:"d.m.Y" }}</span>
            </div>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 9l6 6 6-6"/></svg>
        </div>
        <div class="form-card-body" id="examCard{{ exam.pk }}">
            <!-- VIEW MODE -->
            <div class="form-card-view" id="examView{{ exam.pk }}">
                <div class="fv-section">Bemor ma'lumotlari</div>
                <div class="fv-grid">
                    <div class="fv-row"><div class="fv-lbl">Protokol</div><div class="fv-val">{{ exam.protocol_number }}</div></div>
                    <div class="fv-row"><div class="fv-lbl">Sana</div><div class="fv-val">{{ exam.created_at|date:"d.m.Y H:i" }}</div></div>
                    <div class="fv-row"><div class="fv-lbl">Shifokor</div><div class="fv-val">{% if exam.doctor %}{{ exam.doctor.full_name }}{% else %}—{% endif %}</div></div>
                    <div class="fv-row"><div class="fv-lbl">Filial</div><div class="fv-val">{{ exam.filial|default:"Optimed" }}</div></div>
                </div>
                {% if exam.koz_anamezi %}<div class="fv-section">Ko'z anamnezi</div><div class="fv-row">{{ exam.koz_anamezi }}</div>{% endif %}
                <div class="fv-section">Рефракция</div>
                <div style="overflow-x:auto;">
                    <table style="width:100%;border-collapse:collapse;font-size:11px;">
                        <tr style="background:var(--bg)"><th style="border:1px solid var(--border);padding:3px 6px;"></th><th colspan="3" style="border:1px solid var(--border);padding:3px 6px;">Рефракция</th><th colspan="3" style="border:1px solid var(--border);padding:3px 6px;">Суб. рефракция</th><th colspan="3" style="border:1px solid var(--border);padding:3px 6px;">Циклопл. рефракция</th></tr>
                        <tr><td style="border:1px solid var(--border);padding:3px 6px;font-weight:600;">O'NG</td><td style="border:1px solid var(--border);padding:3px 6px;">{{ exam.ref_ong_sph }}</td><td style="border:1px solid var(--border);padding:3px 6px;">{{ exam.ref_ong_cyl }}</td><td style="border:1px solid var(--border);padding:3px 6px;">{{ exam.ref_ong_axis }}</td><td style="border:1px solid var(--border);padding:3px 6px;">{{ exam.sub_ref_ong_sph }}</td><td style="border:1px solid var(--border);padding:3px 6px;">{{ exam.sub_ref_ong_cyl }}</td><td style="border:1px solid var(--border);padding:3px 6px;">{{ exam.sub_ref_ong_axis }}</td><td style="border:1px solid var(--border);padding:3px 6px;">{{ exam.sik_ref_ong_sph }}</td><td style="border:1px solid var(--border);padding:3px 6px;">{{ exam.sik_ref_ong_cyl }}</td><td style="border:1px solid var(--border);padding:3px 6px;">{{ exam.sik_ref_ong_axis }}</td></tr>
                        <tr><td style="border:1px solid var(--border);padding:3px 6px;font-weight:600;">CHAP</td><td style="border:1px solid var(--border);padding:3px 6px;">{{ exam.ref_chap_sph }}</td><td style="border:1px solid var(--border);padding:3px 6px;">{{ exam.ref_chap_cyl }}</td><td style="border:1px solid var(--border);padding:3px 6px;">{{ exam.ref_chap_axis }}</td><td style="border:1px solid var(--border);padding:3px 6px;">{{ exam.sub_ref_chap_sph }}</td><td style="border:1px solid var(--border);padding:3px 6px;">{{ exam.sub_ref_chap_cyl }}</td><td style="border:1px solid var(--border);padding:3px 6px;">{{ exam.sub_ref_chap_axis }}</td><td style="border:1px solid var(--border);padding:3px 6px;">{{ exam.sik_ref_chap_sph }}</td><td style="border:1px solid var(--border);padding:3px 6px;">{{ exam.sik_ref_chap_cyl }}</td><td style="border:1px solid var(--border);padding:3px 6px;">{{ exam.sik_ref_chap_axis }}</td></tr>
                    </table>
                </div>
                <div class="fv-section">Ko'rish o'tkirligi va Ko'z tekshiruvi</div>
                <div class="fv-grid">
                    <div class="fv-row"><div class="fv-lbl">Tuzatilmagan (OD)</div><div class="fv-val">{{ exam.tuzatilmagan_korish_ong|default:"—" }}</div></div>
                    <div class="fv-row"><div class="fv-lbl">Tuzatilmagan (OS)</div><div class="fv-val">{{ exam.tuzatilmagan_korish_chap|default:"—" }}</div></div>
                    <div class="fv-row"><div class="fv-lbl">Tuzatilgan (OD)</div><div class="fv-val">{{ exam.tuzatilgan_korish_ong|default:"—" }}</div></div>
                    <div class="fv-row"><div class="fv-lbl">Tuzatilgan (OS)</div><div class="fv-val">{{ exam.tuzatilgan_korish_chap|default:"—" }}</div></div>
                    <div class="fv-row"><div class="fv-lbl">Old segment (OD)</div><div class="fv-val">{{ exam.old_segment_ong|default:"—" }}</div></div>
                    <div class="fv-row"><div class="fv-lbl">Old segment (OS)</div><div class="fv-val">{{ exam.old_segment_chap|default:"—" }}</div></div>
                    <div class="fv-row"><div class="fv-lbl">Orqa segment (OD)</div><div class="fv-val">{{ exam.orqa_segment_ong|default:"—" }}</div></div>
                    <div class="fv-row"><div class="fv-lbl">Orqa segment (OS)</div><div class="fv-val">{{ exam.orqa_segment_chap|default:"—" }}</div></div>
                    <div class="fv-row"><div class="fv-lbl">Ko'z bosimi (OD)</div><div class="fv-val">{{ exam.koz_bosimi_ong|default:"—" }}</div></div>
                    <div class="fv-row"><div class="fv-lbl">Ko'z bosimi (OS)</div><div class="fv-val">{{ exam.koz_bosimi_chap|default:"—" }}</div></div>
                </div>
                {% if exam.oyku %}<div class="fv-section">Tarix / O'yku</div><div class="fv-row">{{ exam.oyku }}</div>{% endif %}
                <div class="fv-section">Retsept</div>
                <div class="fv-grid">
                    <div class="fv-row"><div class="fv-lbl">Uzoq OD: SPH/CYL/AX</div><div class="fv-val">{{ exam.uzoq_ong_sph }} / {{ exam.uzoq_ong_cyl }} / {{ exam.uzoq_ong_axis }}</div></div>
                    <div class="fv-row"><div class="fv-lbl">Uzoq OS: SPH/CYL/AX</div><div class="fv-val">{{ exam.uzoq_chap_sph }} / {{ exam.uzoq_chap_cyl }} / {{ exam.uzoq_chap_axis }}</div></div>
                    <div class="fv-row"><div class="fv-lbl">Yaqin OD: SPH/CYL/AX</div><div class="fv-val">{{ exam.yaqin_ong_sph }} / {{ exam.yaqin_ong_cyl }} / {{ exam.yaqin_ong_axis }}</div></div>
                    <div class="fv-row"><div class="fv-lbl">Yaqin OS: SPH/CYL/AX</div><div class="fv-val">{{ exam.yaqin_chap_sph }} / {{ exam.yaqin_chap_cyl }} / {{ exam.yaqin_chap_axis }}</div></div>
                </div>
                <div class="fv-section">Kontakt linza</div>
                <div class="fv-grid">
                    <div class="fv-row"><div class="fv-lbl">Linza OD / OS</div><div class="fv-val">{{ exam.linza_ong|default:"—" }} / {{ exam.linza_chap|default:"—" }}</div></div>
                    <div class="fv-row"><div class="fv-lbl">Diametr OD / OS</div><div class="fv-val">{{ exam.diametr_ong|default:"—" }} / {{ exam.diametr_chap|default:"—" }}</div></div>
                    <div class="fv-row"><div class="fv-lbl">Radius OD / OS</div><div class="fv-val">{{ exam.radius_ong|default:"—" }} / {{ exam.radius_chap|default:"—" }}</div></div>
                    <div class="fv-row"><div class="fv-lbl">Dioptriya OD / OS</div><div class="fv-val">{{ exam.dioptriya_ong|default:"—" }} / {{ exam.dioptriya_chap|default:"—" }}</div></div>
                </div>
                {% if exam.icd_kodi or exam.icd_nomi %}
                <div class="fv-section">Tashxis</div>
                <div class="fv-grid">
                    <div class="fv-row"><div class="fv-lbl">ICD kodi</div><div class="fv-val">{{ exam.icd_kodi|default:"—" }}</div></div>
                    <div class="fv-row"><div class="fv-lbl">ICD nomi</div><div class="fv-val">{{ exam.icd_nomi|default:"—" }}</div></div>
                    <div class="fv-row"><div class="fv-lbl">Tashxis turi</div><div class="fv-val">{{ exam.tashxis_turi|default:"—" }}</div></div>
                    <div class="fv-row"><div class="fv-lbl">Yo'nalish</div><div class="fv-val">{{ exam.yonalish|default:"—" }}</div></div>
                </div>
                {% endif %}
                <div class="form-card-actions">
                    <button class="btn btn-secondary btn-sm" onclick="switchToExamEdit({{ exam.pk }})">Tahrirlash</button>
                </div>
            </div>
            <!-- EDIT MODE -->
            <div class="form-card-edit" id="examEdit{{ exam.pk }}">
                <form method="post" action="{% url 'doctor_edit_eye_exam' doctor.pk exam.pk %}">
                    {% csrf_token %}
                    <div class="fv-section">Ko'z anamnezi</div>
                    <div class="form-group"><textarea name="koz_anamezi" class="form-control" rows="2">{{ exam.koz_anamezi }}</textarea></div>
                    <div class="fv-section">Рефракция (OD — O'ng)</div>
                    <div style="display:grid;grid-template-columns:repeat(6,1fr);gap:6px;">
                        <div><label>REF SPH</label><input type="text" name="ref_ong_sph" value="{{ exam.ref_ong_sph }}"></div>
                        <div><label>REF CYL</label><input type="text" name="ref_ong_cyl" value="{{ exam.ref_ong_cyl }}"></div>
                        <div><label>REF AXIS</label><input type="text" name="ref_ong_axis" value="{{ exam.ref_ong_axis }}"></div>
                        <div><label>SUB SPH</label><input type="text" name="sub_ref_ong_sph" value="{{ exam.sub_ref_ong_sph }}"></div>
                        <div><label>SUB CYL</label><input type="text" name="sub_ref_ong_cyl" value="{{ exam.sub_ref_ong_cyl }}"></div>
                        <div><label>SUB AXIS</label><input type="text" name="sub_ref_ong_axis" value="{{ exam.sub_ref_ong_axis }}"></div>
                        <div><label>SIK SPH</label><input type="text" name="sik_ref_ong_sph" value="{{ exam.sik_ref_ong_sph }}"></div>
                        <div><label>SIK CYL</label><input type="text" name="sik_ref_ong_cyl" value="{{ exam.sik_ref_ong_cyl }}"></div>
                        <div><label>SIK AXIS</label><input type="text" name="sik_ref_ong_axis" value="{{ exam.sik_ref_ong_axis }}"></div>
                    </div>
                    <div class="fv-section">Рефракция (OS — Chap)</div>
                    <div style="display:grid;grid-template-columns:repeat(6,1fr);gap:6px;">
                        <div><label>REF SPH</label><input type="text" name="ref_chap_sph" value="{{ exam.ref_chap_sph }}"></div>
                        <div><label>REF CYL</label><input type="text" name="ref_chap_cyl" value="{{ exam.ref_chap_cyl }}"></div>
                        <div><label>REF AXIS</label><input type="text" name="ref_chap_axis" value="{{ exam.ref_chap_axis }}"></div>
                        <div><label>SUB SPH</label><input type="text" name="sub_ref_chap_sph" value="{{ exam.sub_ref_chap_sph }}"></div>
                        <div><label>SUB CYL</label><input type="text" name="sub_ref_chap_cyl" value="{{ exam.sub_ref_chap_cyl }}"></div>
                        <div><label>SUB AXIS</label><input type="text" name="sub_ref_chap_axis" value="{{ exam.sub_ref_chap_axis }}"></div>
                        <div><label>SIK SPH</label><input type="text" name="sik_ref_chap_sph" value="{{ exam.sik_ref_chap_sph }}"></div>
                        <div><label>SIK CYL</label><input type="text" name="sik_ref_chap_cyl" value="{{ exam.sik_ref_chap_cyl }}"></div>
                        <div><label>SIK AXIS</label><input type="text" name="sik_ref_chap_axis" value="{{ exam.sik_ref_chap_axis }}"></div>
                    </div>
                    <div class="fv-section">Ko'rish o'tkirligi</div>
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;">
                        <div><label>Tuzatilmagan OD</label><input type="text" name="tuzatilmagan_korish_ong" value="{{ exam.tuzatilmagan_korish_ong }}"></div>
                        <div><label>Tuzatilmagan OS</label><input type="text" name="tuzatilmagan_korish_chap" value="{{ exam.tuzatilmagan_korish_chap }}"></div>
                        <div><label>Tuzatilgan OD</label><input type="text" name="tuzatilgan_korish_ong" value="{{ exam.tuzatilgan_korish_ong }}"></div>
                        <div><label>Tuzatilgan OS</label><input type="text" name="tuzatilgan_korish_chap" value="{{ exam.tuzatilgan_korish_chap }}"></div>
                    </div>
                    <div class="fv-section">Ko'z tekshiruvi</div>
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;">
                        <div><label>Old segment OD</label><input type="text" name="old_segment_ong" value="{{ exam.old_segment_ong }}"></div>
                        <div><label>Old segment OS</label><input type="text" name="old_segment_chap" value="{{ exam.old_segment_chap }}"></div>
                        <div><label>Orqa segment OD</label><input type="text" name="orqa_segment_ong" value="{{ exam.orqa_segment_ong }}"></div>
                        <div><label>Orqa segment OS</label><input type="text" name="orqa_segment_chap" value="{{ exam.orqa_segment_chap }}"></div>
                        <div><label>Ko'z bosimi OD</label><input type="text" name="koz_bosimi_ong" value="{{ exam.koz_bosimi_ong }}"></div>
                        <div><label>Ko'z bosimi OS</label><input type="text" name="koz_bosimi_chap" value="{{ exam.koz_bosimi_chap }}"></div>
                    </div>
                    <div class="fv-section">Tarix / O'yku</div>
                    <div class="form-group"><textarea name="oyku" class="form-control" rows="2">{{ exam.oyku }}</textarea></div>
                    <div class="fv-section">Retsept — Uzoq</div>
                    <div style="display:grid;grid-template-columns:repeat(6,1fr);gap:6px;">
                        <div><label>OD SPH</label><input type="text" name="uzoq_ong_sph" value="{{ exam.uzoq_ong_sph }}"></div>
                        <div><label>OD CYL</label><input type="text" name="uzoq_ong_cyl" value="{{ exam.uzoq_ong_cyl }}"></div>
                        <div><label>OD AXIS</label><input type="text" name="uzoq_ong_axis" value="{{ exam.uzoq_ong_axis }}"></div>
                        <div><label>OS SPH</label><input type="text" name="uzoq_chap_sph" value="{{ exam.uzoq_chap_sph }}"></div>
                        <div><label>OS CYL</label><input type="text" name="uzoq_chap_cyl" value="{{ exam.uzoq_chap_cyl }}"></div>
                        <div><label>OS AXIS</label><input type="text" name="uzoq_chap_axis" value="{{ exam.uzoq_chap_axis }}"></div>
                    </div>
                    <div class="fv-section">Retsept — Yaqin</div>
                    <div style="display:grid;grid-template-columns:repeat(6,1fr);gap:6px;">
                        <div><label>OD SPH</label><input type="text" name="yaqin_ong_sph" value="{{ exam.yaqin_ong_sph }}"></div>
                        <div><label>OD CYL</label><input type="text" name="yaqin_ong_cyl" value="{{ exam.yaqin_ong_cyl }}"></div>
                        <div><label>OD AXIS</label><input type="text" name="yaqin_ong_axis" value="{{ exam.yaqin_ong_axis }}"></div>
                        <div><label>OS SPH</label><input type="text" name="yaqin_chap_sph" value="{{ exam.yaqin_chap_sph }}"></div>
                        <div><label>OS CYL</label><input type="text" name="yaqin_chap_cyl" value="{{ exam.yaqin_chap_cyl }}"></div>
                        <div><label>OS AXIS</label><input type="text" name="yaqin_chap_axis" value="{{ exam.yaqin_chap_axis }}"></div>
                    </div>
                    <div class="fv-section">Kontakt linza</div>
                    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:6px;">
                        <div><label>Linza OD</label><input type="text" name="linza_ong" value="{{ exam.linza_ong }}"></div>
                        <div><label>Linza OS</label><input type="text" name="linza_chap" value="{{ exam.linza_chap }}"></div>
                        <div><label>Diametr OD</label><input type="text" name="diametr_ong" value="{{ exam.diametr_ong }}"></div>
                        <div><label>Diametr OS</label><input type="text" name="diametr_chap" value="{{ exam.diametr_chap }}"></div>
                        <div><label>Radius OD</label><input type="text" name="radius_ong" value="{{ exam.radius_ong }}"></div>
                        <div><label>Radius OS</label><input type="text" name="radius_chap" value="{{ exam.radius_chap }}"></div>
                        <div><label>Dioptriya OD</label><input type="text" name="dioptriya_ong" value="{{ exam.dioptriya_ong }}"></div>
                        <div><label>Dioptriya OS</label><input type="text" name="dioptriya_chap" value="{{ exam.dioptriya_chap }}"></div>
                    </div>
                    <div class="fv-section">Tashxis</div>
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;">
                        <div><label>ICD kodi</label><input type="text" name="icd_kodi" value="{{ exam.icd_kodi }}"></div>
                        <div><label>ICD nomi</label><input type="text" name="icd_nomi" value="{{ exam.icd_nomi }}"></div>
                        <div><label>Tashxis turi</label><input type="text" name="tashxis_turi" value="{{ exam.tashxis_turi }}"></div>
                        <div><label>Yo'nalish</label><input type="text" name="yonalish" value="{{ exam.yonalish }}"></div>
                    </div>
                    <div class="form-card-actions">
                        <button type="button" class="btn btn-secondary btn-sm" onclick="switchToExamView({{ exam.pk }})">Bekor qilish</button>
                        <button type="submit" class="btn btn-primary btn-sm">Saqlash</button>
                    </div>
                </form>
            </div>
        </div>
    </div>
    {% endfor %}

    {% for disc in discharge_forms %}
    <div class="form-history-card">
        <div class="form-history-header" onclick="toggleFormCard('discCard{{ disc.pk }}')">
            <div>
                <span class="form-type-badge discharge">Vipiska</span>
                <span style="margin-left:8px;font-size:12px;color:var(--text-muted);">#{{ disc.protocol_number }} &middot; {{ disc.created_at|date:"d.m.Y" }}</span>
            </div>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 9l6 6 6-6"/></svg>
        </div>
        <div class="form-card-body" id="discCard{{ disc.pk }}">
            <!-- VIEW MODE -->
            <div class="form-card-view" id="discView{{ disc.pk }}">
                <div class="fv-section">Bemor ma'lumotlari</div>
                <div class="fv-grid">
                    <div class="fv-row"><div class="fv-lbl">Protokol</div><div class="fv-val">{{ disc.protocol_number }}</div></div>
                    <div class="fv-row"><div class="fv-lbl">Sana</div><div class="fv-val">{{ disc.created_at|date:"d.m.Y H:i" }}</div></div>
                    <div class="fv-row"><div class="fv-lbl">Yotish sanasi</div><div class="fv-val">{{ disc.yotish_sanasi|date:"d.m.Y"|default:"—" }}</div></div>
                    <div class="fv-row"><div class="fv-lbl">Chiqish sanasi</div><div class="fv-val">{{ disc.chiqish_sanasi|date:"d.m.Y"|default:"—" }}</div></div>
                </div>
                {% if disc.shikoyat_tarix %}<div class="fv-section">Шикоят / Тарих</div><div>{{ disc.shikoyat_tarix }}</div>{% endif %}
                {% if disc.shaxsiy_oilaviy_tarix %}<div class="fv-section">Шахсий/Оилавий тарих</div><div>{{ disc.shaxsiy_oilaviy_tarix }}</div>{% endif %}
                {% if disc.tizimli_anamnez %}<div class="fv-section">Тизимли анамнез</div><div>{{ disc.tizimli_anamnez }}</div>{% endif %}
                {% if disc.koz_anamezi %}<div class="fv-section">Кўз анамнези</div><div>{{ disc.koz_anamezi }}</div>{% endif %}
                {% if disc.tashxis_kodi_nomi %}<div class="fv-section">Тащхис</div><div>{{ disc.tashxis_kodi_nomi }}</div>{% endif %}
                {% if disc.operatsiya_kodi_nomi %}<div class="fv-section">Операция</div><div>{{ disc.operatsiya_kodi_nomi }}</div>{% endif %}
                <div class="fv-section">Ko'rik natijalari</div>
                <div class="fv-grid">
                    <div class="fv-row"><div class="fv-lbl">Old segment OD</div><div class="fv-val">{{ disc.old_segment_ong|default:"—" }}</div></div>
                    <div class="fv-row"><div class="fv-lbl">Old segment OS</div><div class="fv-val">{{ disc.old_segment_chap|default:"—" }}</div></div>
                    <div class="fv-row"><div class="fv-lbl">Fundus OD</div><div class="fv-val">{{ disc.fundus_ong|default:"—" }}</div></div>
                    <div class="fv-row"><div class="fv-lbl">Fundus OS</div><div class="fv-val">{{ disc.fundus_chap|default:"—" }}</div></div>
                    <div class="fv-row"><div class="fv-lbl">Ko'z bosimi OD</div><div class="fv-val">{{ disc.koz_bosimi_ong|default:"—" }}</div></div>
                    <div class="fv-row"><div class="fv-lbl">Ko'z bosimi OS</div><div class="fv-val">{{ disc.koz_bosimi_chap|default:"—" }}</div></div>
                    <div class="fv-row"><div class="fv-lbl">Preop OD</div><div class="fv-val">{{ disc.preop_ong|default:"—" }}</div></div>
                    <div class="fv-row"><div class="fv-lbl">Preop OS</div><div class="fv-val">{{ disc.preop_chap|default:"—" }}</div></div>
                    <div class="fv-row"><div class="fv-lbl">Postop OD</div><div class="fv-val">{{ disc.postop_ong|default:"—" }}</div></div>
                    <div class="fv-row"><div class="fv-lbl">Postop OS</div><div class="fv-val">{{ disc.postop_chap|default:"—" }}</div></div>
                </div>
                {% if disc.operatsiya_izohlar %}<div class="fv-section">Операция izohlari</div><div>{{ disc.operatsiya_izohlar }}</div>{% endif %}
                {% if disc.davolash %}<div class="fv-section">Davolash</div><div>{{ disc.davolash }}</div>{% endif %}
                <div class="form-card-actions">
                    <button class="btn btn-secondary btn-sm" onclick="switchToDiscEdit({{ disc.pk }})">Tahrirlash</button>
                </div>
            </div>
            <!-- EDIT MODE -->
            <div class="form-card-edit" id="discEdit{{ disc.pk }}">
                <form method="post" action="{% url 'doctor_edit_discharge' doctor.pk disc.pk %}">
                    {% csrf_token %}
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;">
                        <div class="form-group"><label>Yotish sanasi</label><input type="date" name="yotish_sanasi" value="{{ disc.yotish_sanasi|date:'Y-m-d'|default:'' }}"></div>
                        <div class="form-group"><label>Chiqish sanasi</label><input type="date" name="chiqish_sanasi" value="{{ disc.chiqish_sanasi|date:'Y-m-d'|default:'' }}"></div>
                    </div>
                    <div class="form-group"><label>Shikoyat / Tarix</label><textarea name="shikoyat_tarix" class="form-control" rows="2">{{ disc.shikoyat_tarix }}</textarea></div>
                    <div class="form-group"><label>Shaxsiy/Oilaviy tarix</label><textarea name="shaxsiy_oilaviy_tarix" class="form-control" rows="2">{{ disc.shaxsiy_oilaviy_tarix }}</textarea></div>
                    <div class="form-group"><label>Tizimli anamnez</label><textarea name="tizimli_anamnez" class="form-control" rows="2">{{ disc.tizimli_anamnez }}</textarea></div>
                    <div class="form-group"><label>Ko'z anamezi</label><textarea name="koz_anamezi" class="form-control" rows="2">{{ disc.koz_anamezi }}</textarea></div>
                    <div class="form-group"><label>Tashxis kodi–nomi</label><textarea name="tashxis_kodi_nomi" class="form-control" rows="2">{{ disc.tashxis_kodi_nomi }}</textarea></div>
                    <div class="form-group"><label>Operatsiya kodi–nomi</label><textarea name="operatsiya_kodi_nomi" class="form-control" rows="2">{{ disc.operatsiya_kodi_nomi }}</textarea></div>
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;">
                        <div><label>Old segment OD</label><input type="text" name="old_segment_ong" value="{{ disc.old_segment_ong }}"></div>
                        <div><label>Old segment OS</label><input type="text" name="old_segment_chap" value="{{ disc.old_segment_chap }}"></div>
                        <div><label>Fundus OD</label><input type="text" name="fundus_ong" value="{{ disc.fundus_ong }}"></div>
                        <div><label>Fundus OS</label><input type="text" name="fundus_chap" value="{{ disc.fundus_chap }}"></div>
                        <div><label>Ko'z bosimi OD</label><input type="text" name="koz_bosimi_ong" value="{{ disc.koz_bosimi_ong }}"></div>
                        <div><label>Ko'z bosimi OS</label><input type="text" name="koz_bosimi_chap" value="{{ disc.koz_bosimi_chap }}"></div>
                        <div><label>Daraja OD</label><input type="text" name="daraja_ong" value="{{ disc.daraja_ong }}"></div>
                        <div><label>Daraja OS</label><input type="text" name="daraja_chap" value="{{ disc.daraja_chap }}"></div>
                        <div><label>Qovoq OD</label><input type="text" name="qovoq_ong" value="{{ disc.qovoq_ong }}"></div>
                        <div><label>Qovoq OS</label><input type="text" name="qovoq_chap" value="{{ disc.qovoq_chap }}"></div>
                        <div><label>Glob OD</label><input type="text" name="glob_ong" value="{{ disc.glob_ong }}"></div>
                        <div><label>Glob OS</label><input type="text" name="glob_chap" value="{{ disc.glob_chap }}"></div>
                        <div><label>Preop OD</label><input type="text" name="preop_ong" value="{{ disc.preop_ong }}"></div>
                        <div><label>Preop OS</label><input type="text" name="preop_chap" value="{{ disc.preop_chap }}"></div>
                        <div><label>Postop OD</label><input type="text" name="postop_ong" value="{{ disc.postop_ong }}"></div>
                        <div><label>Postop OS</label><input type="text" name="postop_chap" value="{{ disc.postop_chap }}"></div>
                    </div>
                    <div class="form-group"><label>Muhim tekshiruv</label><textarea name="muhim_tekshiruv" class="form-control" rows="2">{{ disc.muhim_tekshiruv }}</textarea></div>
                    <div class="form-group"><label>Anesteziya turi</label><input type="text" name="anesteziya_turi" class="form-control" value="{{ disc.anesteziya_turi }}"></div>
                    <div class="form-group"><label>Anesteziya izohi</label><textarea name="anesteziya_izohi" class="form-control" rows="2">{{ disc.anesteziya_izohi }}</textarea></div>
                    <div class="form-group"><label>Operatsiya izohlari</label><textarea name="operatsiya_izohlar" class="form-control" rows="2">{{ disc.operatsiya_izohlar }}</textarea></div>
                    <div class="form-group"><label>Ishlatilgan linzalar</label><textarea name="ishlatilgan_linzalar" class="form-control" rows="2">{{ disc.ishlatilgan_linzalar }}</textarea></div>
                    <div class="form-group"><label>Chiqish holati</label><input type="text" name="chiqish_holati" class="form-control" value="{{ disc.chiqish_holati }}"></div>
                    <div class="form-group"><label>Davolash</label><textarea name="davolash" class="form-control" rows="2">{{ disc.davolash }}</textarea></div>
                    <div class="form-card-actions">
                        <button type="button" class="btn btn-secondary btn-sm" onclick="switchToDiscView({{ disc.pk }})">Bekor qilish</button>
                        <button type="submit" class="btn btn-primary btn-sm">Saqlash</button>
                    </div>
                </form>
            </div>
        </div>
    </div>
    {% endfor %}
</div>
{% endif %}
```

Add these JS functions to the `<script>` block at the bottom of `patient_detail.html`:
```javascript
function toggleFormCard(id) {
    var el = document.getElementById(id);
    el.classList.toggle('open');
}
function switchToExamEdit(pk) {
    document.getElementById('examView' + pk).style.display = 'none';
    document.getElementById('examEdit' + pk).classList.add('active');
}
function switchToExamView(pk) {
    document.getElementById('examView' + pk).style.display = '';
    document.getElementById('examEdit' + pk).classList.remove('active');
}
function switchToDiscEdit(pk) {
    document.getElementById('discView' + pk).style.display = 'none';
    document.getElementById('discEdit' + pk).classList.add('active');
}
function switchToDiscView(pk) {
    document.getElementById('discView' + pk).style.display = '';
    document.getElementById('discEdit' + pk).classList.remove('active');
}
```

Also **remove the old overlay divs** (`<div class="form-overlay" id="examOverlay...">` and `<div class="form-overlay" id="discOverlay...">`) — these are no longer needed for the doctor view. The receptionist's separate overlay system in `documents.html` is unchanged.

- [ ] **Remove the old `openFormOverlay` and `closeFormOverlay` JS functions** from the bottom script block (they were used by the old A4 overlay approach).

- [ ] **Run Django check:** `python manage.py check` — no issues.

---

## Chunk 4: Doctor Full History — Add Forms

### Task 5: Add Ko'z Ko'rigi and Vipiska to patient_full_history

**Files:**
- Modify: `clinic/views.py` — `doctor_patient_full_history` function
- Modify: `templates/doctor/patient_full_history.html`

- [ ] **Update `doctor_patient_full_history` view** to include forms. Find the return statement and add the two querysets before it:

```python
# Add before return render(...)
eye_exam_forms = patient.eye_exam_forms.select_related('doctor').all()
discharge_forms = patient.discharge_forms.select_related('doctor').all()
```

Add to the render context dict:
```python
'eye_exam_forms': eye_exam_forms,
'discharge_forms': discharge_forms,
```

- [ ] **Add the forms section to `templates/doctor/patient_full_history.html`**.

Add this CSS to the `<style>` block (or after `{% block content %}`):
```css
.fh-form-card { border:1px solid var(--border); border-radius:8px; margin-bottom:8px; background:var(--white); overflow:hidden; }
.fh-form-header { padding:10px 14px; display:flex; justify-content:space-between; align-items:center; cursor:pointer; font-size:13px; background:var(--bg); }
.fh-form-header:hover { background:var(--border); }
.fh-form-body { display:none; padding:14px 16px; border-top:1px solid var(--border); font-size:12px; line-height:1.6; }
.fh-form-body.open { display:block; }
.fh-form-grid { display:grid; grid-template-columns:1fr 1fr; gap:4px 16px; }
.fh-form-lbl { font-size:10px; color:var(--text-muted); font-weight:600; }
.fh-form-val { font-size:12px; }
.fh-form-section { font-size:10px; font-weight:700; text-transform:uppercase; color:var(--text-muted); letter-spacing:0.5px; margin:8px 0 4px; border-bottom:1px solid var(--border); padding-bottom:2px; }
```

Add this block **before** `{% endblock %}` in `patient_full_history.html`:
```html
{% if eye_exam_forms or discharge_forms %}
<div class="card animate-in" style="margin-top:20px;">
    <div class="card-header"><h3>Tibbiy hujjatlar</h3></div>
    <div style="padding:12px 16px;">

    {% for exam in eye_exam_forms %}
    <div class="fh-form-card">
        <div class="fh-form-header" onclick="this.nextElementSibling.classList.toggle('open')">
            <div>
                <span style="display:inline-block;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600;background:#e0f2fe;color:#0369a1;margin-right:8px;">Ko'z ko'rigi</span>
                #{{ exam.protocol_number }} &middot; {{ exam.created_at|date:"d.m.Y" }}
                {% if exam.doctor %}&middot; {{ exam.doctor.full_name }}{% endif %}
            </div>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 9l6 6 6-6"/></svg>
        </div>
        <div class="fh-form-body">
            <div class="fh-form-grid">
                <div><div class="fh-form-lbl">Protokol</div><div class="fh-form-val">{{ exam.protocol_number }}</div></div>
                <div><div class="fh-form-lbl">Sana</div><div class="fh-form-val">{{ exam.created_at|date:"d.m.Y H:i" }}</div></div>
            </div>
            {% if exam.koz_anamezi %}<div class="fh-form-section">Ko'z anamnezi</div><div>{{ exam.koz_anamezi }}</div>{% endif %}
            <div class="fh-form-section">Ko'rish va ko'z tekshiruvi</div>
            <div class="fh-form-grid">
                <div><div class="fh-form-lbl">Tuzatilmagan OD / OS</div><div class="fh-form-val">{{ exam.tuzatilmagan_korish_ong|default:"—" }} / {{ exam.tuzatilmagan_korish_chap|default:"—" }}</div></div>
                <div><div class="fh-form-lbl">Tuzatilgan OD / OS</div><div class="fh-form-val">{{ exam.tuzatilgan_korish_ong|default:"—" }} / {{ exam.tuzatilgan_korish_chap|default:"—" }}</div></div>
                <div><div class="fh-form-lbl">Ko'z bosimi OD / OS</div><div class="fh-form-val">{{ exam.koz_bosimi_ong|default:"—" }} / {{ exam.koz_bosimi_chap|default:"—" }}</div></div>
            </div>
            {% if exam.icd_kodi or exam.icd_nomi %}
            <div class="fh-form-section">Tashxis</div>
            <div>{{ exam.icd_kodi }} — {{ exam.icd_nomi }}</div>
            {% endif %}
            <div style="margin-top:10px;">
                <a href="{% url 'doctor_edit_eye_exam' doctor.pk exam.pk %}" class="btn btn-secondary btn-sm">Tahrirlash</a>
            </div>
        </div>
    </div>
    {% endfor %}

    {% for disc in discharge_forms %}
    <div class="fh-form-card">
        <div class="fh-form-header" onclick="this.nextElementSibling.classList.toggle('open')">
            <div>
                <span style="display:inline-block;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600;background:#fef3c7;color:#92400e;margin-right:8px;">Vipiska</span>
                #{{ disc.protocol_number }} &middot; {{ disc.created_at|date:"d.m.Y" }}
                {% if disc.doctor %}&middot; {{ disc.doctor.full_name }}{% endif %}
            </div>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 9l6 6 6-6"/></svg>
        </div>
        <div class="fh-form-body">
            <div class="fh-form-grid">
                <div><div class="fh-form-lbl">Protokol</div><div class="fh-form-val">{{ disc.protocol_number }}</div></div>
                <div><div class="fh-form-lbl">Yotish–Chiqish</div><div class="fh-form-val">{{ disc.yotish_sanasi|date:"d.m.Y"|default:"—" }} – {{ disc.chiqish_sanasi|date:"d.m.Y"|default:"—" }}</div></div>
            </div>
            {% if disc.tashxis_kodi_nomi %}<div class="fh-form-section">Tashxis</div><div>{{ disc.tashxis_kodi_nomi }}</div>{% endif %}
            {% if disc.operatsiya_kodi_nomi %}<div class="fh-form-section">Operatsiya</div><div>{{ disc.operatsiya_kodi_nomi }}</div>{% endif %}
            {% if disc.davolash %}<div class="fh-form-section">Davolash</div><div>{{ disc.davolash }}</div>{% endif %}
            <div style="margin-top:10px;">
                <a href="{% url 'doctor_edit_discharge' doctor.pk disc.pk %}" class="btn btn-secondary btn-sm">Tahrirlash</a>
            </div>
        </div>
    </div>
    {% endfor %}

    </div>
</div>
{% endif %}
```

**Note:** The edit links go to the existing `doctor_edit_eye_exam` / `doctor_edit_discharge` views, which redirect back to `doctor_patient_detail` after saving. This is acceptable — if needed later, a `?next=` param can be added.

- [ ] **Run Django check:** `python manage.py check` — no issues.

---

## Chunk 5: Optika Panel Fixes

### Task 6: GlassSale — add discount_amount field

**Files:**
- Modify: `clinic/models.py` — `GlassSale` class
- Create: `clinic/migrations/0016_glasssale_discount_amount.py`

- [ ] **Add `discount_amount` to `GlassSale` in `models.py`:**

```python
class GlassSale(models.Model):
    glasses = models.ForeignKey(Glasses, on_delete=models.CASCADE, related_name='sales')
    quantity = models.IntegerField(default=1)
    sell_price = models.IntegerField(default=0)
    cost_price = models.IntegerField(default=0)
    discount_amount = models.IntegerField(default=0)   # ← ADD THIS
    created_at = models.DateTimeField(auto_now_add=True)
    ...
    @property
    def total_revenue(self):
        return (self.sell_price - self.discount_amount) * self.quantity   # ← UPDATE

    @property
    def total_profit(self):
        return (self.sell_price - self.discount_amount - self.cost_price) * self.quantity   # ← UPDATE
```

- [ ] **Create migration:**
```bash
source venv/bin/activate
python manage.py makemigrations clinic --name glasssale_discount_amount
python manage.py migrate
```
Expected: `Applying clinic.0016_glasssale_discount_amount... OK`

---

### Task 7: Optika — login redirect + nav order

**Files:**
- Modify: `clinic/views.py` — login view (two seller redirect lines)
- Modify: `templates/base.html` — seller nav section

- [ ] **In `clinic/views.py`, find both `seller` redirect lines** and change `seller_panel` → `seller_sales`:

```python
# Line ~114: system accounts
elif acc['role'] == 'seller':
    return redirect('seller_sales')   # was seller_panel

# Line ~131: DB accounts
elif user.role == 'seller':
    return redirect('seller_sales')   # was seller_panel
```

- [ ] **In `templates/base.html`, swap nav order** for seller (Sotuvlar first):

```html
{% if request.session.user_role == 'seller' %}
<div class="nav-section">
    <div class="nav-section-title">Optika</div>
    <a href="{% url 'seller_sales' %}" class="nav-link {% block nav_seller_sales %}{% endblock %}">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 2L3 6v14a2 2 0 002 2h14a2 2 0 002-2V6l-3-4z"/><line x1="3" y1="6" x2="21" y2="6"/><path d="M16 10a4 4 0 01-8 0"/></svg>
        Sotuvlar
    </a>
    <a href="{% url 'seller_panel' %}" class="nav-link {% block nav_seller %}{% endblock %}">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="6" cy="12" r="4"/><circle cx="18" cy="12" r="4"/><line x1="10" y1="12" x2="14" y2="12"/></svg>
        Ko'zoynaklar
    </a>
    <a href="{% url 'seller_analytics' %}" class="nav-link {% block nav_seller_analytics %}{% endblock %}">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>
        Statistika
    </a>
</div>
{% endif %}
```

---

### Task 8: Sotuvlar page — full redesign

**Files:**
- Modify: `clinic/views.py` — `seller_sales` and `seller_sell_glasses` views
- Modify: `templates/seller/sales.html`

- [ ] **Update `seller_sales` view** to show inventory:

```python
@role_required('seller')
def seller_sales(request):
    glasses = Glasses.objects.filter(quantity__gt=0).order_by('model_name')
    return render(request, 'seller/sales.html', {'glasses': glasses})
```

- [ ] **Update `seller_sell_glasses` view** to handle discount and sell 1 unit:

```python
@role_required('seller')
def seller_sell_glasses(request):
    if request.method == 'POST':
        glasses_id = request.POST.get('glasses_id')
        discount = int(request.POST.get('discount_amount', 0) or 0)
        g = get_object_or_404(Glasses, pk=glasses_id)
        if g.quantity < 1:
            return redirect('seller_sales')
        GlassSale.objects.create(
            glasses=g,
            quantity=1,
            sell_price=g.sell_price,
            cost_price=g.cost_price,
            discount_amount=discount,
        )
        g.quantity -= 1
        g.save(update_fields=['quantity'])
    return redirect('seller_sales')
```

- [ ] **Rewrite `templates/seller/sales.html`** completely:

```html
{% extends 'base.html' %}
{% load clinic_filters %}
{% block title %}Sotuvlar — Optimed CRM{% endblock %}
{% block nav_seller_sales %}active{% endblock %}

{% block content %}
<div class="page-header">
    <div>
        <h1>Sotuvlar</h1>
        <p>Mavjud ko'zoynaklar</p>
    </div>
</div>

<!-- SEARCH BAR -->
<div style="margin-bottom:16px;">
    <input type="text" id="glassSearch" class="form-control" placeholder="Model yoki brend bo'yicha qidirish..."
           oninput="filterGlasses(this.value)" style="max-width:400px;">
</div>

{% if messages %}
{% for msg in messages %}
<div style="background:var(--danger);color:#fff;padding:12px 20px;border-radius:8px;margin-bottom:16px;font-size:14px;">{{ msg }}</div>
{% endfor %}
{% endif %}

<div class="card animate-in">
    <div class="table-wrapper">
        <table id="glassTable">
            <thead>
                <tr>
                    <th>Model</th>
                    <th>Brend</th>
                    <th>Linza turi</th>
                    <th>Narx</th>
                    <th>Miqdori</th>
                    <th></th>
                </tr>
            </thead>
            <tbody>
                {% for g in glasses %}
                <tr data-search="{{ g.model_name|lower }} {{ g.brand|lower }}">
                    <td><strong>{{ g.model_name }}</strong></td>
                    <td style="color:var(--text-muted);">{{ g.brand|default:"—" }}</td>
                    <td style="color:var(--text-muted);">{{ g.lens_type|default:"—" }}</td>
                    <td><strong>{{ g.sell_price|format_som }} so'm</strong></td>
                    <td>
                        {% if g.quantity <= 3 %}
                            <span class="badge badge-warning">{{ g.quantity }}</span>
                        {% else %}
                            <span class="badge badge-success">{{ g.quantity }}</span>
                        {% endif %}
                    </td>
                    <td>
                        <button class="btn btn-primary btn-sm"
                                onclick="openSellModal({{ g.pk }}, '{{ g.model_name|escapejs }}', {{ g.sell_price }})">
                            Sotish
                        </button>
                    </td>
                </tr>
                {% empty %}
                <tr><td colspan="6" class="empty-state"><p>Sotish uchun ko'zoynaklar mavjud emas</p></td></tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>

<!-- SELL MODAL -->
<div class="modal-backdrop" id="sellModal">
    <div class="modal" style="max-width:400px;">
        <h3>Ko'zoynak sotish</h3>
        <form method="post" action="{% url 'seller_sell_glasses' %}" id="sellForm">
            {% csrf_token %}
            <input type="hidden" name="glasses_id" id="sellGlassesId">
            <div class="form-group">
                <label style="font-size:12px;color:var(--text-muted);">Mahsulot</label>
                <div id="sellGlassesName" style="font-weight:600;font-size:15px;margin-bottom:4px;"></div>
            </div>
            <div class="form-group">
                <label>Narx</label>
                <div id="sellPrice" style="font-size:14px;color:var(--text-muted);"></div>
            </div>
            <div class="form-group">
                <label>Chegirma (so'm)</label>
                <input type="number" name="discount_amount" id="sellDiscount" class="form-control"
                       min="0" value="0" oninput="updateFinalPrice()">
            </div>
            <div class="form-group">
                <label>Yakuniy narx</label>
                <div id="sellFinalPrice" style="font-size:16px;font-weight:700;color:var(--accent);"></div>
            </div>
            <div class="modal-actions">
                <button type="button" class="btn btn-secondary" onclick="closeModal('sellModal')">Bekor qilish</button>
                <button type="submit" class="btn btn-success">Sotish</button>
            </div>
        </form>
    </div>
</div>

<script>
var currentSellPrice = 0;

function openSellModal(pk, name, price) {
    currentSellPrice = price;
    document.getElementById('sellGlassesId').value = pk;
    document.getElementById('sellGlassesName').textContent = name;
    document.getElementById('sellDiscount').value = 0;
    var priceStr = price.toLocaleString('ru-RU') + " so'm";
    document.getElementById('sellPrice').textContent = priceStr;
    document.getElementById('sellFinalPrice').textContent = priceStr;
    openModal('sellModal');
}

function updateFinalPrice() {
    var discount = parseInt(document.getElementById('sellDiscount').value || 0);
    var final = Math.max(0, currentSellPrice - discount);
    document.getElementById('sellFinalPrice').textContent = final.toLocaleString('ru-RU') + " so'm";
}

function filterGlasses(q) {
    q = q.toLowerCase();
    document.querySelectorAll('#glassTable tbody tr[data-search]').forEach(function(row) {
        row.style.display = row.dataset.search.includes(q) ? '' : 'none';
    });
}

function openModal(id) { document.getElementById(id).classList.add('active'); }
function closeModal(id) { document.getElementById(id).classList.remove('active'); }

document.querySelectorAll('.modal-backdrop').forEach(function(m) {
    m.addEventListener('click', function(e) { if (e.target === m) m.classList.remove('active'); });
});
</script>
{% endblock %}
```

- [ ] **Run Django check:** `python manage.py check` — no issues.

---

## Final Verification

- [ ] **Start the server:**
```bash
cd /Users/iskandarodilov/Desktop/CRM
source venv/bin/activate
python manage.py runserver 8000
```

- [ ] **Test each fix manually:**
  1. Lab search — receptionist panel, add patient to lab, type in search fields, verify combined search works
  2. Hujjatlar — open receptionist Hujjatlar page without searching, verify recent docs appear
  3. Doctor Cyrillic — open any Ko'z ko'rigi or Vipiska form, confirm Russian text shows in Cyrillic
  4. Doctor inline card — click Ko'z ko'rigi card header, expand, press Tahrirlash, edit a field, save
  5. Full history — open a patient's full history as doctor, verify Tibbiy hujjatlar section appears
  6. Seller login — log in as optika/123, verify Sotuvlar page opens (not Ko'zoynaklar)
  7. Sotuvlar — verify only in-stock glasses shown, search by brand works, Sotish modal shows discount field, selling decrements quantity
