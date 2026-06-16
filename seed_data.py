import os
import sys
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_project.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.utils import timezone
from datetime import timedelta, datetime as dt_cls
from clinic.models import (
    Service, Worker, Patient, Visit, Procedure, ProcedureDate,
    UserAccount, VisitService, QueueNumber, ScheduledVisit,
    ClinicalProcedure, Expense, VisitAttachment, ReferralPartner,
    Glasses, GlassSale, EyeRefraction, EyeKRT, EyeIOP,
    LabVisit, LabVisitService,
    get_next_queue_number,
)

# Clear existing data
LabVisitService.objects.all().delete()
LabVisit.objects.all().delete()
EyeRefraction.objects.all().delete()
EyeKRT.objects.all().delete()
EyeIOP.objects.all().delete()
GlassSale.objects.all().delete()
Glasses.objects.all().delete()
QueueNumber.objects.all().delete()
ScheduledVisit.objects.all().delete()
VisitService.objects.all().delete()
ProcedureDate.objects.all().delete()
Procedure.objects.all().delete()
Visit.objects.all().delete()
Patient.objects.all().delete()
UserAccount.objects.all().delete()
Worker.objects.all().delete()
Service.objects.all().delete()
ClinicalProcedure.objects.all().delete()
Expense.objects.all().delete()
ReferralPartner.objects.all().delete()

print("Xizmatlar yaratilmoqda...")
s1 = Service.objects.create(
    name="Ko'z tekshiruvi",
    description="Ko'z salomatligi bo'yicha to'liq tekshiruv: ko'rish o'tkirligi, ko'z ichki bosimi va to'r parda tekshiruvi",
    price=200000,
)
s2 = Service.objects.create(
    name="Katarakta operatsiyasi",
    description="Ko'z gavharini sun'iy linza bilan almashtirish operatsiyasi",
    price=5000000,
)
s3 = Service.objects.create(
    name="LASIK operatsiyasi",
    description="Lazer yordamida ko'rishni tiklash operatsiyasi",
    price=7000000,
)
s4 = Service.objects.create(
    name="Glaukoma davolash",
    description="Glaukoma tashxisi va davolash rejasi, dori-darmonlar va monitoring",
    price=800000,
)
s5 = Service.objects.create(
    name="Retina konsultatsiyasi",
    description="To'r parda tekshiruvi va tashxisi, makula degeneratsiyasi kabi kasalliklar uchun",
    price=500000,
)
s6 = Service.objects.create(
    name="Bolalar oftalmologiyasi",
    description="Bolalar uchun ko'z tekshiruvi va davolash",
    price=300000,
)

services_list = [s1, s2, s3, s4, s5, s6]

print("Doktorlar yaratilmoqda...")
d1 = Worker.objects.create(
    name="Aziz", surname="Kamolov",
    phone="901000002", salary=15000000,
    worker_type="doctor", service=s1,
    description="Bosh shifokor - umumiy oftalmolog",
    room_number="1",
)
d2 = Worker.objects.create(
    name="Jamshid", surname="Rahimov",
    phone="901000003", salary=18000000,
    worker_type="doctor", service=s2,
    description="Katarakta bo'yicha mutaxassis jarroh",
    room_number="2",
)
d3 = Worker.objects.create(
    name="Dilnoza", surname="Toshmatova",
    phone="901000004", salary=20000000,
    worker_type="doctor", service=s3,
    description="LASIK va refraktiv jarrohlik mutaxassisi",
    room_number="3",
)
d4 = Worker.objects.create(
    name="Sardor", surname="Mirzayev",
    phone="901000005", salary=14000000,
    worker_type="doctor", service=s4,
    description="Glaukoma bo'yicha mutaxassis",
    room_number="4",
)
d5 = Worker.objects.create(
    name="Nodira", surname="Abdullayeva",
    phone="901000006", salary=13000000,
    worker_type="doctor", service=s5,
    description="Retina va vitreoretinal kasalliklar mutaxassisi",
    room_number="5",
)

doctors_list = [d1, d2, d3, d4, d5]

# Set M2M services for doctors
d1.services.set([s1, s6])  # Ko'z tekshiruvi + Bolalar oftalmologiyasi
d2.services.set([s2])       # Katarakta operatsiyasi
d3.services.set([s3])       # LASIK operatsiyasi
d4.services.set([s4, s5])   # Glaukoma davolash + Retina konsultatsiyasi
d5.services.set([s5])       # Retina konsultatsiyasi

