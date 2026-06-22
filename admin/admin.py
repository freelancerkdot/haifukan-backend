from django.contrib import admin
from django.utils.html import format_html

from .models import AppLogo, SidebarMenuItem


@admin.register(SidebarMenuItem)
class SidebarMenuItemAdmin(admin.ModelAdmin):
    list_display = ("order", "label", "href", "link_type", "icon", "preview", "is_active")
    list_display_links = ("label",)
    list_editable = ("order", "link_type", "is_active")
    list_filter = ("link_type", "is_active")
    search_fields = ("label", "href", "icon")
    ordering = ("order", "label")

    @admin.display(description="Image")
    def preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:28px;width:28px;object-fit:contain" />',
                obj.image.url,
            )
        return "-"


@admin.register(AppLogo)
class AppLogoAdmin(admin.ModelAdmin):
    list_display = ("alt", "preview", "is_active", "updated_at")

    @admin.display(description="Logo")
    def preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:32px;width:auto;object-fit:contain" />',
                obj.image.url,
            )
        return "-"
