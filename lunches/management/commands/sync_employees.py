import os
from django.core.management.base import BaseCommand
from lunches.models import Collaborator


class Command(BaseCommand):
    help = "Sincroniza colaboradores activos desde EMPLOYEES."

    def handle(self, *args, **options):
        raw_employees = os.getenv("EMPLOYEES", "")

        names = {
            name.strip()
            for name in raw_employees.split(",")
            if name.strip()
        }

        for name in names:
            collaborator, created = Collaborator.objects.get_or_create(
                name=name,
                defaults={"is_active": True},
            )

            if not created and not collaborator.is_active:
                collaborator.is_active = True
                collaborator.save(update_fields=["is_active"])

        Collaborator.objects.exclude(name__in=names).update(is_active=False)

        self.stdout.write(
            self.style.SUCCESS(f"Sincronización completa. Activos: {len(names)}")
        )