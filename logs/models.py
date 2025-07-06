from django.db import models
from django.conf import settings


class Log(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    action = models.TextField()
    date_action = models.DateTimeField(auto_now_add=True)