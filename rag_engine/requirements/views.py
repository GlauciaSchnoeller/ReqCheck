from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import ensure_csrf_cookie
from requests import Response
from rest_framework import viewsets
from rest_framework.views import APIView

from rag_engine.api_service.validate_requirements import validate_requirement_with_combined_rag
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


class RequirementValidationView(APIView):
    def post(self, request):
        project_id = request.data.get("project_id")
        requirement_id = request.data.get("requirement_id")

        if not project_id or not requirement_id:
            return Response({"error": "project_id and requirement_id are required"}, status=400)

        try:
            req = Requirement.objects.get(id=requirement_id, project_id=project_id)
        except Requirement.DoesNotExist:
            return Response({"error": "Requirement not found"}, status=404)

        validation_result = validate_requirement_with_combined_rag(req.text, project_id)

        return Response({"requirement": req.text, "validation_result": validation_result})


class BatchRequirementValidationView(APIView):
    def post(self, request):
        project_id = request.data.get("project_id")
        if not project_id:
            return Response({"error": "project_id is required"}, status=400)

        requirements = Requirement.objects.filter(project_id=project_id)
        results = []

        for req in requirements:
            result = validate_requirement_with_combined_rag(req.text, project_id)
            results.append({"id": req.id, "text": req.text, "validation": result})

        return Response(results)
