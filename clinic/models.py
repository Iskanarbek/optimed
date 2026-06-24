from django.db import models
from django.utils import timezone
import datetime
import uuid


# ─── HELPER: Queue Number ───

def get_next_queue_number(doctor=None):
    """Get the next queue number for today, per doctor."""
    today = timezone.localdate()
    qs = QueueNumber.objects.filter(date=today)
    if doctor:
        qs = qs.filter(doctor=doctor)
    last = qs.order_by('-number').first()
    return (last.number + 1) if last else 1


def get_next_lab_queue_number():
    """Get the next lab queue number for today."""
    today = timezone.localdate()
    last = LabQueueNumber.objects.filter(date=today).order_by('-number').first()
    return (last.number + 1) if last else 1


class UserAccount(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('doctor', 'Doktor'),
        ('receptionist', 'Resepsionist'),
        ('seller', 'Sotuvchi'),
    ]
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, unique=True)
    role = models.CharField(max_length=15, choices=ROLE_CHOICES)
    worker = models.OneToOneField(
        'Worker', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='account'
    )

    def __str__(self):
        return f"{self.name} {self.surname} ({self.get_role_display()})"

    @property
    def full_name(self):
        return f"{self.name} {self.surname}"


class Service(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.price} so'm"


class ClinicalProcedure(models.Model):
    """Catalog of clinical procedures (managed by admin)."""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price_per_session = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.price_per_session} so'm/seans"


class Worker(models.Model):
    WORKER_TYPES = [
        ('doctor', 'Doktor'),
        ('other', 'Boshqa xodim'),
    ]
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    salary = models.IntegerField(default=0)
    worker_type = models.CharField(max_length=10, choices=WORKER_TYPES)
    room_number = models.CharField(max_length=20, blank=True, default='')
    description = models.TextField(blank=True, help_text="Lavozim tavsifi")
    service = models.ForeignKey(
        Service, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='doctors'
    )
    services = models.ManyToManyField(
        Service, blank=True, related_name='assigned_doctors'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} {self.surname} ({self.get_worker_type_display()})"

    @property
    def full_name(self):
        return f"{self.name} {self.surname}"


class Patient(models.Model):
    GENDER_CHOICES = [
        ('erkak', 'Erkak'),
        ('ayol', 'Ayol'),
    ]
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    address = models.TextField(blank=True)
    gender = models.CharField(max_length=10, blank=True, choices=GENDER_CHOICES)
    age = models.IntegerField(null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} {self.surname}"

    @property
    def full_name(self):
        return f"{self.name} {self.surname}"


