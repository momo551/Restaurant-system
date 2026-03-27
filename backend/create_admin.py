import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model

def create_default_admin():
    User = get_user_model()
    # Using the credentials that the admin usually logs in with
    # You can change these inside Railway environment variables later!
    admin_email = os.environ.get('DEFAULT_ADMIN_EMAIL', 'admin@restaurant.com')
    admin_password = os.environ.get('DEFAULT_ADMIN_PASSWORD', 'admin123')
    
    if not User.objects.filter(email=admin_email).exists():
        # Django requires a username, so we'll just extract it from email
        username = admin_email.split('@')[0]
        print(f"Creating default admin account: {admin_email}")
        User.objects.create_superuser(
            email=admin_email,
            username=username,
            password=admin_password
        )
        print("Admin account created successfully!")
    else:
        print("Admin account already exists.")

if __name__ == '__main__':
    create_default_admin()
