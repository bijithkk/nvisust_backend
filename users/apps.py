from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
        from .models import Role
        # Seed default roles if not present
        try:
            for role_name in [Role.ADMIN, Role.MANAGER, Role.EMPLOYEE]:
                Role.objects.get_or_create(name=role_name)
        except Exception:
            # Migrations might not be ready yet; ignore
            pass