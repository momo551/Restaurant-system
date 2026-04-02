from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    verbose_name = 'المستخدمين'

    def ready(self):
        """
        Auto-create a default owner if none exists.
        This provides a fail-safe login for the system owner.
        """
        import os
        # Only run this in the main process, not during reloader or migrations
        if os.environ.get('RUN_MAIN') == 'true' or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
            return
            
        try:
            from .models import User
            from django.db import connection

            # Check if User table exists to avoid errors during initial migration
            if 'users_user' not in connection.introspection.table_names():
                return

            default_username = 'admin@restaurant.com'
            default_password = 'AdminPass123!'
            
            if not User.objects.filter(username=default_username).exists():
                User.objects.create_superuser(
                    username=default_username,
                    email=default_username,
                    password=default_password,
                    role=User.Role.OWNER,
                    first_name='Admin',
                    last_name='Owner'
                )
                print(f"✅ Default owner created: {default_username}")
        except Exception as e:
            # Silent fail to ensure the app still starts
            print(f"⚠️ Could not create default owner: {e}")
