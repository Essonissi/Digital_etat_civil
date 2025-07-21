from rest_framework import viewsets
from .models import Demande
from .serializers import DemandeSerializer
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from documents.models import Document, PieceRequise
from demandes.models import Demande
from fichiers.models import Fichier
from django.urls import reverse
import os
from django.conf import settings
from django.core.files.storage import default_storage
from django.views.decorators.http import require_POST
from django.shortcuts import render, get_object_or_404, redirect
from demandes.models import Demande
from fichiers.models import Fichier
from django.contrib.auth.decorators import login_required
from comptes.decorators import role_required
from django.contrib import messages

class DemandeViewSet(viewsets.ModelViewSet):
    queryset = Demande.objects.all()
    serializer_class = DemandeSerializer



@login_required
def nouvelle_demande(request):
    # Si la commune ou le quartier n'est pas renseigné, on force le choix
    if not request.user.commune or not request.user.quartier:
        return redirect(reverse('choisir_localisation'))

    documents = Document.objects.all()
    user_commune = request.user.commune

    if request.method == 'POST':
        document_id = request.POST.get('document_id')
        document = Document.objects.get(id=document_id)

        # Créer la demande
        demande = Demande.objects.create(
            user=request.user,
            document=document,
            commune=request.user.commune,
            quartier=request.user.quartier,
            statut='en_attente'
        )

        # Sauvegarder les fichiers envoyés
        fichiers = request.FILES.getlist('fichiers')
        for fichier in fichiers:
            # 1. Définir le chemin de stockage
            chemin_relatif = os.path.join('justificatifs', fichier.name)
            chemin_absolu = os.path.join(settings.MEDIA_ROOT, chemin_relatif)
            
            # 2. Sauvegarder le fichier sur le disque
            with default_storage.open(chemin_relatif, 'wb+') as destination:
                for chunk in fichier.chunks():
                    destination.write(chunk)
            
            # 3. Créer l'objet Fichier
            Fichier.objects.create(
                demande=demande,
                nom_fichier=fichier.name,
                chemin=chemin_relatif,
                type='justificatif'
            )

        return redirect('citoyen_dashboard')

    return render(request, 'citoyen/nouvelle_demande.html', {
        'documents': documents
    })


def mes_demandes(request):
    demandes = Demande.objects.filter(user=request.user).order_by('-date_demande')
    if 'just_rejected' in request.GET:
        messages.error(request, "Votre demande a été rejetée. Consultez le détail pour le motif.")
    return render(request, 'citoyen/liste_documents.html', {'demandes': demandes})


@login_required
def detail_demande(request, demande_id):
    demande = get_object_or_404(Demande, id=demande_id, user=request.user)
    return render(request, 'citoyen/detail_demande.html', {'demande': demande})


@login_required
@require_POST
def supprimer_demande(request, demande_id):
    demande = get_object_or_404(Demande, id=demande_id, user=request.user)
    demande.delete()
    return redirect('documents_citoyen')


from django.core.mail import send_mail
from notifications.models import Notification  # Adapte le chemin si nécessaire

@login_required
@role_required(['agent'])
def agent_detail_demande(request, demande_id):
    demande = get_object_or_404(Demande, id=demande_id, quartier=request.user.quartier)
    fichiers = Fichier.objects.filter(demande=demande)
    error = None

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'valider':
            demande.statut = 'validee'
            demande.motif_rejet = ''
            demande.save()

            # ✅ Notification
            Notification.objects.create(
                user=demande.user,
                titre="Demande validée",
                message=f"Votre demande pour « {demande.document.type} » a été validée.",
                type='success',  # ou 'info' selon ton système
                lu=False
            )

            # ✅ Message flash pour l’agent
            messages.success(request, f"La demande de {demande.user.username} a été validée.")
            return redirect('agent:liste_demandes')

        elif action == 'rejeter':
            motif = request.POST.get('motif_rejet', '').strip()
            if not motif:
                error = "Le motif de rejet est obligatoire."
            else:
                demande.statut = 'rejetee'
                demande.motif_rejet = motif
                demande.save()

                # ✅ Notification
                Notification.objects.create(
                    user=demande.user,
                    titre="Demande rejetée",
                    message=f"Votre demande pour « {demande.document.type} » a été rejetée.\nMotif : {demande.motif_rejet}",
                    type='error',
                    lu=False
                )

                # ✅ Email
                send_mail(
                    'Votre demande a été rejetée',
                    f'Bonjour {demande.user.first_name},\n\nVotre demande pour "{demande.document.type}" a été rejetée.\nMotif : {demande.motif_rejet}\n\nVous pouvez vous reconnecter pour plus de détails.',
                    'noreply@mairie.fr',
                    [demande.user.email],
                    fail_silently=True,
                )

                # ✅ Message flash pour l’agent
                messages.error(request, f"La demande de {demande.user.username} a été rejetée.")
                return redirect('agent:liste_demandes')

    return render(request, 'dashboards/agent/detail_demande.html', {
        'demande': demande,
        'fichiers': fichiers,
        'error': error,
    })

@login_required
@role_required(['agent'])
def liste_demandes(request):
    # L'agent ne voit que les demandes de SON quartier
    demandes = Demande.objects.filter(quartier=request.user.quartier)
    return render(request, 'dashboards/agent/liste_demandes.html', {'demandes': demandes})