print("Foydalanuvchi akkauntlari yaratilmoqda...")
UserAccount.objects.create(name="Iskandar", surname="Odilov", phone="901000001", role="admin")
UserAccount.objects.create(name="Aziz", surname="Kamolov", phone="901000002", role="doctor", worker=d1)
UserAccount.objects.create(name="Jamshid", surname="Rahimov", phone="901000003", role="doctor", worker=d2)
UserAccount.objects.create(name="Dilnoza", surname="Toshmatova", phone="901000004", role="doctor", worker=d3)
UserAccount.objects.create(name="Sardor", surname="Mirzayev", phone="901000005", role="doctor", worker=d4)
UserAccount.objects.create(name="Nodira", surname="Abdullayeva", phone="901000006", role="doctor", worker=d5)
UserAccount.objects.create(name="Reception", surname="", phone="1234", role="receptionist")

print("Xarajatlar yaratilmoqda...")
Expense.objects.create(name="Ijara", amount=10000000, expense_type="recurring")
Expense.objects.create(name="Elektr energiyasi", amount=2000000, expense_type="recurring")
Expense.objects.create(name="Suv", amount=500000, expense_type="recurring")
Expense.objects.create(name="Internet va telefon", amount=1000000, expense_type="recurring")
Expense.objects.create(name="Tibbiy jihozlar ta'miri", amount=5000000, expense_type="one_time",
                        date=timezone.now().date() - timedelta(days=30))
Expense.objects.create(name="Yangi ko'z tekshiruv apparati", amount=25000000, expense_type="one_time",
                        date=timezone.now().date() - timedelta(days=60))
Expense.objects.create(name="Ofis ta'miri", amount=8000000, expense_type="one_time",
                        date=timezone.now().date() - timedelta(days=90))

print("Yo'naltiruvchi hamkorlar yaratilmoqda...")
rp1 = ReferralPartner.objects.create(
    name="Alisher", surname="Xolmatov",
    phone="901234001", clinic_name="Noor klinikasi",
    commission_percent=10, notes="Asosiy hamkor, ko'p bemor yo'naltiradi",
)
rp2 = ReferralPartner.objects.create(
    name="Mavluda", surname="Sobirova",
    phone="901234002", clinic_name="Salomatlik markazi",
    commission_percent=15, notes="Oftalmologiya bo'yicha hamkor",
)
rp3 = ReferralPartner.objects.create(
    name="Farhod", surname="Tursunov",
    phone="901234003", clinic_name="",
    commission_percent=8, notes="Mustaqil doktor, oilaviy shifoxona",
)
rp4 = ReferralPartner.objects.create(
    name="Nigora", surname="Karimova",
    phone="901234004", clinic_name="City Med",
    commission_percent=12, is_active=False, notes="Vaqtincha to'xtatilgan hamkorlik",
)
referral_partners = [rp1, rp2, rp3, rp4]

