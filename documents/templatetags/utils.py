from django import template
register = template.Library()

@register.filter
def dict_filter(demandes, statut):
    return [d for d in demandes if d.statut == statut]
