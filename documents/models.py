from django.db import models
from communes.models import Commune

class Document(models.Model):
    type = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.type

class PieceRequise(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    libelle_piece = models.CharField(max_length=100)
    commune = models.ForeignKey(Commune, on_delete=models.CASCADE)
