#!/usr/bin/env python
"""
Create admin user for SSME system
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

def create_admin_user():
    """Create admin user with proper credentials."""
    print("👑 Creating Admin User")
    print("=" * 40)
    
    # Admin user details
    admin_data = {
        'email': 'admin@ssme.com',
        'username': 'admin',
        'first_name': 'System',
        'last_name': 'Administrator',
        'phone': '+233500000000',
        'role': 'super_admin',
        'account_status': 'active',
        'is_staff': True,
        'is_superuser': True,
        'is_business_verified': True
    }
    
    password = 'admin123'
    
    try:
        # Check if admin user already exists
        existing_admin = User.objects.filter(email=admin_data['email']).first()
        
        if existing_admin:
            print(f"✅ Admin user '{admin_data['email']}' already exists.")
            print(f"   Username: {existing_admin.username}")
            print(f"   Role: {existing_admin.role}")
            print(f"   Is Staff: {existing_admin.is_staff}")
            print(f"   Is Superuser: {existing_admin.is_superuser}")
            
            # Update password if needed
            existing_admin.set_password(password)
            existing_admin.save()
            print(f"✅ Password updated to: {password}")
            return True
        
        # Create new admin user
        admin_user = User.objects.create_user(
            email=admin_data['email'],
            username=admin_data['username'],
            first_name=admin_data['first_name'],
            last_name=admin_data['last_name'],
            phone=admin_data['phone'],
            role=admin_data['role'],
            account_status=admin_data['account_status'],
            password=password,
            is_staff=admin_data['is_staff'],
            is_superuser=admin_data['is_superuser'],
            is_business_verified=admin_data['is_business_verified']
        )
        
        print(f"✅ Admin user created successfully!")
        print(f"   Email: {admin_user.email}")
        print(f"   Username: {admin_user.username}")
        print(f"   Name: {admin_user.first_name} {admin_user.last_name}")
        print(f"   Role: {admin_user.role}")
        print(f"   Phone: {admin_user.phone}")
        print(f"   Password: {password}")
        print(f"   Is Staff: {admin_user.is_staff}")
        print(f"   Is Superuser: {admin_user.is_superuser}")
        print(f"   Account Status: {admin_user.account_status}")
        print(f"   Business Verified: {admin_user.is_business_verified}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating admin user: {str(e)}")
        return False

def create_test_admin():
    """Create additional test admin user."""
    print("\n🧪 Creating Test Admin User")
    print("=" * 40)
    
    # Test admin details
    test_admin_data = {
        'email': 'testadmin@ssme.com',
        'username': 'testadmin',
        'first_name': 'Test',
        'last_name': 'Admin',
        'phone': '+233500000001',
        'role': 'admin',
        'account_status': 'active',
        'is_staff': True,
        'is_superuser': False,
        'is_business_verified': True
    }
    
    password = 'testadmin123'
    
    try:
        # Check if test admin already exists
        existing_test_admin = User.objects.filter(email=test_admin_data['email']).first()
        
        if existing_test_admin:
            print(f"✅ Test admin user '{test_admin_data['email']}' already exists.")
            print(f"   Username: {existing_test_admin.username}")
            print(f"   Role: {existing_test_admin.role}")
            
            # Update password if needed
            existing_test_admin.set_password(password)
            existing_test_admin.save()
            print(f"✅ Password updated to: {password}")
            return True
        
        # Create new test admin user
        test_admin_user = User.objects.create_user(
            email=test_admin_data['email'],
            username=test_admin_data['username'],
            first_name=test_admin_data['first_name'],
            last_name=test_admin_data['last_name'],
            phone=test_admin_data['phone'],
            role=test_admin_data['role'],
            account_status=test_admin_data['account_status'],
            password=password,
            is_staff=test_admin_data['is_staff'],
            is_superuser=test_admin_data['is_superuser'],
            is_business_verified=test_admin_data['is_business_verified']
        )
        
        print(f"✅ Test admin user created successfully!")
        print(f"   Email: {test_admin_user.email}")
        print(f"   Username: {test_admin_user.username}")
        print(f"   Name: {test_admin_user.first_name} {test_admin_user.last_name}")
        print(f"   Role: {test_admin_user.role}")
        print(f"   Phone: {test_admin_user.phone}")
        print(f"   Password: {password}")
        print(f"   Is Staff: {test_admin_user.is_staff}")
        print(f"   Is Superuser: {test_admin_user.is_superuser}")
        print(f"   Account Status: {test_admin_user.account_status}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating test admin user: {str(e)}")
        return False

def verify_admin_users():
    """Verify admin users in the system."""
    print("\n🔍 Verifying Admin Users")
    print("=" * 40)
    
    try:
        # Get all admin users
        admin_users = User.objects.filter(
            Q(is_staff=True) | Q(role__in=['admin', 'super_admin'])
        ).order_by('-date_joined')
        
        print(f"📊 Total Admin Users: {admin_users.count()}")
        print("")
        
        for i, admin in enumerate(admin_users, 1):
            print(f"{i}. {admin.email}")
            print(f"   Username: {admin.username}")
            print(f"   Name: {admin.first_name} {admin.last_name}")
            print(f"   Role: {admin.role}")
            print(f"   Phone: {admin.phone}")
            print(f"   Is Staff: {admin.is_staff}")
            print(f"   Is Superuser: {admin.is_superuser}")
            print(f"   Account Status: {admin.account_status}")
            print(f"   Created: {admin.date_joined.strftime('%Y-%m-%d %H:%M')}")
            print("")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verifying admin users: {str(e)}")
        return False

def show_login_info():
    """Show login information for admin users."""
    print("\n🔑 Admin Login Information")
    print("=" * 40)
    
    print("🎯 Main Admin User:")
    print("   Email: admin@ssme.com")
    print("   Password: admin123")
    print("   Role: Super Administrator")
    print("")
    
    print("🧪 Test Admin User:")
    print("   Email: testadmin@ssme.com")
    print("   Password: testadmin123")
    print("   Role: Administrator")
    print("")
    
    print("🌐 Frontend Login:")
    print("   URL: http://localhost:5175/admin-login")
    print("   OR: http://localhost:5175/login")
    print("")
    
    print("🔧 Django Admin:")
    print("   URL: http://localhost:8000/admin/")
    print("   Use main admin credentials")
    print("")
    
    print("📱 Admin Panel:")
    print("   URL: http://localhost:5175/admin-management")
    print("   URL: http://localhost:5175/admin-reports")
    print("   URL: http://localhost:5175/businesses")

if __name__ == '__main__':
    print("🚀 SSME Admin User Creation")
    print("=" * 50)
    
    # Import Q for complex queries
    from django.db.models import Q
    
    # Create main admin user
    main_admin_success = create_admin_user()
    
    # Create test admin user
    test_admin_success = create_test_admin()
    
    # Verify admin users
    verify_success = verify_admin_users()
    
    # Show login information
    show_login_info()
    
    if main_admin_success and test_admin_success and verify_success:
        print("\n🎉 ADMIN USER CREATION SUCCESSFUL!")
        print("👑 Admin users are ready for system management!")
        print("🔑 Login credentials are provided above.")
    else:
        print("\n❌ Some admin user creation failed. Check the logs above.")
    
    sys.exit(0 if (main_admin_success and test_admin_success and verify_success) else 1)
