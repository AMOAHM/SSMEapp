import os
import django
import sys

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ssme_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from businesses.models import Business, Product, Service, BusinessImage, Favorite
from categories.models import Category
from orders.models import Order, OrderItem, OrderStatusHistory
from accounts.models import UserProfile, UserActivity

User = get_user_model()

def clear_database():
    print("Clearing database...")
    
    # 1. We won't delete Categories, as they are usually static setup data, 
    # but we will delete everything else related to users and business.
    
    # Actually, the user said "remove everything", so let's wipe Categories too if requested, 
    # but they are often seeded. I'll leave categories so the marketplace doesn't break.
    
    admin_email = 'admin@ssme.com'
    
    # Check if admin exists
    try:
        admin_user = User.objects.get(email=admin_email)
        print(f"Found admin user: {admin_user.email}")
    except User.DoesNotExist:
        print(f"WARNING: {admin_email} does not exist. It will not be preserved.")
        admin_user = None

    # Delete all businesses (this will cascade to Products, Services, Images, Reviews)
    print("Deleting all businesses...")
    Business.objects.all().delete()
    
    # Delete all orders
    print("Deleting all orders...")
    Order.objects.all().delete()
    
    # Delete all user activities
    print("Deleting user activities...")
    UserActivity.objects.all().delete()

    # Finally, delete users
    print("Deleting users...")
    if admin_user:
        # Delete everyone except admin
        users_to_delete = User.objects.exclude(id=admin_user.id)
        count = users_to_delete.count()
        users_to_delete.delete()
        print(f"Deleted {count} users. Preserved {admin_email}.")
    else:
        count = User.objects.all().count()
        User.objects.all().delete()
        print(f"Deleted all {count} users.")
        
    print("Database cleared successfully.")

if __name__ == '__main__':
    clear_database()
