from django.contrib import admin

from .models import AreaPrefecture, AreaCity, AreaPlace, ProhibitedProperty


class AreaCityInline(admin.TabularInline):
    model = AreaCity
    extra = 0


class AreaPlaceInline(admin.TabularInline):
    model = AreaPlace
    extra = 0


@admin.register(AreaPrefecture)
class AreaPrefectureAdmin(admin.ModelAdmin):
    list_display = ("name", "name_en", "slug")
    search_fields = ("name", "name_en")
    prepopulated_fields = {"slug": ("name_en",)}
    inlines = [AreaCityInline]


@admin.register(AreaCity)
class AreaCityAdmin(admin.ModelAdmin):
    list_display = ("name", "name_en", "prefecture")
    list_filter = ("prefecture",)
    search_fields = ("name", "name_en")
    autocomplete_fields = ("prefecture",)
    inlines = [AreaPlaceInline]


@admin.register(AreaPlace)
class AreaPlaceAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "city",
        "total_households",
        "distance_m",
        "duration_minutes",
        "estimated_price_yen",
        "unit_price_yen",
    )
    list_filter = ("city__prefecture", "city")
    search_fields = ("name", "name_en")
    autocomplete_fields = ("city",)


@admin.register(ProhibitedProperty)
class ProhibitedPropertyAdmin(admin.ModelAdmin):
    list_display = ("address", "tag_name", "impression", "created_by", "created_at")
    list_filter = ("impression",)
    search_fields = ("address", "tag_name")
    raw_id_fields = ("created_by",)
