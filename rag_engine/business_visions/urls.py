from rest_framework.routers import DefaultRouter

from .views import BusinessVisionsViewSet

router = DefaultRouter()
router.register(r"business-visions", BusinessVisionsViewSet)

urlpatterns = router.urls
