from rest_framework import serializers

from .models import AppLogo, SidebarMenuItem


class SidebarMenuItemSerializer(serializers.ModelSerializer):
    """Serializes a sidebar menu item.

    ``image`` returns an absolute URL when a request is available in the
    serializer context (DRF viewsets provide this automatically).
    """

    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = SidebarMenuItem
        fields = [
            "id",
            "label",
            "href",
            "link_type",
            "icon",
            "image",
            "order",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class AppLogoSerializer(serializers.ModelSerializer):
    """Serializes the app/navbar logo. ``image`` is returned as an absolute
    URL when a request is present in the serializer context."""

    image = serializers.ImageField(required=True)

    class Meta:
        model = AppLogo
        fields = ["id", "image", "alt", "is_active", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
