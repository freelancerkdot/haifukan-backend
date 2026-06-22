"""Seed the dynamic sidebar with the menu items previously hard-coded
on the frontend (see ``lib/data/navigation.ts``).

Usage:
    python manage.py seed_sidebar          # create missing items
    python manage.py seed_sidebar --reset  # delete all then recreate
"""

from django.core.management.base import BaseCommand

from admin.models import SidebarMenuItem

# (order, label, href, icon, link_type) — icon is a Lucide icon name used on
# the frontend; link_type is "menu" (icon menu) or "text" (plain text links).
DEFAULT_ITEMS = [
    (1, "依頼者の皆様へ", "/for-request", "Users", "menu"),
    (2, "配布者の皆様へ", "/for-post", "UserCheck", "menu"),
    (3, "依頼を掲載する", "/create", "FileText", "menu"),
    (4, "禁止物件登録", "/prohibited", "Ban", "menu"),
    (5, "よくある質問", "/question", "HelpCircle", "menu"),
    (6, "お問い合わせ", "/inquiry", "Mail", "menu"),
    (7, "お知らせ掲示板", "/review", "Pencil", "menu"),
    # Secondary plain-text links (rendered under the icon menu).
    (8, "特定商取引法に基づく表示", "/legal", "", "text"),
    (9, "プライバシーポリシー", "/privacy", "", "text"),
]


class Command(BaseCommand):
    help = "Populate the SidebarMenuItem table with the default menu items."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete all existing sidebar items before seeding.",
        )

    def handle(self, *args, **options):
        if options["reset"]:
            deleted, _ = SidebarMenuItem.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"Deleted {deleted} existing item(s)."))

        created, updated = 0, 0
        for order, label, href, icon, link_type in DEFAULT_ITEMS:
            obj, was_created = SidebarMenuItem.objects.update_or_create(
                href=href,
                defaults={
                    "label": label,
                    "icon": icon,
                    "link_type": link_type,
                    "order": order,
                    "is_active": True,
                },
            )
            if was_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Sidebar seeded: {created} created, {updated} updated, "
                f"{SidebarMenuItem.objects.count()} total."
            )
        )
