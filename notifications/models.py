# notifications/models.py
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Notification(models.Model):
    TYPE_CHOICES = [
        ('info', 'Information'),
        ('success', 'Succès'),
        ('warning', 'Avertissement'),
        ('error', 'Erreur'),
        ('document', 'Document'),
        ('system', 'Système'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Faible'),
        ('normal', 'Normal'),
        ('high', 'Élevée'),
        ('urgent', 'Urgent'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    titre = models.CharField(max_length=200)
    message = models.TextField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='info')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')
    
    # États
    lu = models.BooleanField(default=False)
    archive = models.BooleanField(default=False)
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True)
    date_lecture = models.DateTimeField(null=True, blank=True)
    
    # Données additionnelles (optionnel)
    data = models.JSONField(default=dict, blank=True)  # Pour stocker des infos supplémentaires
    
    # Action/URL liée (optionnel)
    action_url = models.CharField(max_length=500, blank=True)
    action_label = models.CharField(max_length=100, blank=True)
    
    class Meta:
        ordering = ['-date_creation']
        indexes = [
            models.Index(fields=['user', 'lu']),
            models.Index(fields=['user', 'archive']),
            models.Index(fields=['date_creation']),
        ]

    def __str__(self):
        user_str = getattr(self.user, 'username', str(self.user))
        return f"{self.titre} - {user_str}"

    @property
    def is_urgent(self):
        return self.priority in ['high', 'urgent']