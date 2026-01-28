from datetime import timedelta
from django.utils import timezone
from pharmacy.models import Pharmacy, Counter
from .models import Token

BILLING_TIME_SEC = 180


# -----------------------------
# AUTO COMPLETE EXPIRED TOKENS
# -----------------------------
def auto_complete_expired_tokens(pharmacy):
    now = timezone.now()
    expiry_limit = now - timedelta(seconds=BILLING_TIME_SEC)

    expired_tokens = Token.objects.filter(
        pharmacy=pharmacy,
        completed=False,
        counter__isnull=False,
        created_at__lte=expiry_limit
    )

    for token in expired_tokens:
        token.completed = True
        token.save()

    assign_waiting_tokens(pharmacy)


# -----------------------------
# GET FREE COUNTERS
# -----------------------------
def get_free_counters(pharmacy):
    counters = Counter.objects.filter(
        pharmacy=pharmacy,
        is_active=True
    ).order_by("counter_name")

    free = []
    for c in counters:
        if not Token.objects.filter(
            counter=c,
            completed=False
        ).exists():
            free.append(c)
    return free


# -----------------------------
# ASSIGN WAITING TOKENS (IMPORTANT)
# -----------------------------
def assign_waiting_tokens(pharmacy):
    free_counters = get_free_counters(pharmacy)

    waiting_tokens = Token.objects.filter(
        pharmacy=pharmacy,
        completed=False,
        counter__isnull=True
    ).order_by("created_at")

    for counter in free_counters:
        token = waiting_tokens.first()
        if not token:
            break

        token.counter = counter
        token.save()

        waiting_tokens = waiting_tokens.exclude(pk=token.pk)


# -----------------------------
# ASSIGN TOKEN
# -----------------------------
def assign_token(patient, pharmacy_id):
    pharmacy = Pharmacy.objects.get(
        pharmacy_id=pharmacy_id,
        is_active=True
    )

    auto_complete_expired_tokens(pharmacy)

    existing = Token.objects.filter(
        patient=patient,
        pharmacy=pharmacy,
        completed=False
    ).first()
    if existing:
        return existing

    last = Token.objects.filter(
        pharmacy=pharmacy
    ).order_by("-token_number").first()

    token_number = last.token_number + 1 if last else 1

    free_counters = get_free_counters(pharmacy)
    counter = free_counters[0] if free_counters else None

    return Token.objects.create(
        token_number=token_number,
        patient=patient,
        pharmacy=pharmacy,
        counter=counter
    )


# -----------------------------
# EXPECTED TIME (🔥 CORE LOGIC)
# -----------------------------
def calculate_expected_time(token):
    now = timezone.now()

    # If already at counter → now
    if token.counter:
        return now

    active_counters = Counter.objects.filter(
        pharmacy=token.pharmacy,
        is_active=True
    ).count()

    if active_counters == 0:
        return None

    # 🔥 remaining time of currently running billing
    running_tokens = Token.objects.filter(
        pharmacy=token.pharmacy,
        completed=False,
        counter__isnull=False
    ).order_by("created_at")

    if running_tokens.exists():
        first_running = running_tokens.first()
        billing_end = first_running.created_at + timedelta(seconds=BILLING_TIME_SEC)
        remaining = max(
            timedelta(0),
            billing_end - now
        )
    else:
        remaining = timedelta(0)

    # 🔥 count waiting tokens ahead of me
    waiting_ahead = Token.objects.filter(
        pharmacy=token.pharmacy,
        completed=False,
        counter__isnull=True,
        created_at__lt=token.created_at
    ).count()

    rounds = waiting_ahead // active_counters

    return now + remaining + timedelta(seconds=rounds * BILLING_TIME_SEC)


# -----------------------------
# MANUAL BILLING DONE
# -----------------------------
def billing_done(counter_name):
    token = Token.objects.filter(
        counter__counter_name=counter_name,
        completed=False
    ).first()

    if not token:
        return

    token.completed = True
    token.save()

    assign_waiting_tokens(token.pharmacy)


# -----------------------------
# DISPLAY BOARD
# -----------------------------
def get_display_board(pharmacy_id):
    pharmacy = Pharmacy.objects.get(pharmacy_id=pharmacy_id)

    auto_complete_expired_tokens(pharmacy)

    counters = Counter.objects.filter(
        pharmacy=pharmacy,
        is_active=True
    ).order_by("counter_name")

    current = {}
    for c in counters:
        t = Token.objects.filter(
            counter=c,
            completed=False
        ).first()
        current[c.counter_name] = t.token_number if t else None

    waiting = list(
        Token.objects.filter(
            pharmacy=pharmacy,
            completed=False,
            counter__isnull=True
        ).order_by("created_at")
        .values_list("token_number", flat=True)
    )

    return {
        "current": current,
        "waiting": waiting
    }
