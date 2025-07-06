from rest_framework import viewsets
from .models import Document, PieceRequise
from .serializers import DocumentSerializer, PieceRequiseSerializer

class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

class PieceRequiseViewSet(viewsets.ModelViewSet):
    queryset = PieceRequise.objects.all()
    serializer_class = PieceRequiseSerializer