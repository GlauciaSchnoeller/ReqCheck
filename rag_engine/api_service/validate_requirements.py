import json
import re

import requests
from django.db.models import F
from pgvector.django import CosineDistance

from rag_engine.api_service.settings import OLLAMA_URL
from rag_engine.business_visions.models import PDFChunk
from rag_engine.requirements.convert_requirement import embed_requirement_text
from rag_engine.requirements.models import Requirement


def parse_validation_response(data):
    try:
        if isinstance(data, str):
            data = json.loads(data)

        raw_inner = data.get("response", "{}")

        if isinstance(raw_inner, dict):
            inner = raw_inner
        else:
            raw_inner = raw_inner.strip()

            try:
                inner = json.loads(raw_inner)
            except json.JSONDecodeError:
                match = re.search(r"\{.*\}", raw_inner, re.DOTALL)
                if match:
                    inner = json.loads(match.group(0))
                else:
                    raise

        return {
            "consistency": inner.get("consistency", "Not evaluated"),
            "completeness": inner.get("completeness", "Not evaluated"),
            "ambiguity": inner.get("ambiguity", "Not evaluated"),
            "notes": inner.get("notes") or "No notes provided",
        }

    except Exception as e:
        return {
            "consistency": "Not evaluated",
            "completeness": "Not evaluated",
            "ambiguity": "Not evaluated",
            "notes": f"Failed to parse model response: {e}",
        }


def _call_model(prompt):
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={"model": "llama3", "prompt": prompt, "stream": False},
            timeout=300,
        )
        data = response.json()
        return parse_validation_response(data)

    except requests.RequestException as e:
        return {
            "consistency": "Unknown",
            "completeness": "Unknown",
            "ambiguity": "Unknown",
            "notes": f"Error querying model: {e}",
        }


def validate_individual(text, project_id, top_k=3):
    """
    Quick validation for an individual requirement.
    Uses only top-k similar requirements.
    The full business view is NOT used here.
    """
    embedding = embed_requirement_text(text)

    # Search for the top_k most similar requirements
    similar_reqs = (
        Requirement.objects.filter(project_id=project_id)
        .annotate(distance=CosineDistance(F("embedding"), embedding))
        .order_by("distance")[:top_k]
    )
    requirements_context = "\n\n".join(r.text for r in similar_reqs)

    prompt = f"""
    You are a requirements analyst.

    Strictly output a valid JSON object. Do not add explanations, notes before or after.
    Return only the JSON.

    Evaluate the requirement below:

    Context:
    {requirements_context}

    Requirement:
    "{text}"

    JSON format:
    {{
    "consistency": "Yes" or "No",
    "completeness": "Yes" or "No",
    "ambiguity": "Yes" or "No",
    "notes": "Always include some explanation, or 'No issues found' if nothing to add"
    }}
    """
    return _call_model(prompt)


def validate_batch(requirements, project_id):
    """
    Validation of all project requirements.
    Uses all requirements + complete business vision.
    """
    _ = embed_requirement_text(" ".join(r.text for r in requirements))

    business_chunks = PDFChunk.objects.filter(business_vision__project_id=project_id)
    business_context = "\n\n".join(c.chunk_text for c in business_chunks)

    requirements_context = "\n\n".join(r.text for r in requirements)

    results = []
    for req in requirements:
        prompt = f"""
        You are a requirements analyst.

        Evaluate this requirement using full project context:

        Business Vision Context:
        {business_context}

        All Requirements Context:
        {requirements_context}

        Requirement to evaluate:
        "{req.text}"

        Respond exactly in JSON format:

        {{
        "consistency": "Yes" or "No",
        "completeness": "Yes" or "No",
        "ambiguity": "Yes" or "No",
        "notes": "Any explanatory text or empty string if none"
        }}
    """
        results.append({"id": req.id, "text": req.text, "validation_result": _call_model(prompt)})

    return results
