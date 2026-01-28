from django.db import models

class Pharmacy(models.Model):
    pharmacy_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Counter(models.Model):
    pharmacy = models.ForeignKey(
        Pharmacy,
        related_name="counters",
        on_delete=models.CASCADE
    )
    counter_name = models.CharField(max_length=10)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("pharmacy", "counter_name")
