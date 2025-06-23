from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from rag_engine.business_visions.models import BusinessVision
from rag_engine.business_visions.process_pdf import process_pdf_and_store
from rag_engine.business_visions.serializers import BusinessVisionSerializer


class BusinessVisionViewSet(viewsets.ModelViewSet):
    serializer_class = BusinessVisionSerializer
    parser_classes = [MultiPartParser]

    def get_queryset(self):
        queryset = BusinessVision.objects.all().order_by("-create_date")
        id = self.request.query_params.get("id")
        project = self.request.query_params.get("project")

        if id is not None:
            queryset = queryset.filter(id=id)
        if project is not None:
            queryset = queryset.filter(project=project)

        return queryset

    @action(detail=False, methods=["post"], url_path="upload")
    def upload_business_vision(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            instance = serializer.instance
            process_pdf_and_store(instance.pdf.path, instance.pdf)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
