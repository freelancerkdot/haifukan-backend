"""Seed the notice board (お知らせ掲示板) with the posts previously hard-coded
on the frontend (see ``app/review/page.tsx``).

Usage:
    python manage.py seed_board          # create missing posts
    python manage.py seed_board --reset  # delete all then recreate
"""

import json
from pathlib import Path

from django.core.management.base import BaseCommand

from misc.models import BoardPost

DATA_FILE = Path(__file__).resolve().parent / "board_posts_data.json"


class Command(BaseCommand):
    help = "Populate the BoardPost table with the default notice-board posts."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete all existing board posts before seeding.",
        )

    def handle(self, *args, **options):
        if options["reset"]:
            deleted, _ = BoardPost.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"Deleted {deleted} existing post(s)."))

        with DATA_FILE.open(encoding="utf-8") as f:
            posts = json.load(f)

        created, updated = 0, 0
        for post in posts:
            _, was_created = BoardPost.objects.update_or_create(
                posted_date=post["posted_date"],
                content=post["content"],
                defaults={"is_active": True, "created_by": None},
            )
            if was_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Board seeded: {created} created, {updated} updated, "
                f"{BoardPost.objects.count()} total."
            )
        )
