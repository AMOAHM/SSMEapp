# Django signals for the settings app
# This file can be used to define signal handlers for the settings app

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import SiteSettings, NotificationSettings, SecuritySettings, BackupSettings


@receiver(post_save, sender=SiteSettings)
def site_settings_saved(sender, instance, **kwargs):
    """Signal handler for when site settings are saved."""
    print(f"Site settings updated by {instance.updated_by}")


@receiver(post_save, sender=NotificationSettings)
def notification_settings_saved(sender, instance, **kwargs):
    """Signal handler for when notification settings are saved."""
    print(f"Notification settings updated by {instance.updated_by}")


@receiver(post_save, sender=SecuritySettings)
def security_settings_saved(sender, instance, **kwargs):
    """Signal handler for when security settings are saved."""
    print(f"Security settings updated by {instance.updated_by}")


@receiver(post_save, sender=BackupSettings)
def backup_settings_saved(sender, instance, **kwargs):
    """Signal handler for when backup settings are saved."""
    print(f"Backup settings updated by {instance.updated_by}")
