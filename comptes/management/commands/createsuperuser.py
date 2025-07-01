from django.contrib.auth.management.commands.createsuperuser import Command as BaseCreateSuperuserCommand
from comptes.models import CustomUser

class Command(BaseCreateSuperuserCommand):
    def handle(self, *args, **options):
        super().handle(*args, **options)

        # Récupérer l'utilisateur nouvellement créé
        username = options.get('username')
        user = CustomUser.objects.get(username=username)
        if user.is_superuser:
            user.role = 'superadmin'
            user.save()
