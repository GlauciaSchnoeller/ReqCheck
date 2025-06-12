from django.db import models


class Requirement(models.Model):
    text = models.TextField()
    create_date = models.DateTimeField(auto_now_add=True)
