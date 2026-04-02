from rest_framework import serializers
from django.contrib.auth import get_user_model
from categories.models import Category
from .models import Business, BusinessImage, Product, Favorite, Service

User = get_user_model()


class BusinessImageSerializer(serializers.ModelSerializer):
    """Serializer for business images."""
    
    class Meta:
        model = BusinessImage
        fields = ('id', 'image', 'alt_text', 'created_at')
        read_only_fields = ('id', 'created_at')


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for products."""
    
    class Meta:
        model = Product
        fields = ('id', 'name', 'description', 'price', 'image', 'in_stock', 'created_at')
        read_only_fields = ('id', 'created_at')


class ProductListSerializer(serializers.ModelSerializer):
    """Serializer for global product listings including business info."""
    business_name = serializers.CharField(source='business.name', read_only=True)
    business_city = serializers.CharField(source='business.city', read_only=True)
    
    class Meta:
        model = Product
        fields = ('id', 'business', 'business_name', 'business_city', 'name', 'description', 'price', 'image', 'in_stock')
        read_only_fields = ('id', 'business', 'business_name', 'business_city')


class BusinessSerializer(serializers.ModelSerializer):
    """Serializer for businesses."""
    owner_name = serializers.CharField(source='owner.full_name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    average_rating = serializers.ReadOnlyField()
    review_count = serializers.ReadOnlyField()
    images = BusinessImageSerializer(many=True, read_only=True)
    products = ProductSerializer(many=True, read_only=True)
    
    class Meta:
        model = Business
        fields = (
            'id', 'owner', 'owner_name', 'name', 'description', 'website', 'phone',
            'email', 'address', 'city', 'category', 'category_name', 'status',
            'featured', 'logo', 'rejection_reason', 'suspension_reason',
            'average_rating', 'review_count', 'images',
            'products', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'owner', 'average_rating', 'review_count', 'created_at', 'updated_at')


class BusinessCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating businesses without authentication."""
    
    owner_name = serializers.CharField(write_only=True)
    owner_email = serializers.CharField(write_only=True)
    owner_phone = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = Business
        fields = (
            'name', 'description', 'website', 'phone', 'email', 'address',
            'city', 'category', 'logo', 'owner_name', 'owner_email', 'owner_phone', 'password'
        )
    
    def create(self, validated_data):
        # Extract owner information
        owner_name = validated_data.pop('owner_name')
        owner_email = validated_data.pop('owner_email')
        owner_phone = validated_data.pop('owner_phone')
        password = validated_data.pop('password', None)
        
        # Category is now sent as ID from frontend, so no need to handle string conversion
        # The DRF will automatically handle the ID to object conversion
        
        # Create or get user account
        user, created = User.objects.get_or_create(
            email=owner_email,
            defaults={
                'username': owner_email,
                'first_name': owner_name.split(' ')[0] if ' ' in owner_name else owner_name,
                'last_name': owner_name.split(' ')[1] if ' ' in owner_name else '',
                'phone': owner_phone,
                'is_active': True,
                'role': 'business_owner'  # Set role for business owners
            }
        )
        
        # If user already exists, update their info
        if not created:
            user.first_name = owner_name.split(' ')[0] if ' ' in owner_name else owner_name
            user.last_name = owner_name.split(' ')[1] if ' ' in owner_name else ''
            user.phone = owner_phone
            user.role = 'business_owner'  # Ensure role is set
            user.save()
        
        # Create business
        validated_data['owner'] = user
        business = super().create(validated_data)
        
        # Set business password if provided
        if password:
            business.business_password = password
            business.save()
        
        return business


class BusinessUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating businesses."""
    
    class Meta:
        model = Business
        fields = (
            'name', 'description', 'website', 'phone', 'email', 'address',
            'city', 'category', 'logo'
        )


class FavoriteSerializer(serializers.ModelSerializer):
    """Serializer for favorites."""
    business_name = serializers.CharField(source='business.name', read_only=True)
    business_city = serializers.CharField(source='business.city', read_only=True)
    business_category = serializers.CharField(source='business.category.name', read_only=True)
    
    class Meta:
        model = Favorite
        fields = ('id', 'business', 'business_name', 'business_city', 'business_category', 'created_at')
        read_only_fields = ('id', 'created_at')


class BusinessListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for business listings."""
    owner_name = serializers.CharField(source='owner.full_name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    average_rating = serializers.ReadOnlyField()
    review_count = serializers.ReadOnlyField()
    is_favorited = serializers.SerializerMethodField()
    
    class Meta:
        model = Business
        fields = (
            'id', 'name', 'category_name', 'city', 'phone', 'logo', 'status', 'owner',
            'average_rating', 'review_count', 'featured', 'is_favorited', 'owner_name',
            'description', 'address'
        )
    
    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Favorite.objects.filter(user=request.user, business=obj).exists()
        return False


class BusinessApprovalSerializer(serializers.ModelSerializer):
    """Serializer for business approval/rejection."""
    
    class Meta:
        model = Business
        fields = ['id', 'name', 'owner', 'status', 'rejection_reason', 'suspension_reason', 'created_at']
        read_only_fields = ['id', 'name', 'owner', 'created_at']


class BusinessDetailSerializer(serializers.ModelSerializer):
    """Detailed business serializer for admin management."""
    
    owner_email = serializers.EmailField(source='owner.email', read_only=True)
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    image_count = serializers.SerializerMethodField()
    product_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Business
        fields = [
            'id', 'name', 'description', 'website', 'phone', 'email',
            'address', 'city', 'category', 'category_name', 'status',
            'featured', 'owner', 'owner_email', 'owner_name',
            'rejection_reason', 'suspension_reason',
            'image_count', 'product_count', 'average_rating',
            'review_count', 'created_at', 'updated_at', 'products', 'services'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_image_count(self, obj):
        return obj.images.count()
    
    def get_product_count(self, obj):
        return obj.products.count()


class ServiceSerializer(serializers.ModelSerializer):
    """Serializer for business services."""
    
    class Meta:
        model = Service
        fields = [
            'id', 'business', 'name', 'description', 'price', 
            'duration', 'image', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'business', 'created_at', 'updated_at']


class ServiceListSerializer(serializers.ModelSerializer):
    """Serializer for global service listings including business info."""
    business_name = serializers.CharField(source='business.name', read_only=True)
    business_city = serializers.CharField(source='business.city', read_only=True)
    
    class Meta:
        model = Service
        fields = [
            'id', 'business', 'business_name', 'business_city', 'name', 
            'description', 'price', 'duration', 'image', 'is_active'
        ]
        read_only_fields = ['id', 'business', 'business_name', 'business_city']


class ProductInventorySerializer(serializers.ModelSerializer):
    """Serializer for product inventory management."""
    
    sales_count = serializers.SerializerMethodField()
    revenue = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price', 'image', 'in_stock',
            'sales_count', 'revenue', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_sales_count(self, obj):
        # This would be calculated from order items
        # For now, return 0 as placeholder
        return 0
    
    def get_revenue(self, obj):
        # This would be calculated from order items
        # For now, return 0.00 as placeholder
        return 0.00
