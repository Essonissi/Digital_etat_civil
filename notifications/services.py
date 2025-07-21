from .models import Notification

class NotificationService:
    """Service pour créer et gérer les notifications"""
    
    @staticmethod
    def notify_document_status(user, document, status):
        """Notification pour changement de statut de document"""
        messages = {
            'en_attente': 'Votre demande a été reçue et est en cours de traitement',
            'en_cours': 'Votre demande est actuellement en cours de traitement',
            'pret': 'Votre document est prêt à être récupéré',
            'livre': 'Votre document a été livré avec succès',
            'rejete': 'Votre demande a été rejetée'
        }
        
        types = {
            'en_attente': 'info',
            'en_cours': 'info', 
            'pret': 'success',
            'livre': 'success',
            'rejete': 'error'
        }
        
        priorities = {
            'pret': 'high',
            'rejete': 'high',
        }
        
        return Notification.objects.create_notification(
            user=user,
            titre=f"Document {document.type_document} - {status.replace('_', ' ').title()}",
            message=messages.get(status, 'Changement de statut de votre demande'),
            type=types.get(status, 'info'),
            priority=priorities.get(status, 'normal'),
            action_url=f"/citoyen/documents/{document.id}/",
            action_label="Voir le détail",
            data={'document_id': document.id, 'status': status}
        )
    
    @staticmethod
    def notify_system_maintenance(users, start_time, duration):
        """Notification de maintenance système"""
        for user in users:
            Notification.objects.create_notification(
                user=user,
                titre="Maintenance programmée du système",
                message=f"Une maintenance est prévue le {start_time.strftime('%d/%m/%Y à %H:%M')} (durée: {duration}h)",
                type='warning',
                priority='normal'
            )