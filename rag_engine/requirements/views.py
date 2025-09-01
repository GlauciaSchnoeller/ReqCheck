from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from rag_engine.api_service.validate_requirements import (
    validate_batch,
    validate_individual,
)
from rag_engine.requirements.models import Requirement
from rag_engine.requirements.serializers import RequirementSerializer


@method_decorator(ensure_csrf_cookie, name="dispatch")
class CsrfTokenView(View):
    def get(self, request, *args, **kwargs):
        return JsonResponse({"message": "CSRF cookie set."})


class RequirementViewSet(viewsets.ModelViewSet):
    serializer_class = RequirementSerializer

    def get_queryset(self):
        queryset = Requirement.objects.all().order_by("-create_date")
        req_id = self.request.query_params.get("id")
        project = self.request.query_params.get("project")

        if req_id is not None:
            queryset = queryset.filter(id=req_id)
        if project is not None:
            queryset = queryset.filter(project=project)

        return queryset


class IndividualRequirementValidationView(APIView):
    """Validação de um único requisito (individual)."""

    def post(self, request):
        requirement_id = request.data.get("requirement_id")
        project_id = request.data.get("project_id")

        if not requirement_id or not project_id:
            return Response(
                {"error": "requirement_id and project_id are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        req = get_object_or_404(Requirement, id=requirement_id)
        validation_result = validate_individual(req.text, project_id)

        return Response({"id": req.id, "text": req.text, "validation_result": validation_result})


class BatchRequirementValidationView(APIView):
    """Validação de todos os requisitos de um projeto (batch)."""

    def post(self, request):
        project_id = request.data.get("project_id")
        if not project_id:
            return Response(
                {"error": "project_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        requirements = Requirement.objects.filter(project_id=project_id)
        validation_results = validate_batch(list(requirements), project_id)

        return Response(validation_results)
