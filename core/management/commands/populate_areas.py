import json
import os

from django.core.management.base import BaseCommand

from core.models import AreaPrefecture, AreaCity, AreaPlace


class Command(BaseCommand):
    help = "Populate area data from JSON files in management/commands/populate/"

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete all area records before re-seeding",
        )

    def handle(self, *args, **options):
        if options["reset"]:
            self.stdout.write(self.style.WARNING("Deleting all area records..."))
            AreaPlace.objects.all().delete()
            AreaCity.objects.all().delete()
            AreaPrefecture.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("All area records deleted."))

        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(base_dir, "populate")

        # 1. Prefectures
        prefecture_path = os.path.join(data_dir, "area_prefecture_data.json")
        with open(prefecture_path, encoding="utf-8") as f:
            prefectures = json.load(f)

        prefecture_count = 0
        for p in prefectures:
            name = p.get("名称", "").strip()
            if not name:
                continue
            is_active = p.get("使用スイッチ", "") != "いいえ"
            _, created = AreaPrefecture.objects.update_or_create(
                name=name,
                defaults={
                    "is_active": is_active,
                },
            )
            prefecture_count += 1
            self.stdout.write(
                f"  {'Created' if created else 'Updated'} prefecture: {name}"
            )

        self.stdout.write(
            self.style.SUCCESS(f"Prefectures: {prefecture_count}")
        )

        # 2. Cities
        city_path = os.path.join(data_dir, "area_city_data.json")
        with open(city_path, encoding="utf-8") as f:
            cities = json.load(f)

        city_count = 0
        for c in cities:
            name = c.get("名称", "").strip()
            unique_id = c.get("unique id", "").strip()
            parent_name = c.get("親", "").strip()
            number_raw = c.get("番号", "")
            is_active = c.get("表示スイッチ", "") == "はい"

            if not name:
                continue

            try:
                prefecture = AreaPrefecture.objects.get(name=parent_name)
            except AreaPrefecture.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(
                        f"  Skipping city '{name}': prefecture '{parent_name}' not found"
                    )
                )
                continue

            defaults = {
                "prefecture": prefecture,
                "name": name,
                "is_active": is_active,
            }
            if number_raw:
                try:
                    defaults["number"] = int(number_raw)
                except ValueError:
                    pass

            if unique_id:
                _, created = AreaCity.objects.update_or_create(
                    unique_id=unique_id,
                    defaults=defaults,
                )
            else:
                _, created = AreaCity.objects.update_or_create(
                    prefecture=prefecture,
                    name=name,
                    defaults=defaults,
                )
            city_count += 1
            self.stdout.write(
                f"  {'Created' if created else 'Updated'} city: {name}"
            )

        self.stdout.write(self.style.SUCCESS(f"Cities: {city_count}"))

        # 3. Places
        place_path = os.path.join(data_dir, "area_place_data.json")
        with open(place_path, encoding="utf-8") as f:
            places = json.load(f)

        # Build a lookup of cities by unique_id for fast binding
        city_lookup = {
            c.unique_id: c
            for c in AreaCity.objects.all()
            if c.unique_id
        }

        place_created = 0
        place_updated = 0
        place_skipped = 0

        for p in places:
            name = p.get("名称2", "").strip()
            if not name:
                place_skipped += 1
                continue

            # The "親" / "親8" key links a place to its parent city via the city's unique_id
            parent_uid = p.get("親") or p.get("親8")
            if not parent_uid:
                place_skipped += 1
                continue

            city = city_lookup.get(parent_uid)
            if not city:
                place_skipped += 1
                continue

            total = int(p.get("世帯数1", 0) or 0)
            detached = int(p.get("戸建3", 0) or 0)
            collective = int(p.get("集合6", 0) or 0)
            distance = int(p.get("予想距離", 0) or 0)
            is_active = p.get("表示スイッチ7", "") == "はい"
            details = p.get("詳細5", "")
            map_url = p.get("地図URL", "")

            defaults = {
                "city": city,
                "name": name,
                "total_households": total,
                "detached_households": detached,
                "collective_households": collective,
                "distance_m": distance,
                "is_active": is_active,
                "details": details,
                "map_url": map_url,
            }

            number_raw = p.get("番号4", "")
            if number_raw:
                try:
                    defaults["number"] = int(number_raw)
                except ValueError:
                    pass

            place_uid = p.get("unique id", "").strip()
            if place_uid:
                defaults["unique_id"] = place_uid
                obj, created = AreaPlace.objects.update_or_create(
                    unique_id=place_uid,
                    defaults=defaults,
                )
            else:
                obj, created = AreaPlace.objects.update_or_create(
                    city=city,
                    name=name,
                    defaults=defaults,
                )
            if created:
                place_created += 1
            else:
                place_updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Places: {place_created} created, {place_updated} updated, "
                f"{place_skipped} skipped (missing city reference)"
            )
        )
