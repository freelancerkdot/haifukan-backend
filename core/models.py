import uuid
from decimal import Decimal, ROUND_HALF_UP

from django.conf import settings
from django.db import models
from django.utils.text import slugify


def _round_half_up(value, ndigits=0):
    """Japanese 四捨五入 (ROUND_HALF_UP)."""
    d = Decimal(str(float(value)))
    if ndigits == 0:
        return int(d.quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    exp = Decimal("0.01") if ndigits == 2 else Decimal("0.1")
    return d.quantize(exp, rounding=ROUND_HALF_UP)


class AreaPrefecture(models.Model):
    """A top-level region, e.g. 東京都 (Tokyo)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    name_en = models.CharField(max_length=100, blank=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    is_active = models.BooleanField(default=True)
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
    unique_id = models.CharField(max_length=100, unique=True, blank=True)
    number = models.PositiveIntegerField(null=True, blank=True)
    name = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100, blank=True)
    slug = models.SlugField(max_length=120, blank=True)
    is_active = models.BooleanField(default=True)
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
    unique_id = models.CharField(max_length=100, unique=True, blank=True)
    number = models.PositiveIntegerField(null=True, blank=True)
    name = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100, blank=True)
    slug = models.SlugField(max_length=120, blank=True)
    details = models.TextField(blank=True)
    map_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)

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
        verbose_name = "Area Place"
        verbose_name_plural = "Area Places"

    def calculate_estimates(self):
        """Populate derived fields from distance_m and household counts."""
        total = self.total_households
        distance = self.distance_m

        if not total or not distance:
            self.duration_minutes = 0
            self.duration_minutes_alt = None
            self.estimated_price_yen = 0
            self.estimated_price_yen_alt = None
            self.unit_price_yen = Decimal("0")
            self.unit_price_yen_alt = None
            return

        # Duration (minutes) – 四捨五入
        self.duration_minutes = _round_half_up(
            (distance * 1 + total * 5) / 60
        )
        self.duration_minutes_alt = _round_half_up(
            (distance * 1 + total * 0.7 * 5) / 60
        )

        # Price (yen) – 四捨五入
        self.estimated_price_yen = _round_half_up(
            1350 * self.duration_minutes / 60
        )
        self.estimated_price_yen_alt = _round_half_up(
            1350 * self.duration_minutes_alt / 60
        )

        # Unit price (yen) – 2-decimal 四捨五入
        self.unit_price_yen = _round_half_up(
            self.estimated_price_yen / total, ndigits=2
        )
        self.unit_price_yen_alt = _round_half_up(
            self.estimated_price_yen_alt / (total * 0.7), ndigits=2
        )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name_en or self.name, allow_unicode=True)
        self.calculate_estimates()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.city}{self.name}"


class ProhibitedProperty(models.Model):
    """A property where flyer distribution is prohibited, registered by a client."""

    IMPRESSION_CHOICES = [
        ("kind", "優しい"),
        ("usual", "普通"),
        ("scared", "怖い"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    address = models.CharField(max_length=255)
    tag_name = models.CharField(max_length=255, blank=True)
    impression = models.CharField(max_length=20, choices=IMPRESSION_CHOICES)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="prohibited_properties",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "prohibited_property"
        ordering = ["-created_at"]
        verbose_name = "Prohibited Property"
        verbose_name_plural = "Prohibited Properties"

    def __str__(self):
        return self.address
