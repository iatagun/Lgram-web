from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Create a superuser account'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Username for superuser')
        parser.add_argument('--email', type=str, help='Email for superuser')
        parser.add_argument('--password', type=str, help='Password for superuser')

    def handle(self, *args, **options):
        username = options.get('username') or 'admin'
        email = options.get('email') or 'admin@lgram.local'
        password = options.get('password') or 'admin123'

        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'User "{username}" already exists!')
            )
            return

        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'Superuser "{username}" created successfully!\n'
                f'Username: {username}\n'
                f'Email: {email}\n'
                f'Password: {password}\n'
                f'You can now login to admin panel at http://127.0.0.1:8000/admin/'
            )
        )
