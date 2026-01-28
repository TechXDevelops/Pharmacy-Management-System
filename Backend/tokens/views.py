from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone

from pharmacy.models import Pharmacy, Counter
from patients.models import Patient
from .models import Token   # 🔥 IMPORTANT IMPORT

from .services import (
    assign_token,
    billing_done,
    get_display_board,
    calculate_expected_time,
    assign_waiting_tokens
)


# -----------------------------
# GENERATE TOKEN
# -----------------------------
@api_view(["POST"])
def generate_token_api(request, pharmacy_id):
    patient_id = request.data.get("patient_id")

    try:
        patient = Patient.objects.get(patient_id=patient_id)
    except Patient.DoesNotExist:
        return Response({"error": "Patient not found"}, status=404)

    token = assign_token(patient, pharmacy_id)
    token.refresh_from_db()

    # 🔥 FIRST ESTIMATE AT GENERATION TIME
    generated_time = calculate_expected_time(token)

    return Response({
        "token": token.token_number,
        "generated_expected_time": (
            timezone.localtime(generated_time).strftime("%H:%M")
            if generated_time else None
        )
    })


# -----------------------------
# DISPLAY BOARD
# -----------------------------
@api_view(["GET"])
def display_board_api(request, pharmacy_id):
    return Response(get_display_board(pharmacy_id))


# -----------------------------
# MANUAL BILLING DONE
# -----------------------------
@api_view(["POST"])
def manual_billing_done_api(request):
    counter_name = request.data.get("counter")

    billing_done(counter_name)

    return Response({
        "message": f"Billing completed for {counter_name}"
    })


# -----------------------------
# ADD COUNTER
# -----------------------------
@api_view(["POST"])
def add_counter_api(request, pharmacy_id):
    pharmacy = Pharmacy.objects.get(pharmacy_id=pharmacy_id)

    count = pharmacy.counters.count() + 1
    name = f"C{count}"

    Counter.objects.create(
        pharmacy=pharmacy,
        counter_name=name,
        is_active=True
    )

    # 🔥 fill ALL free counters
    assign_waiting_tokens(pharmacy)

    return Response({
        "message": "Counter added",
        "counter": name
    })


# -----------------------------
# CHECK TOKEN TIME (LIVE)
# -----------------------------
@api_view(["GET"])
def token_time_api(request, pharmacy_id, token_number):
    try:
        token = Token.objects.get(
            pharmacy__pharmacy_id=pharmacy_id,
            token_number=token_number,
            completed=False
        )
    except Token.DoesNotExist:
        return Response({"error": "Token not found"}, status=404)

    current_time = calculate_expected_time(token)

    return Response({
        "token": token_number,
        "current_expected_time": (
            timezone.localtime(current_time).strftime("%H:%M")
            if current_time else None
        )
    })