class Visit(models.Model):
    STATUS_CHOICES = [
        ('waiting', 'Kutmoqda'),
        ('in_progress', 'Qabulda'),
        ('done', 'Tugatildi'),
        ('has_procedure', 'Protsedurasi bor'),
    ]
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='visits')
    doctor = models.ForeignKey(
        Worker, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='visits', limit_choices_to={'worker_type': 'doctor'}
    )
    doctor_name = models.CharField(max_length=200, blank=True, default='')
    referred_by = models.ForeignKey(
        'ReferralPartner', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='visits'
    )
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True, related_name='visits')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='waiting')
    discount_amount = models.IntegerField(default=0)
    discount_reason = models.TextField(blank=True)
    # Expanded medical notes fields
    tashxis = models.TextField(blank=True)
    tavsiya = models.TextField(blank=True)
    gavhar = models.TextField(blank=True)
    korish_otkirligi = models.TextField(blank=True)
    shishasimon_tana = models.TextField(blank=True)
    fundus_od = models.TextField(blank=True, default='')
    fundus_os = models.TextField(blank=True, default='')
    ubm_od = models.TextField(blank=True, default='')
    ubm_os = models.TextField(blank=True, default='')
    oct_od = models.TextField(blank=True, default='')
    oct_os = models.TextField(blank=True, default='')
    kp_od = models.TextField(blank=True, default='')
    kp_os = models.TextField(blank=True, default='')
    b_skan_od = models.TextField(blank=True, default='')
    b_skan_os = models.TextField(blank=True, default='')
    periferiya_od = models.TextField(blank=True, default='')
    periferiya_os = models.TextField(blank=True, default='')
    oftalmoskopiya = models.TextField(blank=True)
    anamnesis_morbi = models.TextField(blank=True)
    operatsiyalar = models.TextField(blank=True)
    tomizilgan = models.TextField(blank=True)
    koz_oynak_kontakt_linza = models.TextField(blank=True)
    retsept_uzoq_od = models.TextField(blank=True, default='')
    retsept_uzoq_os = models.TextField(blank=True, default='')
    retsept_yaqin_od = models.TextField(blank=True, default='')
    retsept_yaqin_os = models.TextField(blank=True, default='')
    retsept_kontakt_od = models.TextField(blank=True, default='')
    retsept_kontakt_os = models.TextField(blank=True, default='')
    anamnesis_vitae = models.TextField(blank=True)
    allergiya = models.TextField(blank=True)
    qovoqlar_koz_yosh_yollari = models.TextField(blank=True)
    koz_soqqasi = models.TextField(blank=True)
    koz_olmasi = models.TextField(blank=True)
    sklera = models.TextField(blank=True)
    shox_parda = models.TextField(blank=True)
    old_kamera = models.TextField(blank=True)
    rangdor_parda_qorachiq = models.TextField(blank=True)
    # OD/OS split anatomy fields for tibbiy yozuv
    qovoqlar_od = models.TextField(blank=True, default='')
    qovoqlar_os = models.TextField(blank=True, default='')
    koz_soqqasi_od = models.TextField(blank=True, default='')
    koz_soqqasi_os = models.TextField(blank=True, default='')
    koz_olmasi_od = models.TextField(blank=True, default='')
    koz_olmasi_os = models.TextField(blank=True, default='')
    sklera_od = models.TextField(blank=True, default='')
    sklera_os = models.TextField(blank=True, default='')
    shox_parda_od = models.TextField(blank=True, default='')
    shox_parda_os = models.TextField(blank=True, default='')
    old_kamera_od = models.TextField(blank=True, default='')
    old_kamera_os = models.TextField(blank=True, default='')
    rangdor_parda_od = models.TextField(blank=True, default='')
    rangdor_parda_os = models.TextField(blank=True, default='')
    gavhar_od = models.TextField(blank=True, default='')
    gavhar_os = models.TextField(blank=True, default='')
    korish_otkirligi_od = models.TextField(blank=True, default='')
    korish_otkirligi_os = models.TextField(blank=True, default='')
    korreksiya_bilan_od = models.TextField(blank=True, default='')
    korreksiya_bilan_os = models.TextField(blank=True, default='')
    shishasimon_tana_od = models.TextField(blank=True, default='')
    shishasimon_tana_os = models.TextField(blank=True, default='')
    oftalmoskopiya_od = models.TextField(blank=True, default='')
    oftalmoskopiya_os = models.TextField(blank=True, default='')
    # Legacy fields kept for backward compatibility
    problem = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    attachment = models.FileField(upload_to='attachments/', blank=True, null=True)
    doctor_rating = models.IntegerField(null=True, blank=True)
    clinic_rating = models.IntegerField(null=True, blank=True)
    rated = models.BooleanField(default=False)
    share_token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        doc_name = self.doctor.surname if self.doctor else "—"
        return f"Tashrif: {self.patient} -> Dr. {doc_name} ({self.get_status_display()})"

    @property
    def total_services_price(self):
        """Total price from all VisitService rows (before discount)."""
        total = sum(vs.price_at_time for vs in self.visit_services.all())
        if total == 0 and self.service:
            total = self.service.price if self.service else 0
        return total

    @property
    def total_procedures_price(self):
        """Total price from all Procedure rows."""
        return sum(p.total_price for p in self.procedures.all())

    @property
    def total_price(self):
        """Total price before discount (services + procedures)."""
        return self.total_services_price + self.total_procedures_price

    @property
    def final_price(self):
        return max(self.total_price - self.discount_amount, 0)

    @property
    def commission_amount(self):
        if self.referred_by:
            if self.referred_by.commission_type == 'fixed':
                return self.referred_by.commission_fixed
            return int(self.final_price * self.referred_by.commission_percent / 100)
        return 0


