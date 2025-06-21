from django.db import models
from pgvector.django import VectorField
from projects.models import Project


class Requirement(models.Model):
    text = models.TextField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="requirements")
    create_date = models.DateTimeField(auto_now_add=True)
    embedding = VectorField(dimensions=384, null=True)
