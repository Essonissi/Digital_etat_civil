from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CentreInteretForm
from .models import CentreInteret
from comptes.decorators import role_required
from communes.models import Commune, Quartier
from rest_framework import viewsets
from .serializers import CentreInteretSerializer
from django.shortcuts import get_object_or_404
from .forms import CentreInteretForm

class CentreInteretViewSet(viewsets.ModelViewSet):
    queryset = CentreInteret.objects.all()
    serializer_class = CentreInteretSerializer

@login_required
@role_required(['operateur'])
def ajouter_centre_interet(request):
    quartiers = Quartier.objects.filter(commune=request.user.commune)

    if request.method == 'POST':
        quartier_id = request.POST.get('quartier')
        form = CentreInteretForm(request.POST)

        if form.is_valid():
            centre = form.save(commit=False)
            centre.commune = request.user.commune
            centre.quartier = Quartier.objects.get(id=quartier_id)            
            centre.save()
            messages.success(request, "Centre d'intérêt ajouté avec succès.")
            return redirect('liste_centres')
    else:
        form = CentreInteretForm()

    return render(request, 'dashboards/operateur/ajouter_centre_interet.html', {
        'form': form,
        'quartiers': quartiers
    })

@login_required
@role_required(['operateur'])
def supprimer_centre_interet(request, centre_id):
    centre = get_object_or_404(CentreInteret, id=centre_id, commune=request.user.commune)

    if request.method == 'POST':
        centre_nom = centre.nom
        centre.delete()
        messages.success(request, f"Centre d'intérêt '{centre_nom}' supprimé avec succès.")
        
        # Si c'est une requête AJAX, retourner une réponse JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f"Centre d'intérêt '{centre_nom}' supprimé avec succès."
            })
        
        return redirect('liste_centres')

    # Pour les requêtes GET, afficher la page de confirmation
    return render(request, 'dashboards/operateur/confirmer_suppression.html', {
        'centre': centre
    })

@login_required
@role_required(['operateur'])
def modifier_centre_interet(request, centre_id):
    centre = get_object_or_404(CentreInteret, id=centre_id, commune=request.user.commune)

    if request.method == 'POST':
        form = CentreInteretForm(request.POST, instance=centre)
        if form.is_valid():
            form.save()
            messages.success(request, f"Centre d'intérêt '{centre.nom}' modifié avec succès.")
            return redirect('liste_centres')
    else:
        form = CentreInteretForm(instance=centre)

    quartiers = Quartier.objects.filter(commune=request.user.commune)

    return render(request, 'dashboards/operateur/ajouter_centre_interet.html', {
        'form': form,
        'quartiers': quartiers,
        'centre': centre,
        'is_edit': True,  
        'existing_lat': float(centre.latitude) if centre.latitude else None,
        'existing_lng': float(centre.longitude) if centre.longitude else None
    })


@login_required
@role_required(['operateur', 'admin', 'citoyen'])
def liste_centres(request):
    centres = CentreInteret.objects.filter(commune=request.user.commune).select_related('commune', 'quartier')
    
    # Calculer les statistiques pour le template
    centres_with_location = centres.filter(latitude__isnull=False, longitude__isnull=False)
    
    # Obtenir les types distincts
    types_distincts = centres.values_list('type', flat=True).distinct()
    types_count = len(types_distincts)
    
    # Obtenir les quartiers distincts - maintenant via la relation ForeignKey
    quartiers_distincts = Quartier.objects.filter(commune=request.user.commune, centreinteret__isnull=False).distinct()
    quartiers_count = quartiers_distincts.count()
    
    context = {
        'centres': centres,
        'centres_with_location': centres_with_location,
        'types_count': types_count,
        'quartiers_count': quartiers_count,
        'types_distincts': types_distincts,
        'quartiers_distincts': quartiers_distincts,
    }
    
    return render(request, 'dashboards/operateur/liste_centres.html', context)

@login_required
@role_required(['citoyen'])
def liste_centres_citoyen(request):
    commune = request.user.commune
    quartier = request.user.quartier
    type_filtre = request.GET.get('type')
    centres = CentreInteret.objects.filter(commune=commune)
    if quartier:
        centres = centres.filter(quartier=quartier)
    if type_filtre:
        centres = centres.filter(type=type_filtre)
    types = CentreInteret.TYPE_CHOICES
    return render(request, 'citoyen/liste_centres.html', {
        'centres': centres,
        'types': types,
        'type_filtre': type_filtre
    })
