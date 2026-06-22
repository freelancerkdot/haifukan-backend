from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import AppLogoView, SidebarMenuItemViewSet

router = DefaultRouter()
router.register("sidebar-items", SidebarMenuItemViewSet, basename="sidebar-item")

urlpatterns = [
    path("logo/", AppLogoView.as_view(), name="app-logo"),
    *router.urls,
]
