from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Creates a superuser automatically'

    def handle(self, *args, **kwargs):
        if not User.objects.filter(username='ahmed').exists():
            User.objects.create_superuser(
                username='ahmed',
                password='Raaxo9318',
                email='xararavic1547@example.com'
            )
            self.stdout.write(self.style.SUCCESS('Superuser created successfully.'))
        else:
            self.stdout.write(self.style.WARNING('Superuser already exists.'))
