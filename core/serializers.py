from rest_framework import serializers

from .models import AreaPrefecture, AreaCity, AreaPlace, ProhibitedProperty


class AreaPrefectureSerializer(serializers.ModelSerializer):
    class Meta:
        model = AreaPrefecture
        fields = ["id", "name", "name_en", "slug"]
        read_only_fields = fields


class AreaCitySerializer(serializers.ModelSerializer):
    class Meta:
        model = AreaCity
        fields = ["id", "name", "name_en", "slug", "prefecture"]
        read_only_fields = fields


class AreaPlaceSerializer(serializers.ModelSerializer):
    city_name = serializers.CharField(source="city.name", read_only=True)
    prefecture_name = serializers.CharField(source="city.prefecture.name", read_only=True)

    class Meta:
        model = AreaPlace
        fields = [
            "id",
            "name",
            "name_en",
            "slug",
            "number",
            "details",
            "map_url",
            "total_households",
            "collective_households",
            "detached_households",
            "distance_m",
            "duration_minutes",
            "duration_minutes_alt",
            "estimated_price_yen",
            "estimated_price_yen_alt",
            "unit_price_yen",
            "unit_price_yen_alt",
            "city",
            "city_name",
            "prefecture_name",
        ]
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
