from django.db.models import Count, Q

from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import AreaPrefecture, AreaCity, AreaPlace, ProhibitedProperty
from .serializers import AreaPrefectureSerializer, AreaCitySerializer, AreaPlaceSerializer, ProhibitedPropertySerializer


class AreaPrefectureViewSet(viewsets.ReadOnlyModelViewSet):
    """Public read-only list of area prefectures for the unit-price page."""

    queryset = AreaPrefecture.objects.all()
    serializer_class = AreaPrefectureSerializer
    permission_classes = [AllowAny]


class AreaCityViewSet(viewsets.ReadOnlyModelViewSet):
    """Public read-only list of area cities, filterable by prefecture.

    Only returns cities that have at least one AreaPlace with a non-zero distance_m.
    """

    serializer_class = AreaCitySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = AreaCity.objects.annotate(
            valid_place_count=Count("places", filter=Q(places__distance_m__gt=0))
        ).filter(valid_place_count__gt=0)

        prefecture_id = self.request.query_params.get("prefecture")
        if prefecture_id:
            queryset = queryset.filter(prefecture__id=prefecture_id)
        return queryset.select_related("prefecture")


class AreaPlaceViewSet(viewsets.ReadOnlyModelViewSet):
    """Public read-only list of area places, filterable by city.

    Only returns places with a non-zero distance_m.
    """

    serializer_class = AreaPlaceSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = AreaPlace.objects.filter(distance_m__gt=0)
        city_id = self.request.query_params.get("city")
        if city_id:
            queryset = queryset.filter(city__id=city_id)
        return queryset.select_related("city", "city__prefecture")


class ProhibitedPropertyViewSet(viewsets.ModelViewSet):
    """Client-only registration of prohibited properties."""

    serializer_class = ProhibitedPropertySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Users only see the properties they registered.
        return ProhibitedProperty.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        profile = getattr(self.request.user, "profile", None)
        if profile is None or profile.role != "client":
            raise PermissionDenied("クライアントのみ可能です")
        serializer.save(created_by=self.request.user)
