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
    queryset = Requirement.objects.all().order_by("-create_date")
    serializer_class = RequirementSerializer
