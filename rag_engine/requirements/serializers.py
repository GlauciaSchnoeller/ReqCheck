from rest_framework import serializers

from rag_engine.requirements.convert_requirement import embed_requirement_text
from rag_engine.requirements.models import Requirement


class RequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Requirement
        fields = "__all__"

    def create(self, validated_data):
        text = validated_data["text"]
        embedding = embed_requirement_text(text)
        validated_data["embedding"] = embedding
        return super().create(validated_data)
