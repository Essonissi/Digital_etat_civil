from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
from .views import choisir_localisation, verifier_email
from comptes.views import quartiers_par_commune


urlpatterns = [
    path('dashboard/superadmin/', views.superadmin_dashboard, name='superadmin_dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/operateur/', views.operateur_dashboard, name='operateur_dashboard'),
    path('dashboard/agent/', views.agent_dashboard, name='agent_dashboard'),
    path('dashboard/', views.citoyen_dashboard, name='citoyen_dashboard'),
    path('login/', views.login_view, name='login'),
    path('citoyen_login/', views.citoyen_login_view, name='citoyen_login'),
    path('citoyen_signup/', views.citoyen_register_view, name='citoyen_signup'),
    path('creer-utilisateur/', views.create_agent_or_operateur, name='creer_utilisateur'),
    path('agents/', views.liste_agents, name='liste_agents'),
    path('operateurs/', views.liste_operateurs, name='liste_operateurs'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),  # Pour les pros/admins
    path('citoyen_logout/', LogoutView.as_view(next_page='citoyen_login'), name='citoyen_logout'),  # Pour les citoyens
    path('modifier/<int:user_id>/', views.modifier_utilisateur, name='modifier_utilisateur'),
    path('toggle/<int:user_id>/', views.toggle_utilisateur, name='toggle_utilisateur'),
    path('changer-mot-de-passe/', views.force_password_change, name='force_password_change'),
    path('choisir-localisation/', choisir_localisation, name='choisir_localisation'),
    path('ajax/quartiers/', quartiers_par_commune, name='ajax_quartiers'),
    path('verifier-email/<uidb64>/<token>/', verifier_email, name='verifier_email'),



]
