from django.contrib import admin

from .models import Inquiry


@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ("email", "subject", "is_submitted", "is_verified", "created_at")
    list_filter = ("subject", "is_submitted", "is_verified")
    search_fields = ("email", "content")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")
