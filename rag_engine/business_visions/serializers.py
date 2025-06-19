from rest_framework import serializers

from .models import BusinessVision


class BusinessVisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessVision
        fields = ["id", "pdf", "project", "create_date"]
        read_only_fields = ["id", "create_date"]