class Procedure(models.Model):
    visit = models.ForeignKey(Visit, on_delete=models.CASCADE, related_name='procedures')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='procedures')
    doctor = models.ForeignKey(Worker, on_delete=models.SET_NULL, null=True, blank=True, related_name='procedures')
    clinical_procedure = models.ForeignKey(
        ClinicalProcedure, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='procedure_instances'
    )
    description = models.TextField()
    total_repetitions = models.IntegerField(default=1)
    price_per_session = models.IntegerField(default=0)
    total_price = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Protsedura: {self.patient} - {self.description[:50]}"

    def recalculate_price(self):
        self.total_price = self.price_per_session * self.total_repetitions
        self.save(update_fields=['total_price'])

    @property
    def completed_count(self):
        return self.dates.filter(completed=True).count()

    @property
    def is_complete(self):
        return not self.dates.filter(completed=False).exists()

    @property
    def progress_text(self):
        return f"{self.completed_count}/{self.total_repetitions}"


class ProcedureDate(models.Model):
    procedure = models.ForeignKey(Procedure, on_delete=models.CASCADE, related_name='dates')
    scheduled_date = models.DateField()
    completed = models.BooleanField(default=False)
    notified = models.BooleanField(default=False)
    notification_visible = models.BooleanField(default=False)

    class Meta:
        ordering = ['scheduled_date']

    def __str__(self):
        return f"{self.procedure.patient} - {self.scheduled_date}"


class VisitService(models.Model):
    """Junction table: Visit can have multiple Services."""
    visit = models.ForeignKey(Visit, on_delete=models.CASCADE, related_name='visit_services')
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True)
    price_at_time = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        svc = self.service.name if self.service else "—"
        return f"{self.visit} - {svc}"


class VisitAttachment(models.Model):
    """Multiple file attachments per visit."""
    visit = models.ForeignKey(Visit, on_delete=models.CASCADE, related_name='visit_attachments')
    file = models.FileField(upload_to='attachments/')
    title = models.CharField(max_length=200, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Fayl: {self.visit} - {self.file.name}"


class QueueNumber(models.Model):
    """Auto-incrementing daily queue number, per doctor."""
    visit = models.OneToOneField(Visit, on_delete=models.CASCADE, related_name='queue')
    doctor = models.ForeignKey(
        Worker, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='queue_numbers'
    )
    number = models.IntegerField()
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('date', 'number', 'doctor')
        ordering = ['date', 'number']

    def __str__(self):
        return f"Navbat #{self.number} ({self.date})"


class ScheduledVisit(models.Model):
    """Future appointment booking."""
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='scheduled_visits')
    doctor = models.ForeignKey(
        Worker, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='scheduled_visits', limit_choices_to={'worker_type': 'doctor'}
    )
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    services = models.ManyToManyField(Service, blank=True, related_name='scheduled_visits')
    activated = models.BooleanField(default=False)
    is_lab = models.BooleanField(default=False)
    lab_services_data = models.TextField(blank=True, default='')
    visit = models.ForeignKey(
        Visit, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='scheduled_from'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['scheduled_date', 'scheduled_time']

    def __str__(self):
        return f"{self.patient.full_name} - {self.scheduled_date}"


class ReferralPartner(models.Model):
    """External referring doctor/partner who sends patients and earns commission."""
    COMMISSION_TYPE_CHOICES = [
        ('percent', 'Foiz'),
        ('fixed', 'Belgilangan summa'),
    ]
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True, default='')
    clinic_name = models.CharField(max_length=200, blank=True, default='')
    commission_type = models.CharField(max_length=10, choices=COMMISSION_TYPE_CHOICES, default='percent')
    commission_percent = models.IntegerField(default=10)
    commission_fixed = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name', 'surname']

    def __str__(self):
        return f"{self.full_name} ({self.clinic_name or 'Mustaqil'})"

    @property
    def full_name(self):
        return f"{self.name} {self.surname}"

    @property
    def commission_display(self):
        if self.commission_type == 'fixed':
            return f"{self.commission_fixed:,} so'm".replace(',', ' ')
        return f"{self.commission_percent}%"


