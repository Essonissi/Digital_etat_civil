from rest_framework import serializers
from .models import CentreInteret

class CentreInteretSerializer(serializers.ModelSerializer):
    class Meta:
        model = CentreInteret
        fields = '__all__'