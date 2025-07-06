from django.db import models

class Commune(models.Model):
    nom = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    departement = models.CharField(max_length=100)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.nom

class Mairie(models.Model):
    nom = models.CharField(max_length=100)
    adresse = models.TextField()
    commune = models.ForeignKey(Commune, on_delete=models.CASCADE)

    def __str__(self):
        return self.nom
