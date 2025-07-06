from django.db import models
from demandes.models import Demande

class Fichier(models.Model):
    TYPE_CHOICES = [
        ('justificatif', 'Justificatif'),
        ('pdf_final', 'PDF Final')
    ]
    nom_fichier = models.CharField(max_length=255)
    chemin = models.TextField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    demande = models.ForeignKey(Demande, on_delete=models.CASCADE, related_name='fichiers')