print("Bemorlar yaratilmoqda...")
patients_data = [
    ("Amir", "Karimov", "931111101"),
    ("Fatima", "Rashidova", "931111102"),
    ("Rustam", "Aliyev", "931111103"),
    ("Nilufar", "Usmanova", "931111104"),
    ("Jasur", "Tursunov", "931111105"),
    ("Dilorom", "Mirzayeva", "931111106"),
    ("Bobur", "Xamidov", "931111107"),
    ("Gulnara", "Nazarova", "931111108"),
    ("Temur", "Abdullayev", "931111109"),
    ("Madina", "Raximova", "931111110"),
    ("Sardor", "Yuldashev", "931111111"),
    ("Zarina", "Ergasheva", "931111112"),
    ("Ulug'bek", "Sharipov", "931111113"),
    ("Kamola", "Ismoilova", "931111114"),
    ("Nodir", "Sultonov", "931111115"),
    ("Shahlo", "Qosimova", "931111116"),
    ("Elbek", "Tojiboyev", "931111117"),
    ("Feruza", "Holmatova", "931111118"),
    ("Oybek", "Jumayev", "931111119"),
    ("Dildora", "Saidova", "931111120"),
    ("Anvar", "Toshpulatov", "931111121"),
    ("Mohinur", "Bekmurodova", "931111122"),
    ("Shaxzod", "Ergashev", "931111123"),
    ("Ozoda", "Xudoyberdiyeva", "931111124"),
    ("Jamol", "Narzullayev", "931111125"),
    ("Barno", "Ruziyeva", "931111126"),
    ("Firdavs", "Olimov", "931111127"),
    ("Sabohat", "Tursunova", "931111128"),
    ("Dostonbek", "Xolmatov", "931111129"),
    ("Nafisa", "Qodirova", "931111130"),
    ("Mirzo", "Usmonov", "931111131"),
    ("Sevinch", "Kamalova", "931111132"),
    ("Baxtiyor", "Jurayev", "931111133"),
    ("Maftuna", "Sobirov", "931111134"),
    ("Abdulaziz", "Normatov", "931111135"),
    ("Zilola", "Yusupova", "931111136"),
    ("Otabek", "Qodirov", "931111137"),
    ("Dilrabo", "Ganiyeva", "931111138"),
    ("Sanjar", "Raxmatullayev", "931111139"),
    ("Nargiza", "Sharipova", "931111140"),
    ("Akbar", "Xalilov", "931111141"),
    ("Laylo", "Muhammadiyeva", "931111142"),
    ("Ravshan", "Tojiyev", "931111143"),
    ("Gulchiroy", "Abduraxmonova", "931111144"),
    ("Eldor", "Mamatov", "931111145"),
    ("Sitora", "Raximova", "931111146"),
    ("Shuhrat", "Yoqubov", "931111147"),
    ("Muhayo", "Turgunova", "931111148"),
    ("Ikrom", "Salimov", "931111149"),
    ("Xurshida", "Azimova", "931111150"),
    ("Umid", "Ibragimov", "931111151"),
    ("Robiya", "Haydarova", "931111152"),
    ("Bekzod", "Norbekov", "931111153"),
    ("Yulduz", "Mahmudova", "931111154"),
    ("Komil", "Fayzullayev", "931111155"),
    ("Malohat", "Samadova", "931111156"),
    ("Husan", "Rajabov", "931111157"),
    ("Nasiba", "Xoshimova", "931111158"),
    ("Furqat", "Alimov", "931111159"),
    ("Zarnigor", "Toshmatova", "931111160"),
]

patients = []
for name, surname, phone in patients_data:
    p = Patient.objects.create(name=name, surname=surname, phone=phone)
    patients.append(p)

print("Tashriflar yaratilmoqda (24 oy)...")
now = timezone.now()

random.seed(42)

discount_reasons = [
    "Keksa yoshli chegirma", "Doimiy mijoz", "Sug'urta", "Talaba chegirmasi",
    "Katta oila chegirmasi", "Yo'naltirma chegirmasi", "Chegirma", "Bayram chegirmasi",
]
problems = [
    "Bemor shikoyatlari qabul paytida qayd etildi",
    "Ko'rish o'tkirligi pasaygan",
    "Ko'z qizarishi va achishish",
    "Ko'z ichki bosimi yuqori",
    "Ko'rish xiralik bilan shikoyat",
    "Bosh og'rig'i va ko'z charchoqligi",
    "Yaqin masofadan ko'rish qiyinlashgan",
    "Uzoq masofadan ko'rish yomonlashgan",
    "To'r parda tekshiruvi kerak",
]
solutions = [
    "Davolash rejasi taqdim etildi",
    "Ko'zoynak retsepti yozildi",
    "Ko'z tomchilari buyurildi",
    "Operatsiya rejalashtirildi",
    "Nazorat tekshiruvi tayinlandi",
    "Vitaminlar va ko'z mashqlari tavsiya etildi",
    "Lazer davolash o'tkazildi",
    "Dori-darmonlar buyurildi",
]

