from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import User

User = get_user_model()

class AdminSerializer(serializers.ModelSerializer):
    """Serializer for admin users."""
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'phone', 'role',
            'is_verified', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class AdminCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating admin users."""
    
    class Meta:
        model = User
        fields = [
            'email', 'username', 'first_name', 'last_name', 'phone', 'password',
            'role', 'is_verified', 'is_active'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password')
        # Use username if provided, otherwise use email as username
        username = validated_data.get('username', validated_data['email'])
        user = User.objects.create_user(
            username=username,
            email=validated_data['email'],
            password=password,
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone=validated_data.get('phone', ''),
            role=validated_data.get('role', 'admin'),
            is_verified=validated_data.get('is_verified', True),
            is_active=validated_data.get('is_active', True)
        )
        return user

class AdminUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating admin users."""
    
    class Meta:
        model = User
        fields = [
            'email', 'first_name', 'last_name', 'phone', 'role',
            'is_verified', 'is_active'
        ]

    def update(self, instance, validated_data):
        # Prevent role changes for superusers
        if instance.is_superuser and 'role' in validated_data:
            validated_data.pop('role')
        
        return super().update(instance, validated_data)
