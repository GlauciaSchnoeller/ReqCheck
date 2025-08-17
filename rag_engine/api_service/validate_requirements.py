import json

import requests
from django.db.models import F
from pgvector.django import CosineDistance

from rag_engine.api_service.settings import OLLAMA_URL
from rag_engine.business_visions.models import PDFChunk
from rag_engine.requirements.convert_requirement import embed_requirement_text
from rag_engine.requirements.models import Requirement


def find_similar_requirements(text, project_id, top_k=5):
    embedding = embed_requirement_text(text)

    return (
        Requirement.objects.filter(project_id=project_id)
        .annotate(distance=CosineDistance(F("embedding"), embedding))
        .order_by("distance")[:top_k]
    )


def parse_validation_response(response_text):
    try:
        data = json.loads(response_text)
        return {
            "consistency": data.get("consistency", "Unknown"),
            "completeness": data.get("completeness", "Unknown"),
            "ambiguity": data.get("ambiguity", "Unknown"),
            "notes": data.get("notes", ""),
        }
    except json.JSONDecodeError:
        return {
            "consistency": "Unknown",
            "completeness": "Unknown",
            "ambiguity": "Unknown",
            "notes": f"Failed to parse model response: {response_text}",
        }


def validate_requirement_with_combined_rag(text, project_id, top_k=3):
    embedding = embed_requirement_text(text)

    business_chunks = (
        PDFChunk.objects.filter(business_vision__project_id=project_id)
        .annotate(distance=CosineDistance(F("embedding"), embedding))
        .order_by("distance")[:top_k]
    )
    business_context = "\n\n".join(c.chunk_text for c in business_chunks)

    previous_reqs = (
        Requirement.objects.filter(project_id=project_id)
        .annotate(distance=CosineDistance(F("embedding"), embedding))
        .order_by("distance")[:top_k]
    )
    requirements_context = "\n\n".join(r.text for r in previous_reqs)

    prompt = f"""
        You are a requirements analyst.

        Use the context below to evaluate the new requirement.

        Business Vision Context:
        {business_context}

        Previous Requirements Context:
        {requirements_context}

        New Requirement:
        "{text}"

        Respond **exactly** in the following JSON format, without any extra text:

        {
        "consistency": "Yes" or "No",
        "completeness": "Yes" or "No",
        "ambiguity": "Yes" or "No",
        "notes": "Any explanatory text or empty string if none"
        }
        """

    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={"model": "llama3", "prompt": prompt, "stream": True},
            timeout=300,
            stream=True,
        )

        raw_response = ""
        for line in response.iter_lines():
            if line:
                data = json.loads(line.decode("utf-8"))
                if data.get("type") == "response":
                    raw_response += data.get("response", "")

        return parse_validation_response(raw_response)

    except requests.RequestException as e:
        return {
            "consistency": "Unknown",
            "completeness": "Unknown",
            "ambiguity": "Unknown",
            "notes": f"Error querying model: {e}",
        }
