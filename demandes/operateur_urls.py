from django.urls import path
from . import views

app_name = 'operateur'

urlpatterns = [
    path('demandes/', views.liste_demandes_operateur, name='liste_demandes'),
    path('demandes/<int:demande_id>/traiter/', views.operateur_traiter_demande, name='traiter_demande'),
    path('demandes/<int:demande_id>/', views.operateur_traiter_demande, name='detail_demande'),  # à adapter si tu as une vue dédiée
] 