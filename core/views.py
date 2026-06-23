from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from .models import AreaPrefecture
from .serializers import AreaPrefectureSerializer


class AreaPrefectureViewSet(viewsets.ReadOnlyModelViewSet):
    """Public read-only list of area prefectures for the unit-price page."""

    queryset = AreaPrefecture.objects.all()
    serializer_class = AreaPrefectureSerializer
    permission_classes = [AllowAny]
