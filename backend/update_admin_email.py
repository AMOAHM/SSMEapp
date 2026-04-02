import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ssme_backend.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def update_admin_email():
    try:
        # Check if the new email already exists
        if User.objects.filter(email='maxzygh8@gmail.com').exists():
            print("maxzygh8@gmail.com already exists. Updating its role to superuser just in case.")
            admin = User.objects.get(email='maxzygh8@gmail.com')
            admin.is_staff = True
            admin.is_superuser = True
            admin.role = 'admin'
            admin.save()
            
            # If admin@ssme.com also exists, we should delete it or leave it. We'll delete it to avoid confusion.
            if User.objects.filter(email='admin@ssme.com').exists():
                old = User.objects.get(email='admin@ssme.com')
                if old.id != admin.id:
                    old.delete()
                    print("Deleted old admin@ssme.com")
            
        else:
            # Change the email of the existing admin
            admin = User.objects.get(email='admin@ssme.com')
            admin.email = 'maxzygh8@gmail.com'
            admin.username = 'maxzygh8@gmail.com'
            admin.save()
            print("Successfully updated admin@ssme.com to maxzygh8@gmail.com")
    except User.DoesNotExist:
        print("admin@ssme.com not found. Creating maxzygh8@gmail.com.")
        User.objects.create_superuser('maxzygh8@gmail.com', 'admin123')

if __name__ == '__main__':
    update_admin_email()
