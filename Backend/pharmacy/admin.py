from django.contrib import admin
from .models import Pharmacy, Counter


@admin.register(Pharmacy)
class PharmacyAdmin(admin.ModelAdmin):
    list_display = ("pharmacy_id", "name", "is_active")


@admin.register(Counter)
class CounterAdmin(admin.ModelAdmin):
    list_display = ("pharmacy", "counter_name", "is_active")