class Expense(models.Model):
    """Recurring or one-time business expenses."""
    EXPENSE_TYPES = [
        ('recurring', 'Har oylik'),
        ('one_time', 'Bir martalik'),
    ]
    name = models.CharField(max_length=200)
    amount = models.IntegerField(default=0)
    expense_type = models.CharField(max_length=10, choices=EXPENSE_TYPES)
    date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.amount} so'm ({self.get_expense_type_display()})"


# ─── GLASSES ───

class Glasses(models.Model):
    model_name = models.CharField(max_length=200, verbose_name="Model")
    cost_price = models.IntegerField(default=0, verbose_name="Tannarx")
    sell_price = models.IntegerField(default=0, verbose_name="Sotish narxi")
    lens_type = models.CharField(max_length=200, blank=True, verbose_name="Linza turi")
    brand = models.CharField(max_length=100, blank=True, verbose_name="Brend")
    quantity = models.IntegerField(default=0, verbose_name="Miqdori")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.model_name} ({self.brand or 'Brendsiz'}) - {self.quantity} dona"

    @property
    def profit_per_unit(self):
        return self.sell_price - self.cost_price


class GlassSale(models.Model):
    glasses = models.ForeignKey(Glasses, on_delete=models.CASCADE, related_name='sales')
    quantity = models.IntegerField(default=1)
    sell_price = models.IntegerField(default=0)
    cost_price = models.IntegerField(default=0)
    discount_amount = models.IntegerField(default=0, verbose_name="Chegirma (so'm)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.glasses.model_name} x{self.quantity} - {self.created_at:%d.%m.%Y}"

    @property
    def total_revenue(self):
        return (self.sell_price - self.discount_amount) * self.quantity

    @property
    def total_profit(self):
        return (self.sell_price - self.discount_amount - self.cost_price) * self.quantity


# ─── OPTIKA ───

class OptikaPatientPrescription(models.Model):
    """Optika-editable prescription per patient (pre-filled from latest visit)."""
    patient = models.OneToOneField('Patient', on_delete=models.CASCADE, related_name='optika_prescription')
    retsept_uzoq_od = models.CharField(max_length=200, blank=True, default='')
    retsept_uzoq_os = models.CharField(max_length=200, blank=True, default='')
    retsept_yaqin_od = models.CharField(max_length=200, blank=True, default='')
    retsept_yaqin_os = models.CharField(max_length=200, blank=True, default='')
    retsept_kontakt_od = models.CharField(max_length=200, blank=True, default='')
    retsept_kontakt_os = models.CharField(max_length=200, blank=True, default='')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Retsept: {self.patient}"


class OptikaSale(models.Model):
    """A single optika sale — flexible items stored as JSON."""
    patient = models.ForeignKey('Patient', on_delete=models.SET_NULL, null=True, blank=True, related_name='optika_sales')
    items = models.JSONField(default=list)
    total = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Optika sotish: {self.patient} — {self.total:,} so'm ({self.created_at:%d.%m.%Y})"


# ─── EYE EXAMINATION DATA ───

class EyeRefraction(models.Model):
    """REF data for patient visit."""
    visit = models.ForeignKey(Visit, on_delete=models.CASCADE, related_name='refractions')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='refractions')
    # Right eye (OD)
    od_s = models.CharField(max_length=20, blank=True, verbose_name="OD S")
    od_c = models.CharField(max_length=20, blank=True, verbose_name="OD C")
    od_a = models.CharField(max_length=20, blank=True, verbose_name="OD A")
    # Left eye (OS)
    os_s = models.CharField(max_length=20, blank=True, verbose_name="OS S")
    os_c = models.CharField(max_length=20, blank=True, verbose_name="OS C")
    os_a = models.CharField(max_length=20, blank=True, verbose_name="OS A")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"REF: {self.patient} - {self.created_at:%d.%m.%Y}"


