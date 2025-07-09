from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from comptes.decorators import role_required
from django.shortcuts import render, redirect
from rest_framework import viewsets
from django.conf import settings
from .forms import CreateUserForm
from .models import CustomUser
from comptes.models import CustomUser as User
from .serializers import UserSerializer
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from .models import Quartier, Demande, Commune

# --- API ViewSet ---
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

# --- Vue de connexion pour agents, admins, opérateurs, superadmin ---
def login_view(request):
    error = None
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            if user.role == 'superadmin':
                return redirect('superadmin_dashboard')
            elif user.role == 'admin':
                return redirect('admin_dashboard')
            elif user.role == 'operateur':
                return redirect('operateur_dashboard')
            elif user.role == 'agent':
                return redirect('agent_dashboard')
        else:
            error = "Identifiants invalides"
    return render(request, 'comptes/login.html', {'error': error})

# --- Vue de connexion citoyen ---
def citoyen_login_view(request):
    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        if not username or not password:
            error = "Veuillez remplir tous les champs."
        else:
            user = authenticate(request, username=username, password=password)
            if user is None:
                error = "Nom d'utilisateur ou mot de passe incorrect."
            elif user.role != 'citoyen':
                error = "Accès réservé aux citoyens."
            else:
                login(request, user)
                return redirect('citoyen_dashboard')

    return render(request, 'comptes/citoyen_login.html', {'error': error})

# --- Inscription citoyen ---
def citoyen_register_view(request):
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        last_name = request.POST.get('last_name')
        first_name = request.POST.get('first_name')
        telephone = request.POST.get('telephone')
        sexe = request.POST.get('sexe')

        if password != password2:
            error = "Les mots de passe ne correspondent pas."
            return render(request, 'comptes/citoyen_signup.html', {'error': error})

        if User.objects.filter(username=username).exists():
            error = "Ce nom d'utilisateur existe déjà."
            return render(request, 'comptes/citoyen_signup.html', {'error': error})

        if User.objects.filter(email=email).exists():
            error = "Cet email est déjà utilisé."
            return render(request, 'comptes/citoyen_signup.html', {'error': error})

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            last_name=last_name,
            first_name=first_name,
            sexe=sexe
        )
        user.role = 'citoyen'
        user.telephone = telephone
        user.save()
        return redirect('citoyen_login')

    return render(request, 'comptes/citoyen_signup.html', {'error': error})

# --- Dashboards selon rôle ---
@login_required
@role_required(['superadmin'])
def superadmin_dashboard(request):
    return render(request, 'dashboards/dashboard_base.html')

@login_required
@role_required(['admin'])
def admin_dashboard(request):
    return render(request, 'dashboards/admin/dashboard.html')

@login_required
@role_required(['operateur'])
def operateur_dashboard(request):
    if request.user.must_change_password:
        return redirect('force_password_change')
    return render(request, 'dashboards/operateur/dashboard.html')

@login_required
@role_required(['agent'])
def agent_dashboard(request):
    if request.user.must_change_password:
        return redirect('force_password_change')
    return render(request, 'dashboards/agent/dashboard.html')

@login_required
@role_required(['citoyen'])
def citoyen_dashboard(request):
    return render(request, 'dashboards/dashboard_base.html')

# --- Création des agents et des opérateurs par l'admin ---


@login_required
@role_required(['admin'])

def create_agent_or_operateur(request):
    error = None
    user_type = request.GET.get('type')

    if user_type not in ['agent', 'operateur']:
        return redirect('admin_dashboard')

    quartiers = Quartier.objects.filter(commune=request.user.commune)

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        sexe = request.POST.get('sexe')  
        quartier_id = request.POST.get('quartier') if user_type == 'agent' else None
        quartier = Quartier.objects.get(id=quartier_id) if quartier_id else None

        commune = request.user.commune  # ✅ hérite de l'admin

        if not username or not email or not password or not sexe:
            error = "Tous les champs sont obligatoires."
        elif user_type == 'agent' and not quartier:
            error = "Veuillez sélectionner un quartier pour l'agent."
        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                role=user_type,
                commune=commune,  # ✅ automatiquement affectée
                sexe=sexe,
                quartier=quartier,
                must_change_password=True
            )
            return redirect('liste_agents' if user_type == 'agent' else 'liste_operateurs')

    return render(request, 'comptes/create_user.html', {
        'error': error,
        'user_type': user_type,
        'quartiers': quartiers
    })



# --- les liens pour la liste des opérateurs et agents ---

@login_required
@role_required(['admin'])
def liste_agents(request):
    agents = CustomUser.objects.filter(role='agent')
    return render(request, 'comptes/liste_agents.html', {'agents': agents})

@login_required
@role_required(['admin'])
def liste_operateurs(request):
    operateurs = CustomUser.objects.filter(role='operateur')
    return render(request, 'comptes/liste_operateurs.html', {'operateurs': operateurs})

@login_required
@role_required(['agent'])
def liste_demandes(request):
    demandes = Demande.objects.filter(quartier=request.user.quartier)
    return render(request, 'comptes/liste_demandes.html', {'demandes': demandes})

# --- Vue pour la modification ---
@login_required
@role_required(['admin'])
def modifier_utilisateur(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        user.last_name = request.POST.get('last_name')
        user.first_name = request.POST.get('first_name')
        user.email = request.POST.get('email')
        user.telephone = request.POST.get('telephone')
        user.sexe = request.POST.get('sexe')
        user.save()
        # Redirige selon le rôle
        if user.role == 'agent':
            return redirect('liste_agents')
        else:
            return redirect('liste_operateurs')
    # Pas de GET ici car tout se fait en POST via la modale
    return redirect('liste_operateurs')

@login_required
@role_required(['admin'])
def toggle_utilisateur(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.is_active = not user.is_active
    user.save()
    return redirect('liste_agents')  

@login_required
def force_password_change(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            user.must_change_password = False
            user.save()
            # Redirige vers le dashboard approprié
            if user.role == 'agent':
                return redirect('agent_dashboard')
            elif user.role == 'operateur':
                return redirect('operateur_dashboard')
        else:
            error = "Veuillez corriger les erreurs ci-dessous."
    else:
        form = PasswordChangeForm(request.user)
        error = None
    return render(request, 'comptes/force_password_change.html', {'form': form, 'error': error})
