from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    path('gestion-pieces/', views.gestion_pieces_requises, name='gestion_pieces'),
    path('ajouter-piece/', views.ajouter_piece, name='ajouter_piece'),
    path('modifier-piece/<int:piece_id>/', views.modifier_piece, name='modifier_piece'),
    path('supprimer-piece/<int:piece_id>/', views.supprimer_piece, name='supprimer_piece'),
    path('ajouter-document/', views.ajouter_document, name='ajouter_document'),
]
