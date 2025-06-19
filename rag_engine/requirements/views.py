from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import viewsets

from .models import Requirement
from .serializers import RequirementSerializer


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
