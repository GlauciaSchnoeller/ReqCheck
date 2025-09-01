from django.contrib import admin

from rag_engine.business_visions.models import BusinessVision, PDFChunk

admin.site.register(BusinessVision)
admin.site.register(PDFChunk)
