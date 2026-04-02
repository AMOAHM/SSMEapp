"""
Seed data script for SSME backend.
Run this script after migrations to populate the database with initial data.
"""

import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ssme_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from categories.models import Category
from businesses.models import Business, BusinessImage, Product
from reviews.models import Review

User = get_user_model()


def create_categories():
    """Create initial categories."""
    categories_data = [
        {'name': 'Food', 'icon': '🍔', 'description': 'Restaurants, cafes, and food services'},
        {'name': 'Fashion', 'icon': '👗', 'description': 'Clothing and fashion accessories'},
        {'name': 'Electronics', 'icon': '📱', 'description': 'Electronic devices and gadgets'},
        {'name': 'Home Decor', 'icon': '🏠', 'description': 'Home decoration and furniture'},
        {'name': 'Bakery', 'icon': '🥖', 'description': 'Bakeries and pastry shops'},
        {'name': 'Health & Beauty', 'icon': '💄', 'description': 'Health and beauty products'},
        {'name': 'Sports', 'icon': '⚽', 'description': 'Sports equipment and services'},
        {'name': 'Books', 'icon': '📚', 'description': 'Bookstores and educational materials'},
        {'name': 'Toys', 'icon': '🎮', 'description': 'Toys and games'},
        {'name': 'Pet Supplies', 'icon': '🐕', 'description': 'Pet products and services'},
        {'name': 'Automotive', 'icon': '🚗', 'description': 'Automotive services and products'},
        {'name': 'Professional Services', 'icon': '💼', 'description': 'Professional and consulting services'},
    ]
    
    created_categories = []
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(
            name=cat_data['name'],
            defaults={
                'icon': cat_data['icon'],
                'description': cat_data['description']
            }
        )
        created_categories.append(category)
        if created:
            print(f"Created category: {category.name}")
    
    return created_categories


def create_users():
    """Create initial users."""
    users_data = [
        {
            'email': 'admin@ssme.com',
            'username': 'admin',
            'first_name': 'Admin',
            'last_name': 'User',
            'role': 'admin',
            'password': 'admin123'
        },
        {
            'email': 'business1@ssme.com',
            'username': 'business1',
            'first_name': 'John',
            'last_name': 'Doe',
            'role': 'business',
            'password': 'business123'
        },
        {
            'email': 'business2@ssme.com',
            'username': 'business2',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'role': 'business',
            'password': 'business123'
        },
        {
            'email': 'customer1@ssme.com',
            'username': 'customer1',
            'first_name': 'Alice',
            'last_name': 'Johnson',
            'role': 'customer',
            'password': 'customer123'
        },
        {
            'email': 'customer2@ssme.com',
            'username': 'customer2',
            'first_name': 'Bob',
            'last_name': 'Wilson',
            'role': 'customer',
            'password': 'customer123'
        },
    ]
    
    created_users = []
    for user_data in users_data:
        user, created = User.objects.get_or_create(
            email=user_data['email'],
            defaults={
                'username': user_data['username'],
                'first_name': user_data['first_name'],
                'last_name': user_data['last_name'],
                'role': user_data['role'],
            }
        )
        if created:
            user.set_password(user_data['password'])
            user.save()
            print(f"Created user: {user.email}")
        created_users.append(user)
    
    return created_users


def create_businesses(users, categories):
    """Create sample businesses."""
    businesses_data = [
        {
            'name': 'The Modern Bistro',
            'description': 'A contemporary restaurant offering fusion cuisine with local ingredients. Experience fine dining in a modern atmosphere.',
            'website': 'https://modernbistro.com',
            'phone': '+233-30-123-4567',
            'email': 'info@modernbistro.com',
            'address': '123 Main Street, Osu',
            'city': 'Accra',
            'category': categories[0],  # Food
            'status': 'approved',
            'featured': True,
            'owner': users[1],  # business1
        },
        {
            'name': 'Chic Fashion Boutique',
            'description': 'Trendy fashion boutique offering the latest styles in clothing and accessories for men and women.',
            'website': 'https://chicfashion.com',
            'phone': '+233-30-234-5678',
            'email': 'hello@chicfashion.com',
            'address': '456 Fashion Avenue, Labone',
            'city': 'Accra',
            'category': categories[1],  # Fashion
            'status': 'approved',
            'featured': True,
            'owner': users[2],  # business2
        },
        {
            'name': 'Tech Solutions Ghana',
            'description': 'Your one-stop shop for all electronic gadgets, repairs, and tech accessories.',
            'website': 'https://techsolutionsgh.com',
            'phone': '+233-30-345-6789',
            'email': 'sales@techsolutionsgh.com',
            'address': '789 Tech Street, Accra Mall',
            'city': 'Accra',
            'category': categories[2],  # Electronics
            'status': 'approved',
            'featured': False,
            'owner': users[1],  # business1
        },
        {
            'name': 'Sweet Dreams Bakery',
            'description': 'Artisanal bakery specializing in cakes, pastries, and custom desserts for all occasions.',
            'website': 'https://sweetdreamsbakery.com',
            'phone': '+233-30-456-7890',
            'email': 'orders@sweetdreamsbakery.com',
            'address': '321 Bakery Lane, East Legon',
            'city': 'Accra',
            'category': categories[4],  # Bakery
            'status': 'approved',
            'featured': False,
            'owner': users[2],  # business2
        },
        {
            'name': 'Glow Beauty Spa',
            'description': 'Premium beauty and wellness spa offering a wide range of treatments and therapies.',
            'website': 'https://glowbeautyspa.com',
            'phone': '+233-30-567-8901',
            'email': 'info@glowbeautyspa.com',
            'address': '654 Wellness Road, Airport Residential',
            'city': 'Accra',
            'category': categories[5],  # Health & Beauty
            'status': 'pending',
            'featured': False,
            'owner': users[1],  # business1
        },
    ]
    
    created_businesses = []
    for biz_data in businesses_data:
        business, created = Business.objects.get_or_create(
            name=biz_data['name'],
            defaults=biz_data
        )
        if created:
            print(f"Created business: {business.name}")
        created_businesses.append(business)
    
    return created_businesses


