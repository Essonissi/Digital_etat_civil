from django.db import models
from django.utils import timezone

class NotificationManager(models.Manager):
    def unread_for_user(self, user):
        """Récupère les notifications non lues d'un utilisateur"""
        return self.filter(user=user, lu=False, archive=False)
    
    def mark_as_read(self, user, notification_ids=None):
        """Marque une ou plusieurs notifications comme lues"""
        queryset = self.filter(user=user, lu=False)
        if notification_ids:
            queryset = queryset.filter(id__in=notification_ids)
        
        return queryset.update(
            lu=True, 
            date_lecture=timezone.now()
        )
    
    def create_notification(self, user, titre, message, type='info', priority='normal', **kwargs):
        """Méthode helper pour créer une notification"""
        return self.create(
            user=user,
            titre=titre,
            message=message,
            type=type,
            priority=priority,
            **kwargs
        )