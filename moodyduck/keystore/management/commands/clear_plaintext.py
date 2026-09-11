"""
clear_plaintext — null out plaintext fields on records that have an encrypted_payload.

Run this after the staging process has encrypted all existing records:

    python manage.py clear_plaintext [--dry-run]
"""

from django.core.management.base import BaseCommand

from moodyduck.cbt.models import ThoughtRecord
from moodyduck.dreams.models import Dream
from moodyduck.health.models import (
    BasicMedicalInfo,
    HealthLog,
    HealthRecord,
    Medication,
    Vaccination,
)
from moodyduck.mood.models import Activity, Mood, Status

TARGETS = [
    (Status, {"title": None, "text": None}),
    (Mood, {"name": None, "icon": None, "color": None, "value": None}),
    (Activity, {"name": None, "icon": None}),
    (Dream, {"title": None, "content": None}),
    (Medication, {"name": None, "remarks": None}),
    (BasicMedicalInfo, {"blood_type": None, "allergies": None, "medical_notes": None}),
    (HealthLog, {"notes": None}),
    (HealthRecord, {"comment": None}),
    (
        Vaccination,
        {
            "name": None,
            "target_disease": None,
            "provider": None,
            "batch_number": None,
            "notes": None,
        },
    ),
    (
        ThoughtRecord,
        {
            "title": None,
            "situation": None,
            "thoughts": None,
            "pro_facts": None,
            "con_facts": None,
            "realistic": None,
            "outcome": None,
        },
    ),
]


class Command(BaseCommand):
    help = (
        "Null out plaintext fields on records that already have an encrypted_payload."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be updated without making changes.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        total = 0

        for model, null_fields in TARGETS:
            qs = model.objects.filter(encrypted_payload__isnull=False)
            count = qs.count()
            if count == 0:
                continue
            model_name = model.__name__
            self.stdout.write(f"{model_name}: {count} record(s) to clear")
            if not dry_run:
                qs.update(**null_fields)
            total += count

        if dry_run:
            self.stdout.write(
                self.style.WARNING(f"Dry run — {total} record(s) would be cleared.")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f"Cleared plaintext from {total} record(s).")
            )