def create_products(businesses):
    """Create sample products for businesses."""
    products_data = [
        # Products for Modern Bistro
        {
            'business': businesses[0],
            'name': 'Grilled Salmon Deluxe',
            'description': 'Fresh Atlantic salmon grilled to perfection with herbs and lemon butter sauce',
            'price': 85.00,
            'in_stock': True,
        },
        {
            'business': businesses[0],
            'name': 'Fusion Pasta Special',
            'description': 'Homemade pasta with local Ghanaian ingredients and Italian techniques',
            'price': 65.00,
            'in_stock': True,
        },
        
        # Products for Chic Fashion Boutique
        {
            'business': businesses[1],
            'name': 'Designer Summer Dress',
            'description': 'Elegant summer dress perfect for any occasion',
            'price': 250.00,
            'in_stock': True,
        },
        {
            'business': businesses[1],
            'name': 'Leather Handbag Collection',
            'description': 'Premium leather handbags with unique designs',
            'price': 450.00,
            'in_stock': True,
        },
        
        # Products for Tech Solutions Ghana
        {
            'business': businesses[2],
            'name': 'Smartphone Pro Max',
            'description': 'Latest smartphone with advanced features and accessories',
            'price': 3500.00,
            'in_stock': True,
        },
        {
            'business': businesses[2],
            'name': 'Wireless Earbuds Premium',
            'description': 'High-quality wireless earbuds with noise cancellation',
            'price': 450.00,
            'in_stock': True,
        },
    ]
    
    created_products = []
    for prod_data in products_data:
        product, created = Product.objects.get_or_create(
            name=prod_data['name'],
            business=prod_data['business'],
            defaults={
                'description': prod_data['description'],
                'price': prod_data['price'],
                'in_stock': prod_data['in_stock']
            }
        )
        if created:
            print(f"Created product: {product.name}")
        created_products.append(product)
    
    return created_products


def create_reviews(users, businesses):
    """Create sample reviews."""
    reviews_data = [
        {
            'user': users[3],  # customer1
            'business': businesses[0],  # Modern Bistro
            'rating': 5,
            'comment': 'Amazing food and excellent service! The fusion concept is brilliant.'
        },
        {
            'user': users[4],  # customer2
            'business': businesses[0],  # Modern Bistro
            'rating': 4,
            'comment': 'Great atmosphere and delicious food. A bit pricey but worth it.'
        },
        {
            'user': users[3],  # customer1
            'business': businesses[1],  # Chic Fashion Boutique
            'rating': 5,
            'comment': 'Love their collection! Always find something unique and stylish.'
        },
        {
            'user': users[4],  # customer2
            'business': businesses[2],  # Tech Solutions Ghana
            'rating': 4,
            'comment': 'Good prices and authentic products. Staff is very knowledgeable.'
        },
        {
            'user': users[3],  # customer1
            'business': businesses[3],  # Sweet Dreams Bakery
            'rating': 5,
            'comment': 'Best cakes in town! Their custom birthday cakes are amazing.'
        },
    ]
    
    created_reviews = []
    for review_data in reviews_data:
        review, created = Review.objects.get_or_create(
            user=review_data['user'],
            business=review_data['business'],
            defaults={
                'rating': review_data['rating'],
                'comment': review_data['comment']
            }
        )
        if created:
            print(f"Created review by {review.user.email} for {review.business.name}")
        created_reviews.append(review)
    
    return created_reviews


def main():
    """Main seeding function."""
    print("Starting database seeding...")
    
    # Create categories first
    print("\n=== Creating Categories ===")
    categories = create_categories()
    
    # Create users
    print("\n=== Creating Users ===")
    users = create_users()
    
    # Create businesses
    print("\n=== Creating Businesses ===")
    businesses = create_businesses(users, categories)
    
    # Create products
    print("\n=== Creating Products ===")
    products = create_products(businesses)
    
    # Create reviews
    print("\n=== Creating Reviews ===")
    reviews = create_reviews(users, businesses)
    
    print("\n=== Database seeding completed! ===")
    print(f"Created {len(categories)} categories")
    print(f"Created {len(users)} users")
    print(f"Created {len(businesses)} businesses")
    print(f"Created {len(products)} products")
    print(f"Created {len(reviews)} reviews")
    
    print("\n=== Login Credentials ===")
    print("Admin: admin@ssme.com / admin123")
    print("Business 1: business1@ssme.com / business123")
    print("Business 2: business2@ssme.com / business123")
    print("Customer 1: customer1@ssme.com / customer123")
    print("Customer 2: customer2@ssme.com / customer123")


if __name__ == '__main__':
    main()
