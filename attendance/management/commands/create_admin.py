import os

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Create or update the deployment admin account'

    def handle(self, *args, **options):
        username = os.getenv('ADMIN_USERNAME')
        password = os.getenv('ADMIN_PASSWORD')

        if not username or not password:
            self.stdout.write(
                self.style.WARNING(
                    'ADMIN_USERNAME or ADMIN_PASSWORD is not configured.'
                )
            )
            return

        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'is_staff': True,
                'is_superuser': True,
                'is_active': True,
            }
        )

        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.set_password(password)
        user.save()

        if created:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Admin account "{username}" created successfully.'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Admin account "{username}" updated successfully.'
                )
            )