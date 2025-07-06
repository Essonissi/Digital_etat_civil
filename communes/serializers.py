from rest_framework import serializers
from .models import Commune, Mairie

class CommuneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Commune
        fields = '__all__'

class MairieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mairie
        fields = '__all__'