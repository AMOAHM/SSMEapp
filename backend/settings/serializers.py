from rest_framework import serializers
from .models import SiteSettings, NotificationSettings, SecuritySettings, BackupSettings


class SiteSettingsSerializer(serializers.ModelSerializer):
    """Serializer for site settings."""
    
    class Meta:
        model = SiteSettings
        fields = [
            'id', 'site_name', 'site_description', 'contact_email', 'contact_phone',
            'contact_address', 'site_url', 'logo', 'favicon', 'maintenance_mode',
            'maintenance_message', 'allow_user_registration', 'allow_business_registration',
            'require_email_verification', 'auto_approve_businesses', 'max_businesses_per_user',
            'business_approval_required', 'email_host', 'email_port', 'email_use_tls',
            'email_host_user', 'default_from_email', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class NotificationSettingsSerializer(serializers.ModelSerializer):
    """Serializer for notification settings."""
    
    class Meta:
        model = NotificationSettings
        fields = [
            'id', 'email_notifications_enabled', 'order_notifications',
            'business_registration_notifications', 'user_registration_notifications',
            'review_notifications', 'system_notifications', 'push_notifications_enabled',
            'welcome_email_template', 'business_approval_template', 'order_confirmation_template',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SecuritySettingsSerializer(serializers.ModelSerializer):
    """Serializer for security settings."""
    
    password_policy = serializers.SerializerMethodField()
    
    class Meta:
        model = SecuritySettings
        fields = [
            'id', 'two_factor_auth_enabled', 'session_timeout_minutes', 'max_login_attempts',
            'lockout_duration_minutes', 'password_min_length', 'password_require_uppercase',
            'password_require_lowercase', 'password_require_numbers', 'password_require_symbols',
            'password_history_count', 'concurrent_sessions_allowed', 'remember_me_days',
            'api_rate_limit', 'api_timeout_minutes', 'password_policy', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_password_policy(self, obj):
        """Determine password policy based on requirements."""
        requirements = []
        if obj.password_require_uppercase:
            requirements.append('uppercase')
        if obj.password_require_lowercase:
            requirements.append('lowercase')
        if obj.password_require_numbers:
            requirements.append('numbers')
        if obj.password_require_symbols:
            requirements.append('symbols')
        
        if len(requirements) >= 4:
            return 'very-strong'
        elif len(requirements) >= 3:
            return 'strong'
        else:
            return 'basic'


class BackupSettingsSerializer(serializers.ModelSerializer):
    """Serializer for backup settings."""
    
    last_backup = serializers.SerializerMethodField()
    
    class Meta:
        model = BackupSettings
        fields = [
            'id', 'auto_backup_enabled', 'backup_frequency', 'backup_retention_days',
            'backup_location', 'cloud_provider', 'cloud_bucket', 'last_backup',
            'last_backup_time', 'last_backup_size', 'backup_status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'last_backup_time', 'last_backup_size', 'backup_status', 'created_at', 'updated_at']
    
    def get_last_backup(self, obj):
        """Format last backup time."""
        if obj.last_backup_time:
            return obj.last_backup_time.strftime('%Y-%m-%d %I:%M %p')
        return 'Never'


class AllSettingsSerializer(serializers.Serializer):
    """Serializer for all settings combined."""
    
    site = SiteSettingsSerializer(read_only=True)
    notifications = NotificationSettingsSerializer(read_only=True)
    security = SecuritySettingsSerializer(read_only=True)
    backup = BackupSettingsSerializer(read_only=True)
