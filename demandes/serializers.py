from rest_framework import serializers
from .models import Demande
from django.conf import settings

class DemandeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Demande
        fields = '__all__'