# Generate 24 months of visits with increasing volume
visit_count = 0
for months_ago in range(23, -1, -1):
    dt_month = now - timedelta(days=months_ago * 30)
    month_start = dt_month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Increasing volume over time: 4-6 early, 8-12 middle, 12-18 recent
    if months_ago > 18:
        num_visits = random.randint(4, 7)
    elif months_ago > 12:
        num_visits = random.randint(6, 10)
    elif months_ago > 6:
        num_visits = random.randint(8, 13)
    else:
        num_visits = random.randint(10, 16)

    for _ in range(num_visits):
        patient = random.choice(patients)
        doctor = random.choice(doctors_list)
        service = doctor.service if doctor.service else random.choice(services_list)

        # Random day within the month
        day_offset = random.randint(0, 27)
        created = month_start + timedelta(days=day_offset, hours=random.randint(8, 17))

        # Don't create future visits in this loop
        if created > now:
            continue

        has_discount = random.random() < 0.2
        discount = random.choice([50000, 100000, 200000, 300000, 500000, 1000000]) if has_discount else 0
        reason = random.choice(discount_reasons) if has_discount else ''

        # Most are done/rated, recent ones may not be rated
        if months_ago > 1:
            rated = True
            dr = random.randint(5, 10)
            cr = random.randint(5, 10)
        elif months_ago == 1:
            rated = random.random() < 0.7
            dr = random.randint(5, 10) if rated else None
            cr = random.randint(5, 10) if rated else None
        else:
            rated = random.random() < 0.4
            dr = random.randint(5, 10) if rated else None
            cr = random.randint(5, 10) if rated else None

        # Random referral partner (~20% of visits)
        ref_partner = random.choice(referral_partners[:3]) if random.random() < 0.2 else None

        v = Visit.objects.create(
            patient=patient, doctor=doctor, service=service,
            doctor_name=doctor.full_name,
            referred_by=ref_partner,
            status='done', discount_amount=discount, discount_reason=reason,
            doctor_rating=dr, clinic_rating=cr, rated=rated,
            problem=random.choice(problems),
        )
        v.created_at = created
        v.completed_at = created + timedelta(hours=random.randint(1, 3))
        v.save(update_fields=['created_at', 'completed_at'])
        # Create VisitService record
        VisitService.objects.create(visit=v, service=service, price_at_time=service.price)
        # Sometimes add a second service
        if random.random() < 0.15:
            extra_svc = random.choice([s for s in services_list if s != service])
            VisitService.objects.create(visit=v, service=extra_svc, price_at_time=extra_svc.price)
        visit_count += 1

print(f"  {visit_count} ta tarix tashriflari yaratildi")

# Recent unrated done visits (for notifications)
for i in range(3):
    p = patients[i]
    d = doctors_list[i % len(doctors_list)]
    svc = d.service or s1
    v = Visit.objects.create(
        patient=p, doctor=d, service=svc,
        doctor_name=d.full_name,
        status='done', discount_amount=0, rated=False,
        problem=random.choice(problems),
    )
    v.created_at = now - timedelta(hours=random.randint(2, 48))
    v.completed_at = v.created_at + timedelta(hours=1)
    v.save(update_fields=['created_at', 'completed_at'])
    VisitService.objects.create(visit=v, service=svc, price_at_time=svc.price)

# Visits waiting for doctor (current) — with per-doctor queue numbers
print("Kutayotgan tashriflar yaratilmoqda...")
waiting_data = [
    (patients[11], d1, s1, 0, ''),
    (patients[12], d2, s2, 200000, "Yo'naltirma chegirmasi"),
    (patients[13], d3, s3, 0, ''),
    (patients[16], d5, s5, 0, ''),
    (patients[17], d1, s6, 0, ''),  # second patient for d1
]
for pat, doc, svc, disc, reason in waiting_data:
    wv = Visit.objects.create(patient=pat, doctor=doc, service=svc, status='waiting',
                              doctor_name=doc.full_name,
                              discount_amount=disc, discount_reason=reason)
    VisitService.objects.create(visit=wv, service=svc, price_at_time=svc.price)
    qnum = get_next_queue_number(doctor=doc)
    QueueNumber.objects.create(visit=wv, doctor=doc, number=qnum, date=now.date())

# Visit with procedure (has_procedure status) — no clinical_procedure FK
v_proc = Visit.objects.create(
    patient=patients[14], doctor=d4, service=s4,
    doctor_name=d4.full_name,
    status='has_procedure', discount_amount=0,
    problem="Ko'z ichki bosimi yuqori",
)
v_proc.completed_at = now - timedelta(days=2)
v_proc.save(update_fields=['completed_at'])
VisitService.objects.create(visit=v_proc, service=s4, price_at_time=s4.price)

proc1 = Procedure.objects.create(
    visit=v_proc, patient=patients[14], doctor=d4,
    description="Ko'z ichki bosimini nazorat qilish va dori-darmonni sozlash",
    total_repetitions=3,
    price_per_session=150000,
    total_price=150000 * 3,
)
ProcedureDate.objects.create(procedure=proc1, scheduled_date=(now + timedelta(days=1)).date())
ProcedureDate.objects.create(procedure=proc1, scheduled_date=(now + timedelta(days=14)).date())
ProcedureDate.objects.create(procedure=proc1, scheduled_date=(now + timedelta(days=28)).date())

