"""Import the default navbar logo into media and create the AppLogo record.

Copies the SVG that previously lived in the frontend's ``public/`` folder into
the backend ``MEDIA_ROOT`` and points the (singleton) AppLogo row at it.

Usage:
    python manage.py seed_logo
    python manage.py seed_logo --source /path/to/haifukan-logo.svg
"""

import os

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError

from admin.models import AppLogo

# Default location of the logo shipped with the frontend.
DEFAULT_SOURCE = os.path.normpath(
    os.path.join(
        settings.BASE_DIR,
        "..",
        "haifukan-frontend",
        "public",
        "haifukan-logo.svg",
    )
)


class Command(BaseCommand):
    help = "Import the default app logo into media and create the AppLogo row."

    def add_arguments(self, parser):
        parser.add_argument(
            "--source",
            default=DEFAULT_SOURCE,
            help="Path to the logo image to import.",
        )

    def handle(self, *args, **options):
        source = options["source"]
        if not os.path.isfile(source):
            raise CommandError(f"Logo source not found: {source}")

        if AppLogo.objects.exists():
            self.stdout.write(
                self.style.WARNING("An AppLogo already exists; skipping import.")
            )
            return

        filename = os.path.basename(source)
        logo = AppLogo(alt="配布館")
        with open(source, "rb") as fh:
            logo.image.save(filename, File(fh), save=True)

        self.stdout.write(
            self.style.SUCCESS(f"App logo imported: {logo.image.url}")
        )
