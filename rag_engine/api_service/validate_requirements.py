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


def validate_requirement_with_combined_rag(text, project_id, top_k=3):
    embedding = embed_requirement_text(text)

    business_chunks = (
        PDFChunk.objects.filter(file__businessvision__project_id=project_id)
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

        Respond with:

        Is it consistent?

        Is it complete?

        Is it clear (unambiguous)?

        Respond with:
        Consistency: [Yes/No]
        Completeness: [Yes/No]
        Ambiguity: [Yes/No]
        Notes: [explanations if there are any issues]
        """

    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={"model": "llama3", "prompt": prompt, "stream": False},
            timeout=30,
        )
        response.raise_for_status()
        return response.json().get("response", "[Erro: answer not found]")
    except requests.RequestException as e:
        return f"[Error querying model: {e}]"
