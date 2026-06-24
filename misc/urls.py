from rest_framework.routers import DefaultRouter

from .views import BoardPostViewSet, InquiryViewSet

router = DefaultRouter()
router.register("inquiries", InquiryViewSet, basename="inquiry")
router.register("board-posts", BoardPostViewSet, basename="board-post")

urlpatterns = [
    *router.urls,
]
