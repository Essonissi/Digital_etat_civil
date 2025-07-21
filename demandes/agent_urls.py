from django.urls import path
from . import views


urlpatterns = [
    path('demandes/', views.liste_demandes, name='liste_demandes'),
    path('demandes/<int:demande_id>/', views.agent_detail_demande, name='detail_demande'),
]