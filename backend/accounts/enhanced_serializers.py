from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User, UserProfile, UserActivity


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Enhanced serializer for user registration."""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = (
            'email', 'username', 'first_name', 'last_name', 'phone', 'role',
            'password', 'password_confirm', 'country', 'state', 'city', 'date_of_birth', 'gender'
        )
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match.")
        return attrs
    
    def validate_email(self, value):
        """Validate email is unique and properly formatted."""
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value.lower()
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        
        # Create user profile
        UserProfile.objects.create(user=user)
        
        # Log activity
        UserActivity.objects.create(
            user=user,
            action_type='account_created',
            description=f"New {user.role} account created"
        )
        
        return user


class UserLoginSerializer(serializers.Serializer):
    """Enhanced serializer for user login."""
    email = serializers.EmailField()
    password = serializers.CharField()
    remember_me = serializers.BooleanField(default=False)
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            email = email.lower()
            user = authenticate(request=self.context.get('request'), username=email, password=password)
            
            if not user:
                # Increment failed login attempts
                try:
                    user_obj = User.objects.get(email=email)
                    user_obj.increment_failed_login_attempts()
                except User.DoesNotExist:
                    pass
                raise serializers.ValidationError('Invalid credentials.')
            
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled.')
            
            if user.is_locked:
                raise serializers.ValidationError('Account is temporarily locked due to multiple failed login attempts.')
            
            if user.account_status != 'active':
                raise serializers.ValidationError(f'Account is {user.get_account_status_display()}.')
            
            # Reset failed login attempts on successful login
            user.reset_failed_login_attempts()
            
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Must include email and password.')


class UserProfileSerializer(serializers.ModelSerializer):
    """Enhanced serializer for user profile."""
    full_name = serializers.ReadOnlyField()
    extended_profile = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = (
            'id', 'uuid', 'email', 'username', 'first_name', 'last_name', 'full_name',
            'phone', 'role', 'account_status', 'is_verified', 'is_phone_verified', 
            'is_business_verified', 'profile_picture', 'bio', 'date_of_birth', 'gender',
            'country', 'state', 'city', 'address', 'postal_code', 'business_name',
            'business_license', 'business_description', 'two_factor_enabled',
            'login_count', 'last_activity', 'created_at', 'updated_at', 'extended_profile'
        )
        read_only_fields = (
            'id', 'uuid', 'email', 'role', 'account_status', 'is_verified',
            'is_phone_verified', 'is_business_verified', 'login_count', 'last_activity',
            'created_at', 'updated_at'
        )
    
    def get_extended_profile(self, obj):
        """Get user's extended profile if it exists."""
        try:
            profile = obj.extended_profile
            return {
                'language': profile.language,
                'timezone': profile.timezone,
                'email_notifications': profile.email_notifications,
                'sms_notifications': profile.sms_notifications,
                'push_notifications': profile.push_notifications,
                'website': profile.website,
                'linkedin': profile.linkedin,
                'twitter': profile.twitter,
                'facebook': profile.facebook,
                'instagram': profile.instagram,
                'skills': profile.skills,
                'experience_years': profile.experience_years,
                'education': profile.education,
                'certifications': profile.certifications
            }
        except UserProfile.DoesNotExist:
            return None


class UserUpdateSerializer(serializers.ModelSerializer):
    """Enhanced serializer for updating user profile."""
    extended_profile = serializers.JSONField(required=False)
    
    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'phone', 'profile_picture', 'bio', 
            'date_of_birth', 'gender', 'country', 'state', 'city', 'address', 
            'postal_code', 'business_name', 'business_license', 'business_description',
            'extended_profile'
        )
    
    def update(self, instance, validated_data):
        extended_profile_data = validated_data.pop('extended_profile', None)
        
        # Update user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update extended profile
        if extended_profile_data:
            profile, created = UserProfile.objects.get_or_create(user=instance)
            for attr, value in extended_profile_data.items():
                if hasattr(profile, attr):
                    setattr(profile, attr, value)
            profile.save()
        
        # Log activity
        UserActivity.objects.create(
            user=instance,
            action_type='profile_update',
            description="User profile updated"
        )
        
        return instance


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for password change."""
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("New passwords don't match.")
        return attrs
    
    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value
    
    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        
        # Log activity
        UserActivity.objects.create(
            user=user,
            action_type='password_change',
            description="Password changed successfully"
        )


class UserProfileExtendedSerializer(serializers.ModelSerializer):
    """Serializer for extended user profile."""
    
    class Meta:
        model = UserProfile
        fields = (
            'language', 'timezone', 'email_notifications', 'sms_notifications',
            'push_notifications', 'website', 'linkedin', 'twitter', 'facebook',
            'instagram', 'skills', 'experience_years', 'education', 'certifications'
        )


class UserActivitySerializer(serializers.ModelSerializer):
    """Serializer for user activity tracking."""
    
    class Meta:
        model = UserActivity
        fields = (
            'id', 'action_type', 'description', 'ip_address', 'user_agent', 'timestamp'
        )
        read_only_fields = ('id', 'timestamp')


class AdminUserSerializer(serializers.ModelSerializer):
    """Enhanced serializer for admin user management."""
    full_name = serializers.ReadOnlyField()
    extended_profile = UserProfileExtendedSerializer(source='extended_profile', read_only=True)
    activities_count = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = (
            'id', 'uuid', 'email', 'username', 'first_name', 'last_name', 'full_name',
            'phone', 'role', 'account_status', 'is_active', 'is_verified', 'is_phone_verified',
            'is_business_verified', 'profile_picture', 'bio', 'date_of_birth', 'gender',
            'country', 'state', 'city', 'business_name', 'business_license', 'business_description',
            'two_factor_enabled', 'failed_login_attempts', 'locked_until', 'login_count',
            'last_activity', 'last_login_ip', 'created_at', 'updated_at', 'extended_profile',
            'activities_count'
        )
    
    def get_activities_count(self, obj):
        """Get count of user activities."""
        return obj.activities.count()


class AdminUserCreateSerializer(serializers.ModelSerializer):
    """Serializer for admin user creation."""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    
    class Meta:
        model = User
        fields = (
            'email', 'username', 'first_name', 'last_name', 'phone', 'role', 'password',
            'is_active', 'is_verified', 'is_phone_verified', 'is_business_verified'
        )
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        
        # Create user profile
        UserProfile.objects.create(user=user)
        
        # Log activity
        UserActivity.objects.create(
            user=self.context['request'].user,
            action_type='account_created',
            description=f"Admin created {user.role} account: {user.email}"
        )
        
        return user


class AdminUserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for admin user updates."""
    
    class Meta:
        model = User
        fields = (
            'username', 'first_name', 'last_name', 'phone', 'role', 'account_status',
            'is_active', 'is_verified', 'is_phone_verified', 'is_business_verified',
            'two_factor_enabled', 'country', 'state', 'city', 'business_name',
            'business_license', 'business_description'
        )
    
    def update(self, instance, validated_data):
        old_status = instance.account_status
        instance = super().update(instance, validated_data)
        
        # Log status changes
        if old_status != instance.account_status:
            action_map = {
                'suspended': 'account_suspended',
                'active': 'account_reactivated'
            }
            action = action_map.get(instance.account_status)
            if action:
                UserActivity.objects.create(
                    user=self.context['request'].user,
                    action_type=action,
                    description=f"Account {instance.account_status}: {instance.email}"
                )
        
        return instance
