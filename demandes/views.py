from rest_framework import viewsets
from .models import Demande
from .serializers import DemandeSerializer

class DemandeViewSet(viewsets.ModelViewSet):
    queryset = Demande.objects.all()
    serializer_class = DemandeSerializer