from django.contrib import admin
from .models import SiteSettings, NotificationSettings, SecuritySettings, BackupSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ['site_name', 'contact_email', 'maintenance_mode', 'updated_at']
    search_fields = ['site_name', 'contact_email']
    list_filter = ['maintenance_mode', 'allow_user_registration', 'allow_business_registration']
    
    def has_add_permission(self, request):
        # Prevent adding multiple site settings instances
        return not SiteSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Prevent deleting the only site settings instance
        return SiteSettings.objects.count() > 1


@admin.register(NotificationSettings)
class NotificationSettingsAdmin(admin.ModelAdmin):
    list_display = ['email_notifications_enabled', 'push_notifications_enabled', 'updated_at']
    list_filter = ['email_notifications_enabled', 'push_notifications_enabled']
    
    def has_add_permission(self, request):
        return not NotificationSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return NotificationSettings.objects.count() > 1


@admin.register(SecuritySettings)
class SecuritySettingsAdmin(admin.ModelAdmin):
    list_display = ['two_factor_auth_enabled', 'session_timeout_minutes', 'max_login_attempts', 'updated_at']
    list_filter = ['two_factor_auth_enabled']
    
    def has_add_permission(self, request):
        return not SecuritySettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return SecuritySettings.objects.count() > 1


@admin.register(BackupSettings)
class BackupSettingsAdmin(admin.ModelAdmin):
    list_display = ['auto_backup_enabled', 'backup_frequency', 'backup_location', 'backup_status', 'last_backup_time']
    list_filter = ['auto_backup_enabled', 'backup_frequency', 'backup_location', 'backup_status']
    
    def has_add_permission(self, request):
        return not BackupSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return BackupSettings.objects.count() > 1
