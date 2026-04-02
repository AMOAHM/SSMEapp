from rest_framework import serializers
from .models import Category


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model."""
    business_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Category
        fields = ('id', 'name', 'description', 'icon', 'is_active', 'business_count', 'created_at')
        read_only_fields = ('id', 'created_at')
