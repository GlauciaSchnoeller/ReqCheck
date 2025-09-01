from django.urls import include, path
from rest_framework.routers import DefaultRouter

from rag_engine.requirements.views import (
    BatchRequirementValidationView,
    CsrfTokenView,
    IndividualRequirementValidationView,
    RequirementViewSet,
)

router = DefaultRouter()
router.register(r"requirements", RequirementViewSet, basename="requirement")

urlpatterns = [
    path("csrf-token/", CsrfTokenView.as_view(), name="csrf-token"),
    path(
        "requirements/validate/",
        IndividualRequirementValidationView.as_view(),
        name="validate-requirement",
    ),
    path(
        "requirements/validate_all/",
        BatchRequirementValidationView.as_view(),
        name="validate-all-requirements",
    ),
    path("", include(router.urls)),
]
