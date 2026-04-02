from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Review

User = get_user_model()


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for reviews."""
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    business_name = serializers.CharField(source='business.name', read_only=True)
    
    class Meta:
        model = Review
        fields = (
            'id', 'user', 'user_name', 'business', 'business_name',
            'rating', 'comment', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')


class ReviewCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating reviews."""
    
    class Meta:
        model = Review
        fields = ('business', 'rating', 'comment')
    
    def validate_business(self, value):
        """Validate that the business is approved."""
        if value.status != 'approved':
            raise serializers.ValidationError("You can only review approved businesses.")
        return value
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
