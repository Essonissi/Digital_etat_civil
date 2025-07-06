from rest_framework import serializers
from .models import Document, PieceRequise

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = '__all__'

class PieceRequiseSerializer(serializers.ModelSerializer):
    class Meta:
        model = PieceRequise
        fields = '__all__'