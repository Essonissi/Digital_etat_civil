from django.urls import path
from . import views

urlpatterns = [
    path('ajouter/', views.ajouter_centre_interet, name='ajouter_centre_interet'),
    path('liste/', views.liste_centres, name='liste_centres'),
     path('citoyen/liste/', views.liste_centres_citoyen, name='liste_centres_citoyen'),
    path('supprimer/<int:centre_id>/', views.supprimer_centre_interet, name='supprimer_centre_interet'),
    path('modifier/<int:centre_id>/', views.modifier_centre_interet, name='modifier_centre_interet'),
]