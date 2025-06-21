from django.conf import settings
from langchain_huggingface import HuggingFaceEmbeddings

embedding_model = HuggingFaceEmbeddings(
    model_name=getattr(settings, "EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")
)


def embed_text(text: str):
    """
    Generate embedding from a single string (1 vector)
    """
    return embedding_model.embed_query(text)


def embed_texts(texts: list[str]):
    """
    Generate embeddings of multiple texts at once (list of vectors)
    """
    return embedding_model.embed_documents(texts)
