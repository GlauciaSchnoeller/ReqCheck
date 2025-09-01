from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import UnstructuredFileLoader

from rag_engine.api_service.embedding import embed_texts
from rag_engine.business_visions.models import PDFChunk


def process_pdf_and_store(file_path, django_file_obj):
    loader = UnstructuredFileLoader(file_path)
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(docs)

    texts = [chunk.page_content for chunk in chunks]
    embeddings = embed_texts(texts)

    for text, vector in zip(texts, embeddings):
        PDFChunk.objects.create(file=django_file_obj, chunk_text=text, embedding=vector)
