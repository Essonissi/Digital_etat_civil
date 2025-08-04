from demandes.models import Demande
from documents.models import Document, PieceRequise
from django.shortcuts import render
from django.db.models import Q
from django.utils.dateparse import parse_date

def home(request):
    return render(request, 'home.html')

def liste_documents_citoyen(request):
    documents = Document.objects.all()
    demandes = Demande.objects.filter(user=request.user).order_by('-date_demande')

    # Filtres
    statut = request.GET.get('statut')
    type_doc = request.GET.get('type')
    date = request.GET.get('date')

    if statut:
        demandes = demandes.filter(statut=statut)
    if type_doc:
        demandes = demandes.filter(document__id=type_doc)
    if date:
        demandes = demandes.filter(date_demande__date=parse_date(date))

    statuts = Demande._meta.get_field('statut').choices

    return render(request, 'citoyen/liste_documents.html', {
        'documents': documents,
        'demandes': demandes,
        'statuts': statuts,
        'filtre_statut': statut,
        'filtre_type': type_doc,
        'filtre_date': date,
    })

