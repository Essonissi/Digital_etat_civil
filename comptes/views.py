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
from django.urls import reverse
from django.http import JsonResponse
from communes.models import Quartier
from documents.models import Document, PieceRequise
from demandes.models import Demande
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_decode
from django.http import HttpResponse

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

    User = get_user_model()

def verifier_email(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.email_verifie = True
        user.save()
        return HttpResponse("Email vérifié avec succès !")
    else:
        return HttpResponse("Lien invalide ou expiré.")

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

def envoyer_email_verification(request, user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    lien = request.build_absolute_uri(reverse('verifier_email', args=[uid, token]))
    
    message = f"Bonjour {user.username},\n\nCliquez sur ce lien pour confirmer votre adresse email : {lien}"
    send_mail(
        "Confirmation de votre adresse email",
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False
    )

@login_required
def choisir_localisation(request):
    communes = Commune.objects.all()

    if request.method == 'POST':
        commune_id = request.POST.get('commune')
        quartier_id = request.POST.get('quartier')

        request.user.commune_id = commune_id
        request.user.quartier_id = quartier_id
        request.user.save()

        return redirect('nouvelle_demande')  # Redirige vers la page de demande

    return render(request, 'citoyen/choisir_localisation.html', {
        'communes': communes
    })


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
    # SUPPRIMER cette ligne :
    # if not request.user.commune or not request.user.quartier:
    #     return redirect('choisir_localisation')

    # Liste des documents disponibles
    documents = Document.objects.all()
    pieces_dict = {}
    for doc in documents:
        pieces = PieceRequise.objects.filter(document=doc, commune=request.user.commune)
        pieces_dict[doc] = pieces

    # Statistiques sur les demandes du citoyen
    demandes = Demande.objects.filter(user=request.user).order_by('-date_demande')
    demandes_validees = [d for d in demandes if d.statut == 'validee']
    demandes_en_attente = [d for d in demandes if d.statut == 'en_attente']
    demandes_rejetees = [d for d in demandes if d.statut == 'rejetee']

    return render(request, 'citoyen/dashboard.html', {
        'documents': documents,
        'pieces_dict': pieces_dict,
        'demandes': demandes,
        'demandes_validees': demandes_validees,
        'demandes_en_attente': demandes_en_attente,
        'demandes_rejetees': demandes_rejetees,
    })
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

    return render(request, 'dashboards/admin/create_user.html', {
        'error': error,
        'user_type': user_type,
        'quartiers': quartiers
    })



# --- les liens pour la liste des opérateurs et agents ---

@login_required
@role_required(['admin'])
def liste_agents(request):
    agents = CustomUser.objects.filter(role='agent')
    return render(request, 'dashboards/admin/liste_agents.html', {'agents': agents})

@login_required
@role_required(['admin'])
def liste_operateurs(request):
    operateurs = CustomUser.objects.filter(role='operateur')
    return render(request, 'dashboards/admin/liste_operateurs.html', {'operateurs': operateurs})



# --- Vue pour la modification ---
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
    if user.role == 'agent':
        return redirect('liste_agents')
    elif user.role == 'operateur':
            return redirect('liste_operateurs')
    else:
            return redirect('admin_dashboard')

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

def quartiers_par_commune(request):
    commune_id = request.GET.get('commune_id')
    quartiers = Quartier.objects.filter(commune_id=commune_id)
    data = [{'id': q.id, 'nom': q.nom} for q in quartiers]
    return JsonResponse({'quartiers': data})
