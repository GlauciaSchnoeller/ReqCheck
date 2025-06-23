from rest_framework import serializers

from rag_engine.business_visions.models import BusinessVision


class BusinessVisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessVision
        fields = "__all__"
