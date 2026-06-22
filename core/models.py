import uuid

from django.db import models
from django.utils.text import slugify


class AreaPrefecture(models.Model):
    """A top-level region, e.g. 東京都 (Tokyo)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    name_en = models.CharField(max_length=100, blank=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "area_prefecture"
        ordering = ["name"]
        verbose_name = "Area Prefecture"
        verbose_name_plural = "Area Prefectures"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name_en or self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class AreaCity(models.Model):
    """A city/ward inside a prefecture, e.g. 千代田区 (Chiyoda-ku)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    prefecture = models.ForeignKey(
        AreaPrefecture,
        on_delete=models.CASCADE,
        related_name="cities",
    )
    name = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100, blank=True)
    slug = models.SlugField(max_length=120, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "area_city"
        ordering = ["prefecture__name", "name"]
        unique_together = ("prefecture", "name")
        verbose_name = "Area City"
        verbose_name_plural = "Area Cities"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name_en or self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.prefecture.name}{self.name}"


class AreaPlace(models.Model):
    """A specific area/town inside a city, e.g. 隼町 (Hayabusachō).

    Holds the distribution estimate attributes shown on the unit-price page.
    Parenthesised values from the design are stored as the ``*_alt`` fields.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    city = models.ForeignKey(
        AreaCity,
        on_delete=models.CASCADE,
        related_name="places",
    )
    name = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100, blank=True)
    slug = models.SlugField(max_length=120, blank=True)

    # Household counts: total = collective (集合) + detached (戸建)
    total_households = models.PositiveIntegerField(default=0)
    collective_households = models.PositiveIntegerField(default=0)
    detached_households = models.PositiveIntegerField(default=0)

    # Distance to cover the area, in metres (e.g. 1,571m)
    distance_m = models.PositiveIntegerField(default=0)

    # Estimated walking/distribution duration in minutes (53分（45分）)
    duration_minutes = models.PositiveIntegerField(default=0)
    duration_minutes_alt = models.PositiveIntegerField(null=True, blank=True)

    # Estimated total price in yen (1,193円（1,012円）)
    estimated_price_yen = models.PositiveIntegerField(default=0)
    estimated_price_yen_alt = models.PositiveIntegerField(null=True, blank=True)

    # Per-household unit price in yen (@3.7円（4.5円）)
    unit_price_yen = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    unit_price_yen_alt = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "area_place"
        ordering = ["city__name", "name"]
        unique_together = ("city", "name")
        verbose_name = "Area Place"
        verbose_name_plural = "Area Places"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name_en or self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.city}{self.name}"
