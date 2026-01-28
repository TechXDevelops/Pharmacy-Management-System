#!/usr/bin/env python
"""
Script to run the pharmacy token management system
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
    django.setup()
    
    print("Pharmacy Token Management System")
    print("==================================")
    print("Available commands:")
    print("1. Run development server: python run_system.py runserver")
    print("2. Apply migrations: python run_system.py migrate")
    print("3. Create superuser: python run_system.py createsuperuser")
    print("4. Update counters: python run_system.py update_counters --all-pharmacies")
    print("5. Collect static files: python run_system.py collectstatic")
    print("")
    print("To run the system, use one of the above commands")
    
    if len(sys.argv) > 1:
        execute_from_command_line(sys.argv)
    else:
        print("\nExample usage:")
        print("  python run_system.py runserver 8000")
        print("  python run_system.py update_counters --all-pharmacies")
        print("  python run_system.py migrate")