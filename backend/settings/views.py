from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.contrib.auth import get_user_model

from .models import SiteSettings, NotificationSettings, SecuritySettings, BackupSettings
from .serializers import (
    SiteSettingsSerializer, NotificationSettingsSerializer, 
    SecuritySettingsSerializer, BackupSettingsSerializer, AllSettingsSerializer
)

User = get_user_model()


class SettingsViewSet(viewsets.ViewSet):
    """ViewSet for managing system settings."""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        """Only admins can manage settings."""
        if self.request.user.role not in ['admin', 'super_admin']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]
    
    def check_permissions(self, request):
        """Check if user has admin permissions."""
        if request.user.role not in ['admin', 'super_admin']:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Admin access required")
    
    @action(detail=False, methods=['get'])
    def all_settings(self, request):
        """Get all system settings."""
        try:
            site_settings = SiteSettings.get_settings()
            notification_settings = NotificationSettings.get_settings()
            security_settings = SecuritySettings.get_settings()
            backup_settings = BackupSettings.get_settings()
            
            data = {
                'site': SiteSettingsSerializer(site_settings).data,
                'notifications': NotificationSettingsSerializer(notification_settings).data,
                'security': SecuritySettingsSerializer(security_settings).data,
                'backup': BackupSettingsSerializer(backup_settings).data
            }
            
            return Response(data)
        except Exception as e:
            return Response(
                {'error': f'Failed to fetch settings: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get', 'patch'])
    def site(self, request):
        """Get or update site settings."""
        if request.method == 'GET':
            try:
                settings = SiteSettings.get_settings()
                serializer = SiteSettingsSerializer(settings)
                return Response(serializer.data)
            except Exception as e:
                return Response(
                    {'error': f'Failed to fetch site settings: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        elif request.method == 'PATCH':
            try:
                settings = SiteSettings.get_settings()
                serializer = SiteSettingsSerializer(settings, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save(updated_by=request.user)
                    return Response(serializer.data)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response(
                    {'error': f'Failed to update site settings: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
    
    @action(detail=False, methods=['get', 'patch'])
    def notifications(self, request):
        """Get or update notification settings."""
        if request.method == 'GET':
            try:
                settings = NotificationSettings.get_settings()
                serializer = NotificationSettingsSerializer(settings)
                return Response(serializer.data)
            except Exception as e:
                return Response(
                    {'error': f'Failed to fetch notification settings: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        elif request.method == 'PATCH':
            try:
                settings = NotificationSettings.get_settings()
                serializer = NotificationSettingsSerializer(settings, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save(updated_by=request.user)
                    return Response(serializer.data)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response(
                    {'error': f'Failed to update notification settings: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
    
    @action(detail=False, methods=['get', 'patch'])
    def security(self, request):
        """Get or update security settings."""
        if request.method == 'GET':
            try:
                settings = SecuritySettings.get_settings()
                serializer = SecuritySettingsSerializer(settings)
                return Response(serializer.data)
            except Exception as e:
                return Response(
                    {'error': f'Failed to fetch security settings: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        elif request.method == 'PATCH':
            try:
                settings = SecuritySettings.get_settings()
                serializer = SecuritySettingsSerializer(settings, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save(updated_by=request.user)
                    return Response(serializer.data)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response(
                    {'error': f'Failed to update security settings: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
    
    @action(detail=False, methods=['get', 'patch'])
    def backup(self, request):
        """Get or update backup settings."""
        if request.method == 'GET':
            try:
                settings = BackupSettings.get_settings()
                serializer = BackupSettingsSerializer(settings)
                return Response(serializer.data)
            except Exception as e:
                return Response(
                    {'error': f'Failed to fetch backup settings: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        elif request.method == 'PATCH':
            try:
                settings = BackupSettings.get_settings()
                serializer = BackupSettingsSerializer(settings, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save(updated_by=request.user)
                    return Response(serializer.data)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response(
                    {'error': f'Failed to update backup settings: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
    
    @action(detail=False, methods=['post'])
    def backup_now(self, request):
        """Trigger a manual backup."""
        try:
            settings = BackupSettings.get_settings()
            
            # Update backup status to running
            settings.backup_status = 'running'
            settings.updated_by = request.user
            settings.save()
            
            # Here you would implement actual backup logic
            # For now, we'll simulate a successful backup
            import random
            import time
            
            def perform_backup():
                time.sleep(2)  # Simulate backup time
                settings.last_backup_time = timezone.now()
                settings.last_backup_size = random.randint(1000000, 5000000)  # Random size in bytes
                settings.backup_status = 'success'
                settings.save()
            
            # Run backup in background (in production, use Celery or similar)
            import threading
            backup_thread = threading.Thread(target=perform_backup)
            backup_thread.start()
            
            return Response({
                'message': 'Backup initiated successfully',
                'status': 'running'
            })
            
        except Exception as e:
            # Update backup status to failed
            settings.backup_status = 'failed'
            settings.updated_by = request.user
            settings.save()
            
            return Response(
                {'error': f'Failed to initiate backup: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def test_email(self, request):
        """Test email configuration."""
        try:
            site_settings = SiteSettings.get_settings()
            
            from django.core.mail import send_mail
            from django.conf import settings as django_settings
            
            # Configure Django settings with site email settings
            # Configure Django settings with site email settings if provided, else use env defaults
            django_settings.EMAIL_HOST = site_settings.email_host if site_settings.email_host else django_settings.EMAIL_HOST
            django_settings.EMAIL_PORT = site_settings.email_port if site_settings.email_port else django_settings.EMAIL_PORT
            django_settings.EMAIL_USE_TLS = site_settings.email_use_tls
            django_settings.EMAIL_HOST_USER = site_settings.email_host_user if site_settings.email_host_user else django_settings.EMAIL_HOST_USER
            django_settings.EMAIL_HOST_PASSWORD = site_settings.email_host_password if site_settings.email_host_password else django_settings.EMAIL_HOST_PASSWORD
            
            # Send test email
            send_mail(
                'SSME Market - Test Email',
                'This is a test email to verify your email configuration is working correctly.',
                site_settings.default_from_email,
                [request.user.email],
                fail_silently=False,
            )
            
            return Response({'message': 'Test email sent successfully'})
            
        except Exception as e:
            return Response(
                {'error': f'Failed to send test email: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def reset_to_defaults(self, request):
        """Reset all settings to default values."""
        try:
            # Delete existing settings to trigger recreation with defaults
            SiteSettings.objects.all().delete()
            NotificationSettings.objects.all().delete()
            SecuritySettings.objects.all().delete()
            BackupSettings.objects.all().delete()
            
            # Recreate with defaults
            SiteSettings.get_settings()
            NotificationSettings.get_settings()
            SecuritySettings.get_settings()
            BackupSettings.get_settings()
            
            return Response({'message': 'Settings reset to defaults successfully'})
            
        except Exception as e:
            return Response(
                {'error': f'Failed to reset settings: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
