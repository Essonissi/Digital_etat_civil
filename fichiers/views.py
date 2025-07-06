from rest_framework import viewsets
from .models import Fichier
from .serializers import FichierSerializer

class FichierViewSet(viewsets.ModelViewSet):
    queryset = Fichier.objects.all()
    serializer_class = FichierSerializer