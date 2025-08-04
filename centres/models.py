from django.db import models
from communes.models import Commune, Quartier

class CentreInteret(models.Model):
    TYPE_CHOICES = [
        ('hopital', 'Hôpital'),
        ('ecole', 'École'),
        ('marche', 'Marché'),
        ('autre', 'Autre')
    ]
    nom = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    quartier = models.ForeignKey(Quartier, on_delete=models.SET_NULL, null=True, blank=True)    
    description = models.TextField(blank=True, null=True)
    commune = models.ForeignKey(Commune, on_delete=models.CASCADE)
    latitude = models.FloatField()
    longitude = models.FloatField()
