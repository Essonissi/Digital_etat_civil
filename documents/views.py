from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from documents.models import Document, PieceRequise
from comptes.decorators import role_required
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseForbidden
from rest_framework import viewsets
from .models import Document, PieceRequise
from .serializers import DocumentSerializer, PieceRequiseSerializer

class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

class PieceRequiseViewSet(viewsets.ModelViewSet):
    queryset = PieceRequise.objects.all()
    serializer_class = PieceRequiseSerializer

@login_required
@role_required(['admin'])  # 🔒 accès uniquement aux admins métiers
def gestion_pieces_requises(request):
    admin_commune = request.user.commune

    if not admin_commune:
        return HttpResponseForbidden("Aucune commune liée à votre compte.")

    documents = Document.objects.all()
    pieces_dict = {}

    for doc in documents:
        pieces = PieceRequise.objects.filter(document=doc, commune=admin_commune)
        pieces_dict[doc] = pieces

    return render(request, 'dashboards/admin/gestion_pieces.html', {
        'documents': documents,
        'pieces_dict': pieces_dict,
        'commune': admin_commune,
    })


@login_required
@role_required(['admin'])
@require_POST
def ajouter_piece(request):
    commune = request.user.commune
    if not commune:
        return HttpResponseForbidden("Vous n'êtes lié à aucune commune.")

    libelle = request.POST.get('libelle_piece')
    obligatoire = 'obligatoire' in request.POST
    document_id = request.POST.get('document_id')

    doc = get_object_or_404(Document, id=document_id)

    PieceRequise.objects.create(
        document=doc,
        commune=commune,
        libelle_piece=libelle,
        obligatoire=obligatoire
    )

    return redirect('gestion_pieces')


@login_required
@role_required(['admin'])
@require_POST
def modifier_piece(request, piece_id):
    piece = get_object_or_404(PieceRequise, id=piece_id, commune=request.user.commune)
    libelle = request.POST.get('libelle_piece')
    obligatoire = 'obligatoire' in request.POST

    piece.libelle_piece = libelle
    piece.obligatoire = obligatoire
    piece.save()
    return redirect('gestion_pieces')


@login_required
@role_required(['admin'])
@require_POST
def supprimer_piece(request, piece_id):
    piece = get_object_or_404(PieceRequise, id=piece_id, commune=request.user.commune)
    piece.delete()
    return redirect('gestion_pieces')


@login_required
@role_required(['admin'])
@require_POST
def ajouter_document(request):
    type_doc = request.POST.get('type')
    description = request.POST.get('description', '')
    if type_doc:
        Document.objects.create(type=type_doc, description=description)
    return redirect('gestion_pieces')
