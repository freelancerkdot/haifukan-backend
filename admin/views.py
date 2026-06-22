from rest_framework import status, viewsets
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import AppLogo, SidebarMenuItem
from .serializers import AppLogoSerializer, SidebarMenuItemSerializer


class SidebarMenuItemViewSet(viewsets.ModelViewSet):
    """CRUD API for the dynamic frontend sidebar menu items.

    * ``GET`` (list/retrieve) is public so the public site can render the
      sidebar.
    * Write actions are also open here to keep the ``/admin2`` management
      page functional out of the box. Tighten ``get_permissions`` with
      ``IsAuthenticated`` once an admin auth flow is wired into ``/admin2``.
    """

    queryset = SidebarMenuItem.objects.all()
    serializer_class = SidebarMenuItemSerializer
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        qs = super().get_queryset()
        # Public listing only returns active items; management views can pass
        # ?all=true to see everything.
        if self.action == "list" and self.request.query_params.get("all") != "true":
            qs = qs.filter(is_active=True)
        return qs


class AppLogoView(APIView):
    """Read and update the (singleton) app/navbar logo.

    * ``GET``  -> current active logo (or 204 when none is set).
    * ``PUT`` / ``PATCH`` -> upload a new logo image (multipart). Updates the
      existing singleton row, or creates it on first upload.

    Open permissions keep ``/admin2`` functional out of the box; tighten to
    ``IsAuthenticated`` once an admin auth flow exists.
    """

    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        logo = AppLogo.current()
        if not logo:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(AppLogoSerializer(logo, context={"request": request}).data)

    def _upsert(self, request, partial):
        logo = AppLogo.current()
        serializer = AppLogoSerializer(
            instance=logo,
            data=request.data,
            partial=partial,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        return self._upsert(request, partial=False)

    def patch(self, request):
        # When no logo exists yet an image is required, so disallow partial.
        return self._upsert(request, partial=AppLogo.current() is not None)
