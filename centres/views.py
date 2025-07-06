from rest_framework import viewsets
from .models import CentreInteret
from .serializers import CentreInteretSerializer

class CentreInteretViewSet(viewsets.ModelViewSet):
    queryset = CentreInteret.objects.all()
    serializer_class = CentreInteretSerializer