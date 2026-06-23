from rest_framework.routers import DefaultRouter

from .views import AreaPrefectureViewSet

router = DefaultRouter()
router.register("prefectures", AreaPrefectureViewSet, basename="prefecture")

urlpatterns = [
    *router.urls,
]
