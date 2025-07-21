from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from comptes.models import Notification

def generate_email_verification_token(user):
    return default_token_generator.make_token(user)

def get_uidb64(user):
    return urlsafe_base64_encode(force_bytes(user.pk))

def notifier_utilisateur(user, message, **kwargs):
    """
    Crée une notification pour l'utilisateur avec un message formaté dynamiquement.
    Utilise les kwargs pour injecter des variables dans le message.
    """
    if kwargs:
        message = message.format(**kwargs)
    Notification.objects.create(user=user, message=message)
