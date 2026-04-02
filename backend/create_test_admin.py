#!/usr/bin/env python
"""
Create admin user for testing frontend connection
"""
import os
import sys
import django

# Setup Django
sys.path.append(r'c:\Users\user\Desktop\SSME\backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ssme_backend.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def create_test_admin():
    """Create a test admin user."""
    try:
        # Create or get admin user
        admin_user, created = User.objects.get_or_create(
            email='admin@ssme.com',
            defaults={
                'username': 'admin@ssme.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True,
                'is_active': True,
                'is_verified': True,
                'account_status': 'active',
            }
        )
        
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            print(f"✅ Created admin user: {admin_user.email}")
            print(f"   Password: admin123")
            print(f"   Role: {admin_user.role}")
        else:
            print(f"✅ Admin user already exists: {admin_user.email}")
        
        # Create test business user
        business_user, created = User.objects.get_or_create(
            email='business@ssme.com',
            defaults={
                'username': 'business@ssme.com',
                'first_name': 'Business',
                'last_name': 'Owner',
                'role': 'business',
                'is_active': True,
                'is_verified': True,
                'account_status': 'active',
            }
        )
        
        if created:
            business_user.set_password('business123')
            business_user.save()
            print(f"✅ Created business user: {business_user.email}")
            print(f"   Password: business123")
            print(f"   Role: {business_user.role}")
        else:
            print(f"✅ Business user already exists: {business_user.email}")
        
        print(f"\n🎯 Test Credentials:")
        print(f"Admin Login: admin@ssme.com / admin123")
        print(f"Business Login: business@ssme.com / business123")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating test users: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = create_test_admin()
    sys.exit(0 if success else 1)
