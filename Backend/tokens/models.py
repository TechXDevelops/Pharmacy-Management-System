from django.db import models
from patients.models import Patient
from pharmacy.models import Pharmacy, Counter

class Token(models.Model):
    token_number = models.IntegerField()

    patient = models.ForeignKey(
        Patient,
        to_field="patient_id",
        on_delete=models.CASCADE
    )

    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE)

    counter = models.ForeignKey(
        Counter,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    # 🔥 make these nullable OR remove later
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)

    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("pharmacy", "token_number")
