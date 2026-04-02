from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.validators import RegexValidator
import uuid


class User(AbstractUser):
    """Enhanced custom user model for SSME platform."""
    
    USER_ROLES = (
        ('customer', _('Customer')),
        ('business', _('Business Owner')),
        ('admin', _('Administrator')),
        ('super_admin', _('Super Administrator')),
    )
    
    ACCOUNT_STATUS = (
        ('active', _('Active')),
        ('inactive', _('Inactive')),
        ('suspended', _('Suspended')),
        ('pending_verification', _('Pending Verification')),
    )
    
    # Basic Information
    email = models.EmailField(_('email address'), unique=True)
    phone = models.CharField(
        _('phone number'), 
        max_length=20, 
        blank=True,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
        )]
    )
    
    # Profile Information
    profile_picture = models.ImageField(
        _('profile picture'), 
        upload_to='profile_pics/', 
        blank=True, 
        null=True
    )
    bio = models.TextField(_('bio'), max_length=500, blank=True)
    date_of_birth = models.DateField(_('date of birth'), blank=True, null=True)
    gender = models.CharField(
        _('gender'),
        max_length=20,
        choices=[
            ('male', _('Male')),
            ('female', _('Female')),
            ('other', _('Other')),
            ('prefer_not_to_say', _('Prefer not to say')),
        ],
        blank=True
    )
    
    # Location Information
    country = models.CharField(_('country'), max_length=100, blank=True)
    state = models.CharField(_('state'), max_length=100, blank=True)
    city = models.CharField(_('city'), max_length=100, blank=True)
    address = models.TextField(_('address'), blank=True)
    postal_code = models.CharField(_('postal code'), max_length=20, blank=True)
    
    # Business Information (for business owners)
    business_name = models.CharField(_('business name'), max_length=200, blank=True)
    business_license = models.CharField(_('business license'), max_length=100, blank=True)
    business_description = models.TextField(_('business description'), blank=True)
    
    # System Fields
    uuid = models.UUIDField(_('unique identifier'), default=uuid.uuid4, unique=False)
    role = models.CharField(_('user role'), max_length=20, choices=USER_ROLES, default='customer')
    account_status = models.CharField(
        _('account status'), 
        max_length=25, 
        choices=ACCOUNT_STATUS, 
        default='pending_verification'
    )
    is_verified = models.BooleanField(_('email verified'), default=False)
    is_phone_verified = models.BooleanField(_('phone verified'), default=False)
    is_business_verified = models.BooleanField(_('business verified'), default=False)
    
    # Django staff and superuser fields for admin access
    is_staff = models.BooleanField(_('staff status'), default=False)
    is_superuser = models.BooleanField(_('superuser status'), default=False)
    
    # Security Fields
    last_login_ip = models.GenericIPAddressField(_('last login IP'), blank=True, null=True)
    failed_login_attempts = models.PositiveIntegerField(_('failed login attempts'), default=0)
    locked_until = models.DateTimeField(_('locked until'), blank=True, null=True)
    password_changed_at = models.DateTimeField(_('password changed at'), default=timezone.now)
    two_factor_enabled = models.BooleanField(_('two-factor enabled'), default=False)
    two_factor_secret = models.CharField(_('two-factor secret'), max_length=32, blank=True)
    
    # Password Reset & Verification Tokens
    password_reset_token = models.CharField(_('password reset token'), max_length=100, blank=True, null=True)
    password_reset_expires = models.DateTimeField(_('password reset expires'), blank=True, null=True)
    email_verification_token = models.CharField(_('email verification token'), max_length=100, blank=True, null=True)
    
    # Activity Tracking
    last_activity = models.DateTimeField(_('last activity'), blank=True, null=True)
    login_count = models.PositiveIntegerField(_('login count'), default=0)
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    deleted_at = models.DateTimeField(_('deleted at'), blank=True, null=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role']),
            models.Index(fields=['account_status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def is_locked(self):
        from django.utils import timezone
        return self.locked_until and self.locked_until > timezone.now()
    
    def is_business_owner(self):
        return self.role == 'business'
    
    def is_admin_user(self):
        return self.role in ['admin', 'super_admin']
    
    def is_super_admin(self):
        return self.role == 'super_admin'
    
    def has_business_access(self):
        """Check if user can access business features."""
        return self.role in ['business', 'admin', 'super_admin']
    
    def has_admin_access(self):
        """Check if user has admin-level access."""
        return self.role in ['admin', 'super_admin']
    
    def has_super_admin_access(self):
        """Check if user has super admin access."""
        return self.role == 'super_admin'
    
    def increment_login_count(self):
        """Increment login count and update last activity."""
        self.login_count += 1
        self.last_activity = timezone.now()
        self.save(update_fields=['login_count', 'last_activity'])
    
    def reset_failed_login_attempts(self):
        """Reset failed login attempts."""
        self.failed_login_attempts = 0
        self.locked_until = None
        self.save(update_fields=['failed_login_attempts', 'locked_until'])
    
    def increment_failed_login_attempts(self):
        """Increment failed login attempts and lock account if necessary."""
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= 5:
            from django.utils import timezone
            from datetime import timedelta
            self.locked_until = timezone.now() + timedelta(minutes=30)
        self.save(update_fields=['failed_login_attempts', 'locked_until'])


class UserProfile(models.Model):
    """Extended user profile with additional information."""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='extended_profile')
    
    # Preferences
    language = models.CharField(_('language'), max_length=10, default='en')
    timezone = models.CharField(_('timezone'), max_length=50, default='UTC')
    email_notifications = models.BooleanField(_('email notifications'), default=True)
    sms_notifications = models.BooleanField(_('SMS notifications'), default=False)
    push_notifications = models.BooleanField(_('push notifications'), default=True)
    
    # Social Links
    website = models.URLField(_('website'), blank=True)
    linkedin = models.URLField(_('LinkedIn'), blank=True)
    twitter = models.URLField(_('Twitter'), blank=True)
    facebook = models.URLField(_('Facebook'), blank=True)
    instagram = models.URLField(_('Instagram'), blank=True)
    
    # Additional Info
    skills = models.TextField(_('skills'), blank=True, help_text="Comma-separated skills")
    experience_years = models.PositiveIntegerField(_('years of experience'), default=0)
    education = models.TextField(_('education'), blank=True)
    certifications = models.TextField(_('certifications'), blank=True)
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('User Profile')
        verbose_name_plural = _('User Profiles')
    
    def __str__(self):
        return f"{self.user.email} - Profile"


class UserActivity(models.Model):
    """Track user activities for audit purposes."""
    
    ACTION_TYPES = (
        ('login', _('Login')),
        ('logout', _('Logout')),
        ('password_change', _('Password Change')),
        ('profile_update', _('Profile Update')),
        ('account_created', _('Account Created')),
        ('account_deleted', _('Account Deleted')),
        ('account_suspended', _('Account Suspended')),
        ('account_reactivated', _('Account Reactivated')),
        ('email_verified', _('Email Verified')),
        ('phone_verified', _('Phone Verified')),
        ('business_verified', _('Business Verified')),
        ('two_factor_enabled', _('Two-Factor Enabled')),
        ('two_factor_disabled', _('Two-Factor Disabled')),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    action_type = models.CharField(_('action type'), max_length=25, choices=ACTION_TYPES)
    description = models.TextField(_('description'), blank=True)
    ip_address = models.GenericIPAddressField(_('IP address'), blank=True, null=True)
    user_agent = models.TextField(_('user agent'), blank=True)
    timestamp = models.DateTimeField(_('timestamp'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('User Activity')
        verbose_name_plural = _('User Activities')
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action_type']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.get_action_type_display()} - {self.timestamp}"