class EyeKRT(models.Model):
    """KRT data for patient visit."""
    visit = models.ForeignKey(Visit, on_delete=models.CASCADE, related_name='krts')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='krts')
    # Right eye (OD)
    od_d = models.CharField(max_length=20, blank=True, verbose_name="OD D")
    od_mm = models.CharField(max_length=20, blank=True, verbose_name="OD MM")
    od_a = models.CharField(max_length=20, blank=True, verbose_name="OD A")
    # Left eye (OS)
    os_d = models.CharField(max_length=20, blank=True, verbose_name="OS D")
    os_mm = models.CharField(max_length=20, blank=True, verbose_name="OS MM")
    os_a = models.CharField(max_length=20, blank=True, verbose_name="OS A")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"KRT: {self.patient} - {self.created_at:%d.%m.%Y}"


class EyeIOP(models.Model):
    """IOP (Ko'z bosimi) data for patient visit."""
    visit = models.ForeignKey(Visit, on_delete=models.CASCADE, related_name='iops')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='iops')
    od_value = models.CharField(max_length=20, blank=True, verbose_name="OD (o'ng)")
    os_value = models.CharField(max_length=20, blank=True, verbose_name="OS (chap)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"IOP: {self.patient} - OD:{self.od_value} OS:{self.os_value}"


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


class EyeExamForm(models.Model):
    """Ko'z ko'rigi — A4 printable eye examination form."""
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='eye_exam_forms')
    visit = models.ForeignKey(Visit, on_delete=models.SET_NULL, null=True, blank=True)
    doctor = models.ForeignKey(Worker, on_delete=models.SET_NULL, null=True)
    protocol_number = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    kelish_sanasi = models.DateTimeField(null=True, blank=True)
    filial = models.CharField(max_length=100, blank=True, default='Optimed')
    koz_anamezi = models.TextField(blank=True, default='')
    ref_ong_sph = models.CharField(max_length=20, blank=True, default='')
    ref_ong_cyl = models.CharField(max_length=20, blank=True, default='')
    ref_ong_axis = models.CharField(max_length=20, blank=True, default='')
    ref_chap_sph = models.CharField(max_length=20, blank=True, default='')
    ref_chap_cyl = models.CharField(max_length=20, blank=True, default='')
    ref_chap_axis = models.CharField(max_length=20, blank=True, default='')
    sub_ref_ong_sph = models.CharField(max_length=20, blank=True, default='')
    sub_ref_ong_cyl = models.CharField(max_length=20, blank=True, default='')
    sub_ref_ong_axis = models.CharField(max_length=20, blank=True, default='')
    sub_ref_chap_sph = models.CharField(max_length=20, blank=True, default='')
    sub_ref_chap_cyl = models.CharField(max_length=20, blank=True, default='')
    sub_ref_chap_axis = models.CharField(max_length=20, blank=True, default='')
    sik_ref_ong_sph = models.CharField(max_length=20, blank=True, default='')
    sik_ref_ong_cyl = models.CharField(max_length=20, blank=True, default='')
    sik_ref_ong_axis = models.CharField(max_length=20, blank=True, default='')
    sik_ref_chap_sph = models.CharField(max_length=20, blank=True, default='')
    sik_ref_chap_cyl = models.CharField(max_length=20, blank=True, default='')
    sik_ref_chap_axis = models.CharField(max_length=20, blank=True, default='')
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
    oyku = models.TextField(blank=True, default='')
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
    linza_ong = models.CharField(max_length=50, blank=True, default='')
    linza_chap = models.CharField(max_length=50, blank=True, default='')
    diametr_ong = models.CharField(max_length=50, blank=True, default='')
    diametr_chap = models.CharField(max_length=50, blank=True, default='')
    radius_ong = models.CharField(max_length=50, blank=True, default='')
    radius_chap = models.CharField(max_length=50, blank=True, default='')
    dioptriya_ong = models.CharField(max_length=50, blank=True, default='')
    dioptriya_chap = models.CharField(max_length=50, blank=True, default='')
    icd_kodi = models.CharField(max_length=20, blank=True, default='')
    icd_nomi = models.CharField(max_length=200, blank=True, default='')
    tashxis_turi = models.CharField(max_length=100, blank=True, default='')
    yonalish = models.CharField(max_length=50, blank=True, default='')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Ko'z ko'rigi #{self.protocol_number} - {self.patient}"


