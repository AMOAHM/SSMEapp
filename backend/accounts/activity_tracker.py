from django.utils import timezone
from django.db import models
from django.contrib.auth import get_user_model
from django.core.serializers.json import DjangoJSONEncoder
import json
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class ActivityTracker:
    """Service for tracking user activities and system events."""
    
    @staticmethod
    def log_activity(user, action_type, description="", details=None, ip_address=None, user_agent=None):
        """Log a user activity."""
        try:
            from .models import UserActivity
            
            activity = UserActivity.objects.create(
                user=user,
                action_type=action_type,
                description=description,
                details=details or {},
                ip_address=ip_address,
                user_agent=user_agent or ""
            )
            
            logger.info(f"Activity logged: {user.email} - {action_type}")
            return activity
            
        except Exception as e:
            logger.error(f"Failed to log activity: {str(e)}")
            return None
    
    @staticmethod
    def log_login(user, request=None):
        """Log user login."""
        ip_address = ActivityTracker.get_client_ip(request) if request else None
        user_agent = request.META.get('HTTP_USER_AGENT', '') if request else ''
        
        return ActivityTracker.log_activity(
            user=user,
            action_type='login',
            description="User logged in successfully",
            details={
                'login_method': 'password',
                'timestamp': timezone.now().isoformat()
            },
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    @staticmethod
    def log_logout(user, request=None):
        """Log user logout."""
        ip_address = ActivityTracker.get_client_ip(request) if request else None
        user_agent = request.META.get('HTTP_USER_AGENT', '') if request else ''
        
        return ActivityTracker.log_activity(
            user=user,
            action_type='logout',
            description="User logged out",
            details={
                'timestamp': timezone.now().isoformat()
            },
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    @staticmethod
    def log_password_change(user, request=None, success=True):
        """Log password change."""
        ip_address = ActivityTracker.get_client_ip(request) if request else None
        user_agent = request.META.get('HTTP_USER_AGENT', '') if request else ''
        
        return ActivityTracker.log_activity(
            user=user,
            action_type='password_change',
            description="Password changed successfully" if success else "Password change failed",
            details={
                'success': success,
                'timestamp': timezone.now().isoformat()
            },
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    @staticmethod
    def log_profile_update(user, changed_fields=None, request=None):
        """Log profile update."""
        ip_address = ActivityTracker.get_client_ip(request) if request else None
        user_agent = request.META.get('HTTP_USER_AGENT', '') if request else ''
        
        return ActivityTracker.log_activity(
            user=user,
            action_type='profile_update',
            description="User profile updated",
            details={
                'changed_fields': changed_fields or [],
                'timestamp': timezone.now().isoformat()
            },
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    @staticmethod
    def log_account_created(user, created_by=None, request=None):
        """Log account creation."""
        ip_address = ActivityTracker.get_client_ip(request) if request else None
        user_agent = request.META.get('HTTP_USER_AGENT', '') if request else ''
        
        return ActivityTracker.log_activity(
            user=user,
            action_type='account_created',
            description=f"Account created for {user.email}",
            details={
                'created_by': created_by.email if created_by else 'self',
                'user_role': user.role,
                'timestamp': timezone.now().isoformat()
            },
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    @staticmethod
    def log_account_suspended(user, suspended_by=None, reason="", request=None):
        """Log account suspension."""
        ip_address = ActivityTracker.get_client_ip(request) if request else None
        user_agent = request.META.get('HTTP_USER_AGENT', '') if request else ''
        
        return ActivityTracker.log_activity(
            user=user,
            action_type='account_suspended',
            description=f"Account suspended: {user.email}",
            details={
                'suspended_by': suspended_by.email if suspended_by else 'system',
                'reason': reason,
                'timestamp': timezone.now().isoformat()
            },
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    @staticmethod
    def log_account_reactivated(user, reactivated_by=None, request=None):
        """Log account reactivation."""
        ip_address = ActivityTracker.get_client_ip(request) if request else None
        user_agent = request.META.get('HTTP_USER_AGENT', '') if request else ''
        
        return ActivityTracker.log_activity(
            user=user,
            action_type='account_reactivated',
            description=f"Account reactivated: {user.email}",
            details={
                'reactivated_by': reactivated_by.email if reactivated_by else 'system',
                'timestamp': timezone.now().isoformat()
            },
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    @staticmethod
    def log_email_verified(user, request=None):
        """Log email verification."""
        ip_address = ActivityTracker.get_client_ip(request) if request else None
        user_agent = request.META.get('HTTP_USER_AGENT', '') if request else ''
        
        return ActivityTracker.log_activity(
            user=user,
            action_type='email_verified',
            description="Email address verified",
            details={
                'timestamp': timezone.now().isoformat()
            },
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    @staticmethod
    def log_phone_verified(user, request=None):
        """Log phone verification."""
        ip_address = ActivityTracker.get_client_ip(request) if request else None
        user_agent = request.META.get('HTTP_USER_AGENT', '') if request else ''
        
        return ActivityTracker.log_activity(
            user=user,
            action_type='phone_verified',
            description="Phone number verified",
            details={
                'timestamp': timezone.now().isoformat()
            },
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    @staticmethod
    def log_business_verified(user, request=None):
        """Log business verification."""
        ip_address = ActivityTracker.get_client_ip(request) if request else None
        user_agent = request.META.get('HTTP_USER_AGENT', '') if request else ''
        
        return ActivityTracker.log_activity(
            user=user,
            action_type='business_verified',
            description="Business verified",
            details={
                'timestamp': timezone.now().isoformat()
            },
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    @staticmethod
    def log_two_factor_enabled(user, request=None):
        """Log 2FA enablement."""
        ip_address = ActivityTracker.get_client_ip(request) if request else None
        user_agent = request.META.get('HTTP_USER_AGENT', '') if request else ''
        
        return ActivityTracker.log_activity(
            user=user,
            action_type='two_factor_enabled',
            description="Two-factor authentication enabled",
            details={
                'timestamp': timezone.now().isoformat()
            },
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    @staticmethod
    def log_two_factor_disabled(user, request=None):
        """Log 2FA disablement."""
        ip_address = ActivityTracker.get_client_ip(request) if request else None
        user_agent = request.META.get('HTTP_USER_AGENT', '') if request else ''
        
        return ActivityTracker.log_activity(
            user=user,
            action_type='two_factor_disabled',
            description="Two-factor authentication disabled",
            details={
                'timestamp': timezone.now().isoformat()
            },
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    @staticmethod
    def log_failed_login(email, ip_address=None, user_agent="", reason="invalid_credentials"):
        """Log failed login attempt."""
        try:
            from .models import FailedLoginAttempt
            
            FailedLoginAttempt.objects.create(
                email=email,
                ip_address=ip_address,
                user_agent=user_agent,
                reason=reason,
                timestamp=timezone.now()
            )
            
            logger.warning(f"Failed login attempt: {email} from {ip_address}")
            
        except Exception as e:
            logger.error(f"Failed to log failed login: {str(e)}")
    
    @staticmethod
    def log_permission_change(changed_by, target_user, action, details=None, request=None):
        """Log permission changes."""
        ip_address = ActivityTracker.get_client_ip(request) if request else None
        user_agent = request.META.get('HTTP_USER_AGENT', '') if request else ''
        
        return ActivityTracker.log_activity(
            user=target_user,
            action_type='permission_change',
            description=f"Permission {action}: {target_user.email}",
            details={
                'changed_by': changed_by.email,
                'action': action,
                'details': details or {},
                'timestamp': timezone.now().isoformat()
            },
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    @staticmethod
    def log_system_event(event_type, description, details=None, user=None):
        """Log system-level events."""
        try:
            from .models import SystemEvent
            
            SystemEvent.objects.create(
                event_type=event_type,
                description=description,
                details=details or {},
                user=user,
                timestamp=timezone.now()
            )
            
            logger.info(f"System event logged: {event_type} - {description}")
            
        except Exception as e:
            logger.error(f"Failed to log system event: {str(e)}")
    
    @staticmethod
    def get_client_ip(request):
        """Get client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    @staticmethod
    def get_user_activities(user, limit=50, action_types=None):
        """Get user activities with optional filtering."""
        from .models import UserActivity
        
        queryset = UserActivity.objects.filter(user=user)
        
        if action_types:
            queryset = queryset.filter(action_type__in=action_types)
        
        return queryset.order_by('-timestamp')[:limit]
    
    @staticmethod
    def get_recent_activities(limit=100, action_types=None):
        """Get recent activities across all users."""
        from .models import UserActivity
        
        queryset = UserActivity.objects.all()
        
        if action_types:
            queryset = queryset.filter(action_type__in=action_types)
        
        return queryset.order_by('-timestamp')[:limit]
    
    @staticmethod
    def get_activity_statistics(days=30):
        """Get activity statistics for the specified period."""
        from django.db.models import Count
        from .models import UserActivity
        
        since_date = timezone.now() - timezone.timedelta(days=days)
        
        stats = {
            'total_activities': UserActivity.objects.filter(timestamp__gte=since_date).count(),
            'unique_users': UserActivity.objects.filter(timestamp__gte=since_date).values('user').distinct().count(),
            'activities_by_type': dict(
                UserActivity.objects.filter(timestamp__gte=since_date)
                .values('action_type')
                .annotate(count=Count('id'))
                .values_list('action_type', 'count')
            ),
            'activities_by_day': dict(
                UserActivity.objects.filter(timestamp__gte=since_date)
                .extra({'day': 'date(timestamp)'})
                .values('day')
                .annotate(count=Count('id'))
                .values_list('day', 'count')
            )
        }
        
        return stats
    
    @staticmethod
    def get_failed_login_statistics(days=30):
        """Get failed login statistics."""
        from django.db.models import Count
        from .models import FailedLoginAttempt
        
        since_date = timezone.now() - timezone.timedelta(days=days)
        
        stats = {
            'total_failed_logins': FailedLoginAttempt.objects.filter(timestamp__gte=since_date).count(),
            'unique_ips': FailedLoginAttempt.objects.filter(timestamp__gte=since_date).values('ip_address').distinct().count(),
            'failed_by_ip': dict(
                FailedLoginAttempt.objects.filter(timestamp__gte=since_date)
                .values('ip_address')
                .annotate(count=Count('id'))
                .order_by('-count')[:10]
                .values_list('ip_address', 'count')
            ),
            'failed_by_reason': dict(
                FailedLoginAttempt.objects.filter(timestamp__gte=since_date)
                .values('reason')
                .annotate(count=Count('id'))
                .values_list('reason', 'count')
            )
        }
        
        return stats
    
    @staticmethod
    def cleanup_old_activities(days_to_keep=90):
        """Clean up old activity logs."""
        from .models import UserActivity, FailedLoginAttempt, SystemEvent
        
        cutoff_date = timezone.now() - timezone.timedelta(days=days_to_keep)
        
        deleted_activities = UserActivity.objects.filter(timestamp__lt=cutoff_date).delete()[0]
        deleted_failed_logins = FailedLoginAttempt.objects.filter(timestamp__lt=cutoff_date).delete()[0]
        deleted_system_events = SystemEvent.objects.filter(timestamp__lt=cutoff_date).delete()[0]
        
        logger.info(f"Cleaned up {deleted_activities} activities, {deleted_failed_logins} failed logins, {deleted_system_events} system events")
        
        return {
            'activities_deleted': deleted_activities,
            'failed_logins_deleted': deleted_failed_logins,
            'system_events_deleted': deleted_system_events
        }


class AuditLogger:
    """Enhanced audit logging for compliance and security."""
    
    @staticmethod
    def log_data_access(user, resource_type, resource_id, action, request=None):
        """Log data access for audit purposes."""
        ip_address = ActivityTracker.get_client_ip(request) if request else None
        user_agent = request.META.get('HTTP_USER_AGENT', '') if request else ''
        
        try:
            from .models import DataAccessLog
            
            DataAccessLog.objects.create(
                user=user,
                resource_type=resource_type,
                resource_id=resource_id,
                action=action,
                ip_address=ip_address,
                user_agent=user_agent,
                timestamp=timezone.now()
            )
            
        except Exception as e:
            logger.error(f"Failed to log data access: {str(e)}")
    
    @staticmethod
    def log_admin_action(admin_user, action, target_user=None, details=None, request=None):
        """Log administrative actions."""
        ip_address = ActivityTracker.get_client_ip(request) if request else None
        user_agent = request.META.get('HTTP_USER_AGENT', '') if request else ''
        
        try:
            from .models import AdminActionLog
            
            AdminActionLog.objects.create(
                admin_user=admin_user,
                target_user=target_user,
                action=action,
                details=details or {},
                ip_address=ip_address,
                user_agent=user_agent,
                timestamp=timezone.now()
            )
            
        except Exception as e:
            logger.error(f"Failed to log admin action: {str(e)}")
    
    @staticmethod
    def log_security_event(event_type, severity, description, user=None, ip_address=None, details=None):
        """Log security events."""
        try:
            from .models import SecurityEvent
            
            SecurityEvent.objects.create(
                event_type=event_type,
                severity=severity,
                description=description,
                user=user,
                ip_address=ip_address,
                details=details or {},
                timestamp=timezone.now()
            )
            
            # Log high-severity events to system logger
            if severity in ['high', 'critical']:
                logger.warning(f"Security event [{severity}]: {event_type} - {description}")
            
        except Exception as e:
            logger.error(f"Failed to log security event: {str(e)}")
    
    @staticmethod
    def detect_suspicious_activity(user, request=None):
        """Detect and log suspicious activity patterns."""
        ip_address = ActivityTracker.get_client_ip(request) if request else None
        
        # Check for multiple failed logins
        from .models import FailedLoginAttempt
        
        recent_failures = FailedLoginAttempt.objects.filter(
            email=user.email,
            timestamp__gte=timezone.now() - timezone.timedelta(hours=1)
        ).count()
        
        if recent_failures >= 5:
            AuditLogger.log_security_event(
                event_type='multiple_failed_logins',
                severity='medium',
                description=f"Multiple failed login attempts for {user.email}",
                user=user,
                ip_address=ip_address,
                details={'failure_count': recent_failures}
            )
        
        # Check for unusual login location (simplified)
        # In production, you'd implement geolocation checking
        if user.last_login_ip and ip_address and user.last_login_ip != ip_address:
            AuditLogger.log_security_event(
                event_type='unusual_login_location',
                severity='low',
                description=f"Login from new IP address for {user.email}",
                user=user,
                ip_address=ip_address,
                details={'previous_ip': user.last_login_ip, 'new_ip': ip_address}
            )
        
        # Check for rapid successive logins
        recent_logins = ActivityTracker.get_user_activities(
            user, 
            limit=10, 
            action_types=['login']
        )
        
        if len(recent_logins) >= 3:
            # Check if logins happened within short time frame
            time_diff = (timezone.now() - recent_logins[0].timestamp).total_seconds()
            if time_diff < 300:  # 5 minutes
                AuditLogger.log_security_event(
                    event_type='rapid_successive_logins',
                    severity='medium',
                    description=f"Rapid successive logins for {user.email}",
                    user=user,
                    ip_address=ip_address,
                    details={'login_count': len(recent_logins), 'time_frame': time_diff}
                )


# Decorators for automatic activity logging
def log_activity(action_type, description_template="", include_details=False):
    """Decorator to automatically log function calls as activities."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Try to extract user from arguments
            user = None
            request = None
            
            for arg in args:
                if hasattr(arg, 'user'):
                    request = arg
                    user = arg.user
                    break
                elif hasattr(arg, 'email'):
                    user = arg
                    break
            
            if not user:
                # Check in kwargs
                user = kwargs.get('user')
                request = kwargs.get('request')
            
            # Execute the function
            result = func(*args, **kwargs)
            
            # Log the activity
            if user:
                description = description_template.format(*args, **kwargs) if description_template else f"{func.__name__} executed"
                details = {}
                
                if include_details:
                    details['function'] = func.__name__
                    details['args_count'] = len(args)
                    details['kwargs_keys'] = list(kwargs.keys())
                
                ActivityTracker.log_activity(
                    user=user,
                    action_type=action_type,
                    description=description,
                    details=details,
                    ip_address=ActivityTracker.get_client_ip(request) if request else None,
                    user_agent=request.META.get('HTTP_USER_AGENT', '') if request else ''
                )
            
            return result
        return wrapper
    return decorator
