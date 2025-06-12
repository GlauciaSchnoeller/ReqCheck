from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import BusinessVisions
from .serializers import BusinessVisionsSerializer


class BusinessVisionsViewSet(viewsets.ModelViewSet):
    queryset = BusinessVisions.objects.all().order_by("-create_date")
    serializer_class = BusinessVisionsSerializer

    @action(detail=False, methods=["post"], url_path="upload")
    def upload_business_vision(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
