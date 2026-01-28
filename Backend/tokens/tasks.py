from celery import shared_task
from tokens.services import check_and_assign_waiting_tokens
from pharmacy.models import Pharmacy


@shared_task
def auto_assign_waiting_tokens():
    """
    Automatically assign waiting tokens to free counters across all pharmacies
    This task can be run periodically to ensure tokens are assigned efficiently
    """
    pharmacies = Pharmacy.objects.all()
    total_assigned = 0
    
    for pharmacy in pharmacies:
        # Count how many tokens were waiting before assignment
        waiting_before = pharmacy.token_set.filter(
            completed=False,
            counter__isnull=True
        ).count()
        
        # Assign waiting tokens to free counters
        check_and_assign_waiting_tokens(pharmacy)
        
        # Count how many tokens are waiting after assignment
        waiting_after = pharmacy.token_set.filter(
            completed=False,
            counter__isnull=True
        ).count()
        
        assigned_count = waiting_before - waiting_after
        total_assigned += assigned_count
    
    return f"Auto-assigned {total_assigned} tokens across all pharmacies"


@shared_task
def assign_waiting_tokens_for_pharmacy(pharmacy_id):
    """
    Assign waiting tokens to free counters for a specific pharmacy
    """
    try:
        pharmacy = Pharmacy.objects.get(pharmacy_id=pharmacy_id)
        check_and_assign_waiting_tokens(pharmacy)
        return f"Successfully assigned waiting tokens for pharmacy {pharmacy_id}"
    except Pharmacy.DoesNotExist:
        return f"Pharmacy with ID {pharmacy_id} does not exist"