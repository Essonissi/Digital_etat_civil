# demandes/utils.py

from io import BytesIO
from django.template.loader import get_template
from xhtml2pdf import pisa

def generer_pdf_confirmation(demande):
    """Génère un PDF de confirmation de demande"""
    try:
        template = get_template("pdf/confirmation_demande.html")
        context = {
            "demande": demande,
            "citoyen": demande.user,
            "document": demande.document,
            "commune": demande.commune,
            "quartier": demande.quartier,
            "date": demande.date_demande.strftime("%d/%m/%Y %H:%M"),
        }
        html = template.render(context)
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
        if not pdf.err:
            return result.getvalue()
        return None
    except Exception as e:
        print("Erreur génération PDF :", e)
        return None
