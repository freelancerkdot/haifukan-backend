from rest_framework import serializers

from .models import AreaPrefecture


class AreaPrefectureSerializer(serializers.ModelSerializer):
    class Meta:
        model = AreaPrefecture
        fields = ["id", "name", "name_en", "slug"]
        read_only_fields = fields
