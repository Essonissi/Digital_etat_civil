from django.contrib import admin
from .models import Commune

@admin.register(Commune)
class CommuneAdmin(admin.ModelAdmin):
    list_display = ('nom', 'region', 'préfecture')
    search_fields = ('nom', 'region')

from .models import Commune, Quartier

@admin.register(Quartier)
class QuartierAdmin(admin.ModelAdmin):
    list_display = ('nom', 'commune')
    list_filter = ('commune',)
    search_fields = ('nom',)