class DischargeForm(models.Model):
    """Vipiska — A4 printable discharge summary form."""
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='discharge_forms')
    visit = models.ForeignKey(Visit, on_delete=models.SET_NULL, null=True, blank=True)
    doctor = models.ForeignKey(Worker, on_delete=models.SET_NULL, null=True)
    protocol_number = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    yotish_sanasi = models.DateField(null=True, blank=True)
    chiqish_sanasi = models.DateField(null=True, blank=True)
    shikoyat_tarix = models.TextField(blank=True, default='')
    shaxsiy_oilaviy_tarix = models.TextField(blank=True, default='')
    tizimli_anamnez = models.TextField(blank=True, default='')
    koz_anamezi = models.TextField(blank=True, default='')
    tashxis_kodi_nomi = models.TextField(blank=True, default='')
    operatsiya_kodi_nomi = models.TextField(blank=True, default='')
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


class LasikForm(models.Model):
    """LASIK — хирургическая выписка после лазерной коррекции."""
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='lasik_forms')
    visit = models.ForeignKey(Visit, on_delete=models.SET_NULL, null=True, blank=True)
    doctor = models.ForeignKey(Worker, on_delete=models.SET_NULL, null=True)
    protocol_number = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    tashxis = models.TextField(blank=True, default='')
    operatsiya_turi = models.CharField(max_length=50, blank=True, default='')  # TENEO317/PRK/RTK/dokorrektsiya
    ko_z = models.CharField(max_length=10, blank=True, default='')  # OD/OS/OU
    octavius = models.BooleanField(default=False)
    operatsiya_sanasi = models.DateField(null=True, blank=True)
    oper_hirurg = models.CharField(max_length=200, blank=True, default='')
    assistent = models.CharField(max_length=200, blank=True, default='')
    vgd_od = models.CharField(max_length=20, blank=True, default='')
    vgd_os = models.CharField(max_length=20, blank=True, default='')
    preop_vis_od = models.CharField(max_length=20, blank=True, default='')
    preop_sph_od = models.CharField(max_length=20, blank=True, default='')
    preop_cyl_od = models.CharField(max_length=20, blank=True, default='')
    preop_axis_od = models.CharField(max_length=20, blank=True, default='')
    preop_vis_os = models.CharField(max_length=20, blank=True, default='')
    preop_sph_os = models.CharField(max_length=20, blank=True, default='')
    preop_cyl_os = models.CharField(max_length=20, blank=True, default='')
    preop_axis_os = models.CharField(max_length=20, blank=True, default='')
    postop_vis_od = models.CharField(max_length=20, blank=True, default='')
    postop_vis_os = models.CharField(max_length=20, blank=True, default='')
    preop_corr_od = models.CharField(max_length=20, blank=True, default='')
    preop_corr_os = models.CharField(max_length=20, blank=True, default='')
    holat = models.TextField(blank=True, default='')
    tavsiya = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"LASIK #{self.protocol_number} - {self.patient}"


class StrabismusForm(models.Model):
    """Косоглазие — хирургический протокол операции на глазодвигательных мышцах."""
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='strabismus_forms')
    visit = models.ForeignKey(Visit, on_delete=models.SET_NULL, null=True, blank=True)
    doctor = models.ForeignKey(Worker, on_delete=models.SET_NULL, null=True)
    protocol_number = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    shikoyat = models.TextField(blank=True, default='')
    vis = models.CharField(max_length=100, blank=True, default='')
    dev_darajasi = models.CharField(max_length=50, blank=True, default='')
    tashxis = models.TextField(blank=True, default='')
    recession_muscle = models.CharField(max_length=100, blank=True, default='')
    recession_eye = models.CharField(max_length=10, blank=True, default='')
    recession_mm = models.CharField(max_length=20, blank=True, default='')
    resection_muscle = models.CharField(max_length=100, blank=True, default='')
    resection_eye = models.CharField(max_length=10, blank=True, default='')
    resection_mm = models.CharField(max_length=20, blank=True, default='')
    transposition_eye = models.CharField(max_length=10, blank=True, default='')
    postop_dev = models.CharField(max_length=50, blank=True, default='')
    tavsiya = models.TextField(blank=True, default='')
    gilaylik_keyin = models.TextField(blank=True, default='')
    gilaylik_keyin_ru = models.TextField(blank=True, default='')
    dorilar = models.TextField(blank=True, default='')
    dorilar_ru = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Ko'squlilik #{self.protocol_number} - {self.patient}"


