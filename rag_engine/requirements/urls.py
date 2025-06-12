from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CsrfTokenView, RequirementViewSet

router = DefaultRouter()
router.register(r"requirements", RequirementViewSet, basename="requirement")

urlpatterns = [
    path("csrf-token/", CsrfTokenView.as_view(), name="csrf-token"),
    path("", include(router.urls)),
]
