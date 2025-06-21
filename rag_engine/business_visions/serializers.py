from rest_framework import serializers

from .models import BusinessVision


class BusinessVisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessVision
        fields = "__all__"
