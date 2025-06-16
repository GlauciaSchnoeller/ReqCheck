from django.db import models


class Project(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_in = models.DateTimeField(auto_now_add=True)
