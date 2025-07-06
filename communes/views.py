from rest_framework import viewsets
from .models import Commune, Mairie
from .serializers import CommuneSerializer, MairieSerializer

class CommuneViewSet(viewsets.ModelViewSet):
    queryset = Commune.objects.all()
    serializer_class = CommuneSerializer

class MairieViewSet(viewsets.ModelViewSet):
    queryset = Mairie.objects.all()
    serializer_class = MairieSerializer