from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    """Management command to seed the database with initial data."""

    help = "Seed database with initial data"

    def add_arguments(self, parser):
        parser.add_argument("--create-super-user", action="store_true")
        parser.add_argument("-u", type=str, default="admin")
        parser.add_argument("-p", type=str, default="admin")

    def handle(self, *args, **options):
        self.create_super_user = options["create_super_user"]
        self.username = options["u"].strip()
        self.password = options["p"].strip()

        if options["create_super_user"]:
            if User.objects.filter(username=self.username).exists():
                self.stdout.write(
                    self.style.WARNING(f'Superuser "{self.username}" already exists')
                )
                return

            _handle_superuser_creation(self.username, self.password)

            self.stdout.write(
                self.style.SUCCESS(f'Superuser "{self.username}" created successfully')
            )


def _handle_superuser_creation(username: str, password: str) -> None:
    User.objects.create_superuser(username=username, email=None, password=password)
