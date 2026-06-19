from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = "User Profile"


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ["email", "username", "is_email_verified", "is_staff", "is_superuser"]
    list_filter = ["is_email_verified", "is_staff", "is_superuser"]
    search_fields = ["email", "username"]
    ordering = ["email"]

    fieldsets = (
        (None, {"fields": ("email", "username", "password")}),
        ("Personal Info", {"fields": ("first_name", "last_name")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important Dates", {"fields": ("last_login", "date_joined")}),
        ("Email Verification", {"fields": ("is_email_verified", "email_verification_token")}),
    )


admin.site.register(User, UserAdmin)
admin.site.register(UserProfile)
