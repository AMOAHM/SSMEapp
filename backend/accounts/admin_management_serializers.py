from rest_framework import serializers
from django.contrib.auth import get_user_model
from businesses.models import Business, Product, BusinessImage

User = get_user_model()


class BusinessApprovalSerializer(serializers.ModelSerializer):
    """Serializer for business approval/rejection."""
    
    class Meta:
        model = Business
        fields = ['id', 'name', 'owner', 'status', 'created_at']
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
            'image_count', 'product_count', 'average_rating',
            'review_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_image_count(self, obj):
        return obj.images.count()
    
    def get_product_count(self, obj):
        return obj.products.count()


class ProductManagementSerializer(serializers.ModelSerializer):
    """Enhanced product serializer for management."""
    
    business_name = serializers.CharField(source='business.name', read_only=True)
    business_owner = serializers.CharField(source='business.owner.email', read_only=True)
    business_status = serializers.CharField(source='business.status', read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price', 'image', 'in_stock',
            'business', 'business_name', 'business_owner', 'business_status',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_business(self, value):
        """Validate that user can add products to this business."""
        user = self.context['request'].user
        
        if user.role == 'business':
            try:
                business = Business.objects.get(id=value, owner=user, status='approved')
                return business
            except Business.DoesNotExist:
                raise serializers.ValidationError(
                    "You can only add products to your approved businesses."
                )
        elif user.role in ['admin', 'super_admin']:
            try:
                return Business.objects.get(id=value)
            except Business.DoesNotExist:
                raise serializers.ValidationError("Business does not exist.")
        else:
            raise serializers.ValidationError(
                "Only business owners and admins can add products."
            )


class BusinessImageSerializer(serializers.ModelSerializer):
    """Serializer for business images."""
    
    class Meta:
        model = BusinessImage
        fields = ['id', 'image', 'alt_text', 'created_at']
        read_only_fields = ['id', 'created_at']


class AdminUserSerializer(serializers.ModelSerializer):
    """Enhanced user serializer for admin management."""
    
    full_name = serializers.CharField(read_only=True)
    business_count = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'full_name', 'phone', 'role', 'account_status',
            'is_verified', 'is_phone_verified', 'is_business_verified',
            'business_count', 'created_at', 'last_login'
        ]
        read_only_fields = ['id', 'created_at', 'last_login']
    
    def get_business_count(self, obj):
        return obj.businesses.count()


class BusinessRegistrationSerializer(serializers.ModelSerializer):
    """Enhanced serializer for business registration."""
    
    class Meta:
        model = Business
        fields = [
            'name', 'description', 'website', 'phone', 'email',
            'address', 'city', 'category'
        ]
    
    def validate(self, attrs):
        """Validate business registration data."""
        user = self.context['request'].user
        
        if user.role != 'business':
            raise serializers.ValidationError(
                "Only business users can register businesses."
            )
        
        # Check if user already has pending business
        if Business.objects.filter(owner=user, status='pending').exists():
            raise serializers.ValidationError(
                "You already have a business pending approval."
            )
        
        return attrs


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
        # For now, return 0 as placeholder
        return 0.00
