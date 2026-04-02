#!/usr/bin/env python
"""
Script to delete all businesses/stores from database
"""
import os
import sys
import django

# Setup Django
sys.path.append(r'c:\Users\user\Desktop\SSME\backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ssme_backend.settings')
django.setup()

from django.db import transaction
from businesses.models import Business, BusinessImage, Product, Favorite
from reviews.models import Review

def delete_all_businesses():
    """Delete all businesses and related data from database."""
    print("🗑️  DELETING ALL BUSINESSES FROM DATABASE")
    print("=" * 60)
    
    try:
        with transaction.atomic():
            # Get counts before deletion
            business_count = Business.objects.count()
            image_count = BusinessImage.objects.count()
            product_count = Product.objects.count()
            favorite_count = Favorite.objects.count()
            review_count = Review.objects.count()
            
            print(f"📊 Current Database Status:")
            print(f"   Businesses: {business_count}")
            print(f"   Business Images: {image_count}")
            print(f"   Products: {product_count}")
            print(f"   Favorites: {favorite_count}")
            print(f"   Reviews: {review_count}")
            
            if business_count == 0:
                print("\n✅ No businesses found in database. Nothing to delete.")
                return True
            
            print(f"\n⚠️  WARNING: This will permanently delete ALL {business_count} businesses!")
            print("   This action cannot be undone!")
            
            # Ask for confirmation
            confirm = input("\nType 'DELETE ALL' to confirm: ")
            if confirm != 'DELETE ALL':
                print("❌ Deletion cancelled. No changes made.")
                return False
            
            print("\n🗑️  Starting deletion process...")
            
            # Delete in correct order to respect foreign key constraints
            print("1. Deleting favorites...")
            Favorite.objects.all().delete()
            
            print("2. Deleting reviews...")
            Review.objects.all().delete()
            
            print("3. Deleting products...")
            Product.objects.all().delete()
            
            print("4. Deleting business images...")
            BusinessImage.objects.all().delete()
            
            print("5. Deleting businesses...")
            Business.objects.all().delete()
            
            print("\n✅ SUCCESS: All businesses and related data deleted!")
            
            # Verify deletion
            remaining_businesses = Business.objects.count()
            if remaining_businesses == 0:
                print("✅ Verification: No businesses remain in database")
            else:
                print(f"❌ Warning: {remaining_businesses} businesses still exist")
            
            return True
            
    except Exception as e:
        print(f"❌ Error during deletion: {str(e)}")
        return False

def show_final_status():
    """Show final database status after deletion."""
    print("\n📊 Final Database Status:")
    print("=" * 40)
    
    try:
        business_count = Business.objects.count()
        image_count = BusinessImage.objects.count()
        product_count = Product.objects.count()
        favorite_count = Favorite.objects.count()
        review_count = Review.objects.count()
        
        print(f"   Businesses: {business_count}")
        print(f"   Business Images: {image_count}")
        print(f"   Products: {product_count}")
        print(f"   Favorites: {favorite_count}")
        print(f"   Reviews: {review_count}")
        
        if business_count == 0:
            print("\n🎉 All businesses successfully deleted!")
            print("🏪 The stores database is now empty.")
        else:
            print(f"\n⚠️  {business_count} businesses still remain.")
            
    except Exception as e:
        print(f"❌ Error checking final status: {str(e)}")

if __name__ == '__main__':
    print("🚀 Business Deletion Script")
    print("=" * 40)
    print("⚠️  This script will delete ALL businesses from the database!")
    print("   Including all related data:")
    print("   - Business images")
    print("   - Products")
    print("   - Reviews")
    print("   - Favorites")
    print()
    
    success = delete_all_businesses()
    show_final_status()
    
    if success:
        print("\n🎯 Next Steps:")
        print("1. Refresh frontend: http://localhost:5175/stores")
        print("2. Check admin panel: http://localhost:5175/admin-management")
        print("3. Add new businesses as needed")
    
    sys.exit(0 if success else 1)
