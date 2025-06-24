from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from comptes.decorators import role_required
from django.shortcuts import render, redirect
from django.contrib import messages

def login_view(request):
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
            return render(request, 'comptes/login.html', {'error': 'Identifiants invalides'})
    return render(request, 'comptes/login.html')

def citoyen_login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user and user.role == 'citoyen':
            login(request, user)
            return redirect('citoyen_dashboard')  # ou page d'accueil citoyen
        else:
            messages.error(request, "Accès réservé aux citoyens.")
    
    return render(request, 'comptes/citoyen_login.html')

def citoyen_register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password != password2:
            messages.error(request, "Les mots de passe ne correspondent pas.")
            return render(request, 'comptes/citoyen_signup.html')

        if user.objects.filter(username=username).exists():
            messages.error(request, "Ce nom d'utilisateur existe déjà.")
            return render(request, 'comptes/citoyen_signup.html')

        user = user.objects.create_user(username=username, password=password)
        user.role = 'citoyen'
        user.save()
        login(request, user)
        return redirect('citoyen_dashboard')

    return render(request, 'comptes/citoyen_signup.html')


@login_required
@role_required(['superadmin'])
def superadmin_dashboard(request):
    return render(request, 'dashboards/dashboard_base.html')


@login_required
@role_required(['admin'])
def admin_dashboard(request):
    return render(request, 'dashboards/dashboard_base.html')


@login_required
@role_required(['operateur'])
def operateur_dashboard(request):
    return render(request, 'dashboards/dashboard_base.html')


@login_required
@role_required(['agent'])
def agent_dashboard(request):
    return render(request, 'dashboards/dashboard_base.html')

