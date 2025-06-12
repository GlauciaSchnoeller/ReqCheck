from rest_framework import serializers

from .models import BusinessVisions


class BusinessVisionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessVisions
        fields = ["id", "pdf", "create_date"]
        read_only_fields = ["id", "create_date"]
