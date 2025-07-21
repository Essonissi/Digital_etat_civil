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
    date_demande = models.DateTimeField(null=True)
    
    def save(self, *args, **kwargs):
        if not self.date_demande and self.demande:
            self.date_demande = self.demande.date_demande  # suppose que Demande a un champ date_demande
        super().save(*args, **kwargs)