import uuid

from django.db import models


class SidebarMenuItem(models.Model):
    """A dynamic item rendered in the frontend left sidebar.

    Mirrors the static items previously hard-coded on the frontend. Each item
    keeps a *static* ``href`` (routes are fixed), while the ``label``, ``icon``
    and optional ``image`` are managed dynamically through the admin / API.

    If ``image`` is set, the frontend renders the image instead of the
    Lucide ``icon`` glyph.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Display label (Japanese), e.g. 依頼者の皆様へ
    label = models.CharField(max_length=100)

    # Static frontend route, e.g. /for-request
    href = models.CharField(max_length=200)

    # Where the item is rendered on the frontend:
    #   * "menu" -> primary icon menu (top of sidebar)
    #   * "text" -> secondary plain-text links (e.g. /legal, /privacy)
    class LinkType(models.TextChoices):
        MENU = "menu", "Menu"
        TEXT = "text", "Text link"

    link_type = models.CharField(
        max_length=10,
        choices=LinkType.choices,
        default=LinkType.MENU,
    )

    # Lucide icon name (used when no image is uploaded), e.g. "Users"
    icon = models.CharField(
        max_length=50,
        blank=True,
        help_text="Lucide icon name, used when no image is uploaded.",
    )

    # Optional image; when present it is shown instead of the icon.
    image = models.ImageField(
        upload_to="sidebar_icons/",
        blank=True,
        null=True,
    )

    # Lower numbers appear first.
    order = models.PositiveIntegerField(default=0)

    # Toggle visibility without deleting the item.
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "sidebar_menu_item"
        ordering = ["order", "label"]
        verbose_name = "Sidebar Menu Item"
        verbose_name_plural = "Sidebar Menu Items"

    def __str__(self):
        return self.label


class AppLogo(models.Model):
    """The site/navbar logo, managed dynamically.

    Treated as a singleton: the most recently updated active row is served
    as the current logo. Uploading a new image via the API updates this row.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = models.ImageField(upload_to="app_logo/")
    alt = models.CharField(max_length=200, blank=True, default="配布館")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "app_logo"
        ordering = ["-updated_at"]
        verbose_name = "App Logo"
        verbose_name_plural = "App Logo"

    def __str__(self):
        return self.alt or "App Logo"

    @classmethod
    def current(cls):
        """Return the active logo to serve, or None if none exists."""
        return cls.objects.filter(is_active=True).order_by("-updated_at").first()


class FaqItem(models.Model):
    """A dynamic FAQ item rendered on the /question page.

    Previously hard-coded in the frontend; now editable via the admin / API.
    Category headers are represented by rows with empty question/answer.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Category name (e.g. 配布館に関する質問). When question/answer are empty,
    # the frontend renders this as a section header.
    category = models.CharField(max_length=100, blank=True, default="")

    question = models.CharField(max_length=500, blank=True, default="")
    answer = models.TextField(blank=True, default="")

    # Display order; lower numbers appear first.
    order = models.PositiveIntegerField(default=0)

    # Toggle visibility without deleting.
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "faq_item"
        ordering = ["order", "category", "question"]
        verbose_name = "FAQ Item"
        verbose_name_plural = "FAQ Items"

    def __str__(self):
        if self.question:
            return self.question[:60]
        return self.category or "Category header"
