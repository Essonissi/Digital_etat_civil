from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Import des ViewSets
from comptes.views import UserViewSet
from communes.views import CommuneViewSet, MairieViewSet
from documents.views import DocumentViewSet, PieceRequiseViewSet
from demandes.views import DemandeViewSet
from fichiers.views import FichierViewSet
from centres.views import CentreInteretViewSet
from logs.views import LogViewSet

# Router DRF pour les API REST
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'communes', CommuneViewSet)
router.register(r'mairies', MairieViewSet)
router.register(r'documents', DocumentViewSet)
router.register(r'pieces-requises', PieceRequiseViewSet)
router.register(r'demandes', DemandeViewSet)
router.register(r'fichiers', FichierViewSet)
router.register(r'centres', CentreInteretViewSet)
router.register(r'logs', LogViewSet)

# Toutes les URLs
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),                  # API REST
    path('', include('comptes.urls')),           # Vues login, dashboard, etc.
]
