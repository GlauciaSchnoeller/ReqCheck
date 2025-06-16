from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from .models import BusinessVision
from .process_pdf import process_pdf_and_store
from .serializers import BusinessVisionSerializer


class BusinessVisionViewSet(viewsets.ModelViewSet):
    queryset = BusinessVision.objects.all().order_by("-create_date")
    serializer_class = BusinessVisionSerializer
    parser_classes = [MultiPartParser]

    @action(detail=False, methods=["post"], url_path="upload")
    def upload_business_vision(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            instance = serializer.instance
            process_pdf_and_store(instance.file.path, instance.file)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
