from django.core.exceptions import ValidationError
from django.db import models
from pgvector.django import VectorField
from PyPDF2 import PdfReader


def validate_pdf(fileobj):
    max_size = 2 * 1024 * 1024
    if fileobj.size > max_size:
        raise ValidationError("Max file size is 2MB.")

    try:
        PdfReader(fileobj)
        fileobj.seek(0)
    except Exception:
        raise ValidationError("Uploaded file is not a valid PDF.")


class BusinessVisions(models.Model):
    pdf = models.FileField(upload_to="documents_pdf", validators=[validate_pdf])
    create_date = models.DateTimeField(auto_now_add=True)


class PDFChunk(models.Model):
    file = models.FileField(upload_to="media/")
    chunk_text = models.TextField()
    embedding = VectorField(dimensions=384)
