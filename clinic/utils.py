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
