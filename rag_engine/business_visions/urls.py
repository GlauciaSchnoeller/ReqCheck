from rest_framework.routers import DefaultRouter

from .views import BusinessVisionViewSet

router = DefaultRouter()
router.register(r"business-visions", BusinessVisionViewSet, basename="businessvision")

urlpatterns = router.urls
