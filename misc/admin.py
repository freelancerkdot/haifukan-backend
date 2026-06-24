from django.contrib import admin

from .models import BoardPost, Inquiry


@admin.register(BoardPost)
class BoardPostAdmin(admin.ModelAdmin):
    list_display = ("posted_date", "content", "is_active", "created_by", "created_at")
    list_filter = ("is_active", "posted_date")
    search_fields = ("content",)
    ordering = ("-posted_date", "-created_at")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ("email", "subject", "is_submitted", "is_verified", "created_at")
    list_filter = ("subject", "is_submitted", "is_verified")
    search_fields = ("email", "content")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")
