from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class SiteSettings(models.Model):
    """Site-wide settings and configuration."""
    
    # Site Information
    site_name = models.CharField(max_length=200, default='SSME Market')
    site_description = models.TextField(default='Small and Medium Enterprises Marketplace')
    contact_email = models.EmailField(default='admin@ssme.com')
    contact_phone = models.CharField(max_length=20, default='+233 20 123 4567')
    contact_address = models.TextField(default='Accra, Ghana')
    
    # Site Configuration
    site_url = models.URLField(default='https://ssme.com')
    logo = models.ImageField(upload_to='settings/', null=True, blank=True)
    favicon = models.ImageField(upload_to='settings/', null=True, blank=True)
    
    # Maintenance
    maintenance_mode = models.BooleanField(default=False)
    maintenance_message = models.TextField(default='Site is under maintenance. Please check back later.')
    
    # Registration Settings
    allow_user_registration = models.BooleanField(default=True)
    allow_business_registration = models.BooleanField(default=True)
    require_email_verification = models.BooleanField(default=True)
    auto_approve_businesses = models.BooleanField(default=False)
    
    # Business Settings
    max_businesses_per_user = models.IntegerField(default=1)
    business_approval_required = models.BooleanField(default=True)
    
    # Email Settings
    email_host = models.CharField(max_length=200, default='smtp.gmail.com')
    email_port = models.IntegerField(default=587)
    email_use_tls = models.BooleanField(default=True)
    email_host_user = models.CharField(max_length=200, blank=True)
    email_host_password = models.CharField(max_length=200, blank=True)
    default_from_email = models.EmailField(default='noreply@ssme.com')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        verbose_name = 'Site Settings'
        verbose_name_plural = 'Site Settings'
    
    def __str__(self):
        return self.site_name
    
    @classmethod
    def get_settings(cls):
        """Get or create the singleton settings instance."""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings


class NotificationSettings(models.Model):
    """Notification preferences and settings."""
    
    # Email Notifications
    email_notifications_enabled = models.BooleanField(default=True)
    order_notifications = models.BooleanField(default=True)
    business_registration_notifications = models.BooleanField(default=True)
    user_registration_notifications = models.BooleanField(default=True)
    review_notifications = models.BooleanField(default=True)
    system_notifications = models.BooleanField(default=True)
    
    # Push Notifications
    push_notifications_enabled = models.BooleanField(default=True)
    
    # Notification Templates
    welcome_email_template = models.TextField(blank=True)
    business_approval_template = models.TextField(blank=True)
    order_confirmation_template = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        verbose_name = 'Notification Settings'
        verbose_name_plural = 'Notification Settings'
    
    def __str__(self):
        return 'Notification Settings'
    
    @classmethod
    def get_settings(cls):
        """Get or create the singleton notification settings instance."""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings


class SecuritySettings(models.Model):
    """Security and authentication settings."""
    
    # Authentication
    two_factor_auth_enabled = models.BooleanField(default=False)
    session_timeout_minutes = models.IntegerField(default=30)
    max_login_attempts = models.IntegerField(default=5)
    lockout_duration_minutes = models.IntegerField(default=15)
    
    # Password Policy
    password_min_length = models.IntegerField(default=8)
    password_require_uppercase = models.BooleanField(default=True)
    password_require_lowercase = models.BooleanField(default=True)
    password_require_numbers = models.BooleanField(default=True)
    password_require_symbols = models.BooleanField(default=True)
    password_history_count = models.IntegerField(default=5)
    
    # Session Settings
    concurrent_sessions_allowed = models.IntegerField(default=3)
    remember_me_days = models.IntegerField(default=30)
    
    # API Settings
    api_rate_limit = models.IntegerField(default=100)  # requests per hour
    api_timeout_minutes = models.IntegerField(default=15)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        verbose_name = 'Security Settings'
        verbose_name_plural = 'Security Settings'
    
    def __str__(self):
        return 'Security Settings'
    
    @classmethod
    def get_settings(cls):
        """Get or create the singleton security settings instance."""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings


class BackupSettings(models.Model):
    """Backup and maintenance settings."""
    
    # Backup Configuration
    auto_backup_enabled = models.BooleanField(default=True)
    backup_frequency = models.CharField(
        max_length=20,
        choices=[
            ('hourly', 'Hourly'),
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
        ],
        default='daily'
    )
    backup_retention_days = models.IntegerField(default=30)
    
    # Backup Location
    backup_location = models.CharField(
        max_length=20,
        choices=[
            ('local', 'Local Storage'),
            ('cloud', 'Cloud Storage'),
            ('both', 'Both'),
        ],
        default='cloud'
    )
    
    # Cloud Settings
    cloud_provider = models.CharField(max_length=50, default='aws', blank=True)
    cloud_bucket = models.CharField(max_length=200, blank=True)
    cloud_access_key = models.CharField(max_length=200, blank=True)
    cloud_secret_key = models.CharField(max_length=200, blank=True)
    
    # Backup Status
    last_backup_time = models.DateTimeField(null=True, blank=True)
    last_backup_size = models.BigIntegerField(null=True, blank=True)
    backup_status = models.CharField(
        max_length=20,
        choices=[
            ('success', 'Success'),
            ('failed', 'Failed'),
            ('running', 'Running'),
            ('never', 'Never'),
        ],
        default='never'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        verbose_name = 'Backup Settings'
        verbose_name_plural = 'Backup Settings'
    
    def __str__(self):
        return 'Backup Settings'
    
    @classmethod
    def get_settings(cls):
        """Get or create the singleton backup settings instance."""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings
