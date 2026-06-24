from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import AreaPrefecture, ProhibitedProperty
from .serializers import AreaPrefectureSerializer, ProhibitedPropertySerializer


class AreaPrefectureViewSet(viewsets.ReadOnlyModelViewSet):
    """Public read-only list of area prefectures for the unit-price page."""

    queryset = AreaPrefecture.objects.all()
    serializer_class = AreaPrefectureSerializer
    permission_classes = [AllowAny]


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
