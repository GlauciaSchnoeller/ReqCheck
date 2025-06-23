from rest_framework import viewsets

from rag_engine.projects.models import Project
from rag_engine.projects.serializers import ProjectSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all().order_by("-created_in")
    serializer_class = ProjectSerializer
