from django.db import models
from projects.models import Project


class Requirement(models.Model):
    text = models.TextField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="requirements")
    create_date = models.DateTimeField(auto_now_add=True)
