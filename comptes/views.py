from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from comptes.decorators import role_required
from django.shortcuts import render, redirect
from rest_framework import viewsets
from django.conf import settings
from comptes.models import CustomUser as User
from .serializers import UserSerializer

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
            first_name=first_name
        )
        user.role = 'citoyen'
        user.telephone = telephone  # si ce champ existe dans ton modèle
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
    return render(request, 'dashboards/dashboard_base.html')

@login_required
@role_required(['agent'])
def agent_dashboard(request):
    return render(request, 'dashboards/dashboard_base.html')

@login_required
@role_required(['citoyen'])
def citoyen_dashboard(request):
    return render(request, 'dashboards/dashboard_base.html')