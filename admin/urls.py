from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import AppLogoView, FaqItemViewSet, SidebarMenuItemViewSet

router = DefaultRouter()
router.register("sidebar-items", SidebarMenuItemViewSet, basename="sidebar-item")
router.register("faq", FaqItemViewSet, basename="faq-item")

urlpatterns = [
    path("logo/", AppLogoView.as_view(), name="app-logo"),
    *router.urls,
]
