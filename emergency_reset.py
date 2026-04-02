import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from users.models import User

def reset_owner_password():
    """
    Emergency script to reset the main owner password.
    """
    username = 'Mohamed-Abed123'
    new_password = 'NewPass123!'
    
    try:
        user = User.objects.get(username=username)
        user.set_password(new_password)
        user.save()
        print(f"✅ Success: Password for {username} has been reset.")
        print(f"🔑 New Login: {username} / {new_password}")
    except User.DoesNotExist:
        print(f"❌ Error: User {username} not found in the database.")
        # Optional: create the user if it doesn't exist
        print("Checking for any owner accounts...")
        any_owner = User.objects.filter(role='owner').first()
        if any_owner:
            any_owner.set_password(new_password)
            any_owner.save()
            print(f"✅ Success: Password for owner '{any_owner.username}' has been reset.")
        else:
            print("❌ No owner accounts found.")

if __name__ == '__main__':
    reset_owner_password()