# Another visit with a procedure that has some completed dates
v_proc2 = Visit.objects.create(
    patient=patients[15], doctor=d1, service=s1,
    doctor_name=d1.full_name,
    status='has_procedure', discount_amount=0,
    problem="Ko'rish pasayishi",
)
v_proc2.completed_at = now - timedelta(days=10)
v_proc2.save(update_fields=['completed_at'])
VisitService.objects.create(visit=v_proc2, service=s1, price_at_time=s1.price)

proc2 = Procedure.objects.create(
    visit=v_proc2, patient=patients[15], doctor=d1,
    description="Ko'z mashqlari va vitaminlar kursi",
    total_repetitions=4,
    price_per_session=100000,
    total_price=100000 * 4,
)
ProcedureDate.objects.create(procedure=proc2, scheduled_date=(now - timedelta(days=7)).date(), completed=True)
ProcedureDate.objects.create(procedure=proc2, scheduled_date=(now - timedelta(days=1)).date())
ProcedureDate.objects.create(procedure=proc2, scheduled_date=(now + timedelta(days=7)).date())
ProcedureDate.objects.create(procedure=proc2, scheduled_date=(now + timedelta(days=14)).date())

# A third procedure for today's badge
v_proc3 = Visit.objects.create(
    patient=patients[20], doctor=d3, service=s3,
    doctor_name=d3.full_name,
    status='has_procedure', discount_amount=0,
    problem="LASIK operatsiyadan keyin nazorat",
)
v_proc3.completed_at = now - timedelta(days=5)
v_proc3.save(update_fields=['completed_at'])
VisitService.objects.create(visit=v_proc3, service=s3, price_at_time=s3.price)

proc3 = Procedure.objects.create(
    visit=v_proc3, patient=patients[20], doctor=d3,
    description="LASIK operatsiyadan keyingi nazorat tekshiruvi",
    total_repetitions=2,
    price_per_session=200000,
    total_price=200000 * 2,
)
ProcedureDate.objects.create(procedure=proc3, scheduled_date=now.date())
ProcedureDate.objects.create(procedure=proc3, scheduled_date=(now + timedelta(days=30)).date())

# Scheduled visits (future appointments)
print("Rejalashtirilgan tashriflar yaratilmoqda...")
ScheduledVisit.objects.create(
    patient=patients[25], doctor=d1,
    scheduled_date=(now + timedelta(days=3)).date(),
    notes="Ko'z tekshiruvi uchun qayta kelish",
)
ScheduledVisit.objects.create(
    patient=patients[30], doctor=d2,
    scheduled_date=(now + timedelta(days=5)).date(),
    notes="Katarakta operatsiyasi uchun tayyorgarlik",
)
ScheduledVisit.objects.create(
    patient=patients[35], doctor=d3,
    scheduled_date=(now + timedelta(days=7)).date(),
    notes="LASIK konsultatsiya",
)
# Today's scheduled visit — for testing "Bugun uchrashuvi bor" button
sv_today = ScheduledVisit.objects.create(
    patient=patients[10], doctor=d2,
    scheduled_date=now.date(),
    notes="Bugungi ko'z tekshiruvi",
)
# Add services to today's scheduled visit
sv_today.services.set([s2])

# ─── GLASSES ───
print("Ko'zoynaklar yaratilmoqda...")
g1 = Glasses.objects.create(model_name="Ray-Ban RB3025", brand="Ray-Ban", lens_type="Polarized", cost_price=500000, sell_price=900000, quantity=15)
g2 = Glasses.objects.create(model_name="Oakley Holbrook", brand="Oakley", lens_type="UV Protection", cost_price=600000, sell_price=1100000, quantity=8)
g3 = Glasses.objects.create(model_name="Gucci GG0036S", brand="Gucci", lens_type="Gradient", cost_price=1200000, sell_price=2200000, quantity=5)
g4 = Glasses.objects.create(model_name="Tom Ford FT0237", brand="Tom Ford", lens_type="Polarized", cost_price=800000, sell_price=1500000, quantity=10)
g5 = Glasses.objects.create(model_name="Silmo Classic", brand="Silmo", lens_type="Blue Light", cost_price=200000, sell_price=450000, quantity=25)
g6 = Glasses.objects.create(model_name="Hugo Boss 0944", brand="Hugo Boss", lens_type="Progressive", cost_price=700000, sell_price=1300000, quantity=0)

# Some glass sales
print("Ko'zoynak sotuvlari yaratilmoqda...")
for i in range(12):
    g = random.choice([g1, g2, g3, g4, g5])
    qty = random.randint(1, 2)
    sale = GlassSale.objects.create(glasses=g, quantity=qty, sell_price=g.sell_price, cost_price=g.cost_price)
    sale.created_at = now - timedelta(days=random.randint(0, 60))
    sale.save(update_fields=['created_at'])

