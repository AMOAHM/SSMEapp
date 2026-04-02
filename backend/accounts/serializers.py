from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from businesses.models import Business
from django.contrib.auth.password_validation import validate_password
from .models import User


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'phone', 'role', 'password', 'password_confirm')
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match.")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(request=self.context.get('request'), username=email, password=password)
            
            if not user:
                raise serializers.ValidationError('Invalid credentials.')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled.')
            
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Must include email and password.')


class BusinessLoginSerializer(serializers.Serializer):
    """Serializer for business login using business password."""
    email = serializers.EmailField()
    business_password = serializers.CharField()
    
    def validate(self, attrs):
        email = attrs.get('email')
        business_password = attrs.get('business_password')
        
        if email and business_password:
            try:
                # Find user by email
                user = User.objects.get(email=email)
                
                # Check if user has a business (any status)
                business = Business.objects.filter(owner=user).first()
                if not business:
                    raise serializers.ValidationError('No business found for this account. Please register a business first.')
                
                # Check business status
                if business.status == 'pending':
                    raise serializers.ValidationError('Your business is pending approval. Please wait for admin approval before logging in.')
                elif business.status == 'rejected':
                    raise serializers.ValidationError('Your business application has been rejected. Please contact support for more information.')
                elif business.status == 'suspended':
                    raise serializers.ValidationError('Your business has been suspended. Please contact support.')
                elif business.status != 'approved':
                    raise serializers.ValidationError('Your business is not approved. Please wait for admin approval.')
                
                # Check business password
                if business.business_password != business_password:
                    raise serializers.ValidationError('Invalid business credentials.')
                
                attrs['user'] = user
                attrs['business'] = business
                return attrs
                
            except User.DoesNotExist:
                raise serializers.ValidationError('Invalid credentials.')
        else:
            raise serializers.ValidationError('Must include email and business password.')


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile."""
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'full_name', 'phone', 'role', 'is_verified', 'is_active', 'account_status', 'is_superuser', 'created_at')
        read_only_fields = ('id', 'email', 'is_verified', 'is_active', 'account_status', 'is_superuser', 'created_at')


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile."""
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'phone')

class AdminUserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for admins to update other user's profiles including passwords."""
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'phone', 'role', 'is_verified', 'password')
        
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
