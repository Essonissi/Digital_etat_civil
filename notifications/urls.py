# notifications/urls.py
from django.contrib.auth import views
from django.urls import path
from .views import notifications_citoyen, marquer_lue, marquer_toutes_lues, archiver_notification



urlpatterns = [
    path('notifications/citoyen/', notifications_citoyen, name='notifications_citoyen'),
    path('marquer-lue/<int:notif_id>/', marquer_lue, name='marquer_notification_lue'),
    path('marquer-toutes-lues/', marquer_toutes_lues, name='marquer_toutes_lues'),
    path('archiver/<int:notif_id>/', archiver_notification, name='archiver_notification'),
]
