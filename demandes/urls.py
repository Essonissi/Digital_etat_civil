from django.urls import path
from .views import nouvelle_demande
from demandes import views as demandes_views



urlpatterns = [
    path('nouvelle/', nouvelle_demande, name='nouvelle_demande'),
    path('demande/<int:demande_id>/', demandes_views.detail_demande, name='detail_demande'),
    path('demande/<int:demande_id>/supprimer/', demandes_views.supprimer_demande, name='supprimer_demande'),
]