# ─── LAB VISITS ───
print("Laboratoriya tashriflari yaratilmoqda...")
from clinic.lab_services import LAB_SERVICES

# Create some lab visits
for i in range(5):
    p = random.choice(patients[:20])
    lv = LabVisit.objects.create(patient=p, status='done', completed_at=now - timedelta(days=random.randint(1, 30)))
    lv.created_at = lv.completed_at - timedelta(hours=2)
    lv.save(update_fields=['created_at'])
    # Add 2-4 random lab services
    selected = random.sample(LAB_SERVICES[:50], random.randint(2, 4))
    for num, name, price, *rest in selected:
        LabVisitService.objects.create(lab_visit=lv, service_number=num, service_name=name, price=price, result=f"Natija: norma ({random.randint(1, 10)}.{random.randint(0, 9)})")

# Active lab visits (waiting)
for i in range(2):
    p = random.choice(patients[20:30])
    lv = LabVisit.objects.create(patient=p, status='waiting')
    selected = random.sample(LAB_SERVICES[:30], random.randint(1, 3))
    for num, name, price, *rest in selected:
        LabVisitService.objects.create(lab_visit=lv, service_number=num, service_name=name, price=price)

# ─── EYE EXAMINATION DATA ───
print("Ko'z tekshiruv ma'lumotlari yaratilmoqda...")
done_visits = Visit.objects.filter(status='done')[:10]
for v in done_visits:
    if random.random() < 0.5:
        EyeRefraction.objects.create(
            visit=v, patient=v.patient,
            od_s=f"{random.uniform(-5, 2):.2f}", od_c=f"{random.uniform(-3, 0):.2f}", od_a=f"{random.randint(0, 180)}",
            os_s=f"{random.uniform(-5, 2):.2f}", os_c=f"{random.uniform(-3, 0):.2f}", os_a=f"{random.randint(0, 180)}",
        )
    if random.random() < 0.4:
        EyeKRT.objects.create(
            visit=v, patient=v.patient,
            od_d=f"{random.uniform(40, 48):.2f}", od_mm=f"{random.uniform(7, 9):.2f}", od_a=f"{random.randint(0, 180)}",
            os_d=f"{random.uniform(40, 48):.2f}", os_mm=f"{random.uniform(7, 9):.2f}", os_a=f"{random.randint(0, 180)}",
        )
    if random.random() < 0.3:
        EyeIOP.objects.create(
            visit=v, patient=v.patient,
            od_value=str(random.randint(10, 22)),
            os_value=str(random.randint(10, 22)),
        )

print(f"\nSeed ma'lumotlar muvaffaqiyatli yaratildi!")
print(f"  Xizmatlar: {Service.objects.count()}")
print(f"  Doktorlar: {Worker.objects.filter(worker_type='doctor').count()}")
print(f"  Xarajatlar: {Expense.objects.count()}")
print(f"  Yo'naltiruvchilar: {ReferralPartner.objects.count()}")
print(f"  Bemorlar: {Patient.objects.count()}")
print(f"  Tashriflar: {Visit.objects.count()}")
print(f"  Ko'zoynaklar: {Glasses.objects.count()}")
print(f"  Ko'zoynak sotuvlari: {GlassSale.objects.count()}")
print(f"  Lab tashriflar: {LabVisit.objects.count()}")
print(f"  Ko'z tekshiruvlari (REF): {EyeRefraction.objects.count()}")
print(f"  Foydalanuvchi akkauntlari: {UserAccount.objects.count()}")
print("\n--- Kirish ma'lumotlari ---")
print("TIZIM AKKAUNTLARI (hardcoded, har doim ishlaydi):")
print("  Admin:        Sherzod           | 911666222")
print("  Resepsionist: reception         | 123")
print("  Laboratoriya: labaratoriya      | 123")
print("\nBD AKKAUNTLARI:")
print("  Doktor:       Aziz Kamolov       | 901000002")
print("  Doktor:       Jamshid Rahimov    | 901000003")
print("  Doktor:       Dilnoza Toshmatova | 901000004")
print("  Doktor:       Sardor Mirzayev    | 901000005")
print("  Doktor:       Nodira Abdullayeva | 901000006")
print("\nTIZIM AKKAUNTLARI (davomi):")
print("  Optika:       optika             | 123")
