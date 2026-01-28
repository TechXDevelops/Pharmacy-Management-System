from django.core.management.base import BaseCommand
from tokens.services import check_and_assign_waiting_tokens
from pharmacy.models import Pharmacy


class Command(BaseCommand):
    help = 'Manually update and assign waiting tokens to free counters'

    def add_arguments(self, parser):
        parser.add_argument('--pharmacy-id', type=str, help='Pharmacy ID to update')
        parser.add_argument(
            '--all-pharmacies',
            action='store_true',
            help='Update all pharmacies'
        )

    def handle(self, *args, **options):
        if options['all_pharmacies']:
            pharmacies = Pharmacy.objects.all()
            for pharmacy in pharmacies:
                self.stdout.write(f'Updating counters for pharmacy: {pharmacy.pharmacy_id}')
                check_and_assign_waiting_tokens(pharmacy)
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully updated pharmacy {pharmacy.pharmacy_id}')
                )
        elif options['pharmacy_id']:
            try:
                pharmacy = Pharmacy.objects.get(pharmacy_id=options['pharmacy_id'])
                self.stdout.write(f'Updating counters for pharmacy: {pharmacy.pharmacy_id}')
                check_and_assign_waiting_tokens(pharmacy)
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully updated pharmacy {pharmacy.pharmacy_id}')
                )
            except Pharmacy.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Pharmacy with ID {options["pharmacy_id"]} does not exist')
                )
        else:
            self.stdout.write(
                self.style.ERROR('Please provide either --pharmacy-id or --all-pharmacies')
            )