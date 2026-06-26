from rest_framework.routers import DefaultRouter

from .views import AreaPrefectureViewSet, AreaCityViewSet, AreaPlaceViewSet, ProhibitedPropertyViewSet

router = DefaultRouter()
router.register("prefectures", AreaPrefectureViewSet, basename="prefecture")
router.register("cities", AreaCityViewSet, basename="city")
router.register("places", AreaPlaceViewSet, basename="place")
router.register(
    "prohibited-properties", ProhibitedPropertyViewSet, basename="prohibited-property"
)

urlpatterns = [
    *router.urls,
]