class PostOpForm(models.Model):
    """Операционная выписка — post-operative discharge summary."""
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='postop_forms')
    visit = models.ForeignKey(Visit, on_delete=models.SET_NULL, null=True, blank=True)
    doctor = models.ForeignKey(Worker, on_delete=models.SET_NULL, null=True)
    protocol_number = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    davolash_boshlanishi = models.DateField(null=True, blank=True)
    davolash_tugashi = models.DateField(null=True, blank=True)
    asosiy_tashxis = models.TextField(blank=True, default='')
    qoshimcha_tashxis = models.TextField(blank=True, default='')
    hamroh_kasallik = models.TextField(blank=True, default='')
    qabulda_vis_od = models.CharField(max_length=50, blank=True, default='')
    qabulda_vis_os = models.CharField(max_length=50, blank=True, default='')
    qabulda_od = models.CharField(max_length=200, blank=True, default='')
    qabulda_os = models.CharField(max_length=200, blank=True, default='')
    xususiyatlar = models.TextField(blank=True, default='')
    operatsiya = models.TextField(blank=True, default='')
    narkoz_turi = models.CharField(max_length=50, blank=True, default='')  # vv/mestnaya
    operatsiya_sanasi = models.DateField(null=True, blank=True)
    hirurg = models.CharField(max_length=200, blank=True, default='')
    chiqimda_vis_od = models.CharField(max_length=50, blank=True, default='')
    chiqimda_vis_os = models.CharField(max_length=50, blank=True, default='')
    chiqimda_od = models.CharField(max_length=200, blank=True, default='')
    chiqimda_os = models.CharField(max_length=200, blank=True, default='')
    xususiyat_chiqim = models.TextField(blank=True, default='')
    tavsiya = models.TextField(blank=True, default='')
    keyingi_qayta_korish = models.CharField(max_length=100, blank=True, default='')
    lech_vrach = models.CharField(max_length=200, blank=True, default='')
    bemor_eslatma = models.TextField(blank=True, default='')
    bemor_eslatma_ru = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Operatsionnaya ko'chirma #{self.protocol_number} - {self.patient}"


# ─── LABORATORY ───

class LabVisit(models.Model):
    """Laboratory visit - when patient is sent to lab."""
    STATUS_CHOICES = [
        ('waiting', 'Kutmoqda'),
        ('in_progress', 'Jarayonda'),
        ('done', 'Tayyor'),
    ]
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='lab_visits')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='waiting')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Lab: {self.patient} ({self.get_status_display()})"

    @property
    def total_price(self):
        return sum(ls.price for ls in self.lab_services.all())


class LabVisitService(models.Model):
    """Services chosen for a lab visit."""
    lab_visit = models.ForeignKey(LabVisit, on_delete=models.CASCADE, related_name='lab_services')
    service_number = models.IntegerField(default=0)
    service_name = models.CharField(max_length=300)
    price = models.IntegerField(default=0)
    result = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['service_number']

    def __str__(self):
        return f"#{self.service_number} {self.service_name}"


class LabQueueNumber(models.Model):
    """Daily queue number for laboratory visits."""
    lab_visit = models.OneToOneField(LabVisit, on_delete=models.CASCADE, related_name='queue')
    number = models.IntegerField()
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('date', 'number')
        ordering = ['date', 'number']

    def __str__(self):
        return f"Lab #{self.number} ({self.date})"


class LabServiceTemplate(models.Model):
    """Editable lab service catalog managed by laborant."""
    number = models.IntegerField(unique=True)
    name = models.CharField(max_length=500)
    price = models.IntegerField(default=0)
    reference_value = models.TextField(blank=True)

    class Meta:
        ordering = ['number']

    def __str__(self):
        return f"#{self.number} {self.name}"
