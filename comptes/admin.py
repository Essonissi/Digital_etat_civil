from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser





@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'role', 'commune', 'is_active')
    list_filter = ('role', 'commune')
    fieldsets = UserAdmin.fieldsets + (
        ('Infos métier', {'fields': ('role', 'commune')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Infos métier', {'fields': ('role', 'commune')}),
    )


