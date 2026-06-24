from rest_framework import serializers

from .models import AreaPrefecture, ProhibitedProperty


class AreaPrefectureSerializer(serializers.ModelSerializer):
    class Meta:
        model = AreaPrefecture
        fields = ["id", "name", "name_en", "slug"]
        read_only_fields = fields


class ProhibitedPropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProhibitedProperty
        fields = [
            "id",
            "address",
            "tag_name",
            "impression",
            "created_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_by", "created_at", "updated_at"]
