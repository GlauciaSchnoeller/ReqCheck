from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import UnstructuredFileLoader
from langchain_huggingface import HuggingFaceEmbeddings

from .models import PDFChunk

embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")


def process_pdf_and_store(file_path, django_file_obj):
    loader = UnstructuredFileLoader(file_path)
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(docs)

    texts = [chunk.page_content for chunk in chunks]
    embeddings = embedding_model.embed_documents(texts)

    for text, vector in zip(texts, embeddings):
        PDFChunk.objects.create(file=django_file_obj, chunk_text=text, embedding=vector)
