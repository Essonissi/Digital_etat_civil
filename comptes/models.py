# comptes/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('superadmin', 'Super Administrateur'),
        ('admin', 'Administrateur métier'),
        ('agent', 'Agent'),
        ('operateur', 'Opérateur'),
        ('citoyen', 'Citoyen'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='agent')

    def save(self, *args, **kwargs):
        # Si superuser, on garde is_superuser et is_staff à True
        if self.is_superuser:
            self.is_staff = True
            self.role = 'superadmin'
        else:
            # Pour le rôle admin (pas superuser), on active is_staff
            if self.role == 'admin':
                self.is_staff = True
                self.is_superuser = False
            else:
                # Agents et opérateurs : accès admin pas possible (is_staff), mais pas superuser
                self.is_staff = False
                self.is_superuser = False
        super().save(*args, **kwargs)
