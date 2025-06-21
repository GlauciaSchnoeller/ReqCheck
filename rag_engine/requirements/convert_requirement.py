from rag_engine.api_service.embedding import embed_text


def embed_requirement_text(text: str):
    return embed_text(text)
