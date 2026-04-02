from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.signing import TimestampSigner, BadSignature
from django.urls import reverse
import logging
import hashlib

User = get_user_model()
logger = logging.getLogger(__name__)


class EmailVerificationService:
    """Service for handling email verification."""
    
    @staticmethod
    def generate_verification_token(user):
        """Generate a secure email verification token."""
        # Create a timestamped token that expires in 24 hours
        signer = TimestampSigner()
        token_data = f"{user.id}:{user.email}"
        token = signer.sign(token_data)
        
        # Store the token hash for verification
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        user.email_verification_token = token_hash
        user.email_verification_expires = timezone.now() + timezone.timedelta(hours=24)
        user.save(update_fields=['email_verification_token', 'email_verification_expires'])
        
        return token
    
    @staticmethod
    def verify_email_token(token):
        """Verify email verification token."""
        try:
            signer = TimestampSigner()
            token_data = signer.unsign(token, max_age=24*60*60)  # 24 hours
            
            user_id, email = token_data.split(':')
            user = User.objects.get(id=user_id, email=email)
            
            # Check if token hash matches
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            if user.email_verification_token != token_hash:
                return None, "Invalid verification token"
            
            # Check if token has expired
            if user.email_verification_expires and user.email_verification_expires < timezone.now():
                return None, "Verification token has expired"
            
            return user, "Token verified successfully"
            
        except (BadSignature, ValueError, User.DoesNotExist):
            return None, "Invalid verification token"
    
    @staticmethod
    def send_verification_email(user, request=None):
        """Send email verification email."""
        try:
            token = EmailVerificationService.generate_verification_token(user)
            
            # Build verification URL
            if hasattr(settings, 'FRONTEND_URL'):
                verification_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
            else:
                # Fallback to Django URL
                verification_url = request.build_absolute_uri(
                    reverse('verify-email') + f'?token={token}'
                ) if request else f"http://localhost:8000/api/auth/verify-email?token={token}"
            
            # Render email template
            subject = "Verify Your Email Address"
            context = {
                'user': user,
                'verification_url': verification_url,
                'site_name': getattr(settings, 'SITE_NAME', 'SSME Platform'),
                'support_email': getattr(settings, 'SUPPORT_EMAIL', 'support@ssme.com')
            }
            
            html_message = render_to_string('emails/email_verification.html', context)
            text_message = render_to_string('emails/email_verification.txt', context)
            
            # Send email
            send_mail(
                subject=subject,
                message=text_message,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@ssme.com'),
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False
            )
            
            logger.info(f"Verification email sent to {user.email}")
            return True, "Verification email sent successfully"
            
        except Exception as e:
            logger.error(f"Failed to send verification email: {str(e)}")
            return False, f"Failed to send verification email: {str(e)}"
    
    @staticmethod
    def verify_user_email(token):
        """Verify user email and update account status."""
        user, message = EmailVerificationService.verify_email_token(token)
        
        if user:
            user.is_verified = True
            user.email_verification_token = None
            user.email_verification_expires = None
            
            # Update account status if it was pending verification
            if user.account_status == 'pending_verification':
                user.account_status = 'active'
            
            user.save(update_fields=['is_verified', 'email_verification_token', 'email_verification_expires', 'account_status'])
            
            # Log the activity
            from .activity_tracker import ActivityTracker
            ActivityTracker.log_email_verified(user)
            
            logger.info(f"Email verified for user: {user.email}")
            return True, "Email verified successfully"
        
        return False, message


class PasswordResetService:
    """Service for handling password reset functionality."""
    
    @staticmethod
    def generate_reset_token(user):
        """Generate a secure password reset token."""
        # Create a timestamped token that expires in 1 hour
        signer = TimestampSigner()
        token_data = f"{user.id}:{user.email}"
        token = signer.sign(token_data)
        
        # Store the token hash for verification
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        user.password_reset_token = token_hash
        user.password_reset_expires = timezone.now() + timezone.timedelta(hours=1)
        user.save(update_fields=['password_reset_token', 'password_reset_expires'])
        
        return token
    
    @staticmethod
    def verify_reset_token(token):
        """Verify password reset token."""
        try:
            signer = TimestampSigner()
            token_data = signer.unsign(token, max_age=60*60)  # 1 hour
            
            user_id, email = token_data.split(':')
            user = User.objects.get(id=user_id, email=email)
            
            # Check if token hash matches
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            if user.password_reset_token != token_hash:
                return None, "Invalid reset token"
            
            # Check if token has expired
            if user.password_reset_expires and user.password_reset_expires < timezone.now():
                return None, "Reset token has expired"
            
            return user, "Token verified successfully"
            
        except (BadSignature, ValueError, User.DoesNotExist):
            return None, "Invalid reset token"
    
    @staticmethod
    def send_reset_email(user, request=None):
        """Send password reset email."""
        try:
            token = PasswordResetService.generate_reset_token(user)
            
            # Build reset URL
            if hasattr(settings, 'FRONTEND_URL'):
                reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
            else:
                # Fallback to Django URL
                reset_url = request.build_absolute_uri(
                    reverse('password-reset-confirm') + f'?token={token}'
                ) if request else f"http://localhost:8000/reset-password?token={token}"
            
            # Render email template
            subject = "Reset Your Password"
            context = {
                'user': user,
                'reset_url': reset_url,
                'site_name': getattr(settings, 'SITE_NAME', 'SSME Platform'),
                'support_email': getattr(settings, 'SUPPORT_EMAIL', 'support@ssme.com'),
                'expires_hours': 1
            }
            
            html_message = render_to_string('emails/password_reset.html', context)
            text_message = render_to_string('emails/password_reset.txt', context)
            
            # Send email
            send_mail(
                subject=subject,
                message=text_message,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@ssme.com'),
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False
            )
            
            # Log the activity
            from .activity_tracker import ActivityTracker
            ActivityTracker.log_activity(
                user=user,
                action_type='password_reset_requested',
                description="Password reset requested",
                details={'ip_address': getattr(request, 'ip_address', None)}
            )
            
            logger.info(f"Password reset email sent to {user.email}")
            return True, "Password reset email sent successfully"
            
        except Exception as e:
            logger.error(f"Failed to send password reset email: {str(e)}")
            return False, f"Failed to send password reset email: {str(e)}"
    
    @staticmethod
    def reset_password(token, new_password):
        """Reset user password using token."""
        user, message = PasswordResetService.verify_reset_token(token)
        
        if user:
            user.set_password(new_password)
            user.password_reset_token = None
            user.password_reset_expires = None
            user.password_changed_at = timezone.now()
            user.save(update_fields=['password', 'password_reset_token', 'password_reset_expires', 'password_changed_at'])
            
            # Log the activity
            from .activity_tracker import ActivityTracker
            ActivityTracker.log_password_change(user, success=True)
            
            logger.info(f"Password reset completed for user: {user.email}")
            return True, "Password reset successfully"
        
        return False, message


class PhoneVerificationService:
    """Service for handling phone number verification."""
    
    @staticmethod
    def generate_verification_code():
        """Generate a 6-digit verification code."""
        return get_random_string(6, allowed_chars='0123456789')
    
    @staticmethod
    def send_verification_code(user, code):
        """Send SMS verification code (placeholder implementation)."""
        try:
            # This is a placeholder - in production, you'd integrate with an SMS service
            # like Twilio, AWS SNS, or another SMS provider
            
            message = f"Your SSME verification code is: {code}. This code expires in 10 minutes."
            
            # Log the code for development (remove in production)
            logger.info(f"SMS verification code for {user.phone}: {code}")
            
            # In production, send actual SMS:
            # from twilio.rest import Client
            # client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            # message = client.messages.create(
            #     body=message,
            #     from_=settings.TWILIO_PHONE_NUMBER,
            #     to=user.phone
            # )
            
            # Store the code hash and expiry
            import hashlib
            code_hash = hashlib.sha256(code.encode()).hexdigest()
            user.phone_verification_code = code_hash
            user.phone_verification_expires = timezone.now() + timezone.timedelta(minutes=10)
            user.save(update_fields=['phone_verification_code', 'phone_verification_expires'])
            
            return True, "Verification code sent successfully"
            
        except Exception as e:
            logger.error(f"Failed to send SMS verification: {str(e)}")
            return False, f"Failed to send verification code: {str(e)}"
    
    @staticmethod
    def verify_phone_code(user, code):
        """Verify phone verification code."""
        try:
            # Check if code has expired
            if user.phone_verification_expires and user.phone_verification_expires < timezone.now():
                return False, "Verification code has expired"
            
            # Check if code matches
            import hashlib
            code_hash = hashlib.sha256(code.encode()).hexdigest()
            
            if user.phone_verification_code == code_hash:
                user.is_phone_verified = True
                user.phone_verification_code = None
                user.phone_verification_expires = None
                user.save(update_fields=['is_phone_verified', 'phone_verification_code', 'phone_verification_expires'])
                
                # Log the activity
                from .activity_tracker import ActivityTracker
                ActivityTracker.log_phone_verified(user)
                
                return True, "Phone number verified successfully"
            else:
                return False, "Invalid verification code"
                
        except Exception as e:
            logger.error(f"Failed to verify phone code: {str(e)}")
            return False, f"Failed to verify code: {str(e)}"


class TwoFactorAuthService:
    """Service for handling two-factor authentication."""
    
    @staticmethod
    def generate_secret():
        """Generate a new 2FA secret."""
        return get_random_string(32, allowed_chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ234567')
    
    @staticmethod
    def generate_backup_codes():
        """Generate backup codes for 2FA."""
        return [get_random_string(8, allowed_chars='0123456789ABCDEF') for _ in range(10)]
    
    @staticmethod
    def setup_2fa(user):
        """Setup 2FA for user."""
        try:
            secret = TwoFactorAuthService.generate_secret()
            backup_codes = TwoFactorAuthService.generate_backup_codes()
            
            user.two_factor_secret = secret
            user.two_factor_backup_codes = backup_codes
            user.save(update_fields=['two_factor_secret', 'two_factor_backup_codes'])
            
            # In production, you'd generate QR code here
            # import pyotp
            # import qrcode
            # totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            #     name=user.email,
            #     issuer_name="SSME Platform"
            # )
            # qr = qrcode.QRCode(version=1, box_size=10, border=5)
            # qr.add_data(totp_uri)
            # qr.make(fit=True)
            
            return {
                'secret': secret,
                'backup_codes': backup_codes,
                # 'qr_code': qr_code_data_url  # Implement QR code generation
            }
            
        except Exception as e:
            logger.error(f"Failed to setup 2FA: {str(e)}")
            return None
    
    @staticmethod
    def verify_2fa_token(user, token):
        """Verify 2FA token."""
        try:
            import pyotp
            totp = pyotp.TOTP(user.two_factor_secret)
            return totp.verify(token)
        except:
            return False
    
    @staticmethod
    def verify_backup_code(user, code):
        """Verify backup code."""
        if not user.two_factor_backup_codes:
            return False
        
        if code in user.two_factor_backup_codes:
            # Remove used backup code
            user.two_factor_backup_codes.remove(code)
            user.save(update_fields=['two_factor_backup_codes'])
            return True
        
        return False
    
    @staticmethod
    def enable_2fa(user, verification_token):
        """Enable 2FA after verification."""
        if TwoFactorAuthService.verify_2fa_token(user, verification_token):
            user.two_factor_enabled = True
            user.save(update_fields=['two_factor_enabled'])
            
            # Log the activity
            from .activity_tracker import ActivityTracker
            ActivityTracker.log_two_factor_enabled(user)
            
            return True, "2FA enabled successfully"
        
        return False, "Invalid verification token"
    
    @staticmethod
    def disable_2fa(user, password):
        """Disable 2FA after password verification."""
        if user.check_password(password):
            user.two_factor_enabled = False
            user.two_factor_secret = None
            user.two_factor_backup_codes = None
            user.save(update_fields=['two_factor_enabled', 'two_factor_secret', 'two_factor_backup_codes'])
            
            # Log the activity
            from .activity_tracker import ActivityTracker
            ActivityTracker.log_two_factor_disabled(user)
            
            return True, "2FA disabled successfully"
        
        return False, "Invalid password"


class NotificationService:
    """Service for sending various types of notifications."""
    
    @staticmethod
    def send_welcome_email(user):
        """Send welcome email to new users."""
        try:
            subject = f"Welcome to {getattr(settings, 'SITE_NAME', 'SSME Platform')}!"
            context = {
                'user': user,
                'site_name': getattr(settings, 'SITE_NAME', 'SSME Platform'),
                'login_url': f"{getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')}/login",
                'support_email': getattr(settings, 'SUPPORT_EMAIL', 'support@ssme.com')
            }
            
            html_message = render_to_string('emails/welcome.html', context)
            text_message = render_to_string('emails/welcome.txt', context)
            
            send_mail(
                subject=subject,
                message=text_message,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@ssme.com'),
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False
            )
            
            logger.info(f"Welcome email sent to {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send welcome email: {str(e)}")
            return False
    
    @staticmethod
    def send_security_alert(user, alert_type, details=None):
        """Send security alert email."""
        try:
            subject = f"Security Alert: {alert_type}"
            context = {
                'user': user,
                'alert_type': alert_type,
                'details': details or {},
                'site_name': getattr(settings, 'SITE_NAME', 'SSME Platform'),
                'support_email': getattr(settings, 'SUPPORT_EMAIL', 'support@ssme.com')
            }
            
            html_message = render_to_string('emails/security_alert.html', context)
            text_message = render_to_string('emails/security_alert.txt', context)
            
            send_mail(
                subject=subject,
                message=text_message,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@ssme.com'),
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False
            )
            
            logger.info(f"Security alert sent to {user.email}: {alert_type}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send security alert: {str(e)}")
            return False
    
    @staticmethod
    def send_account_suspended_notification(user, reason=""):
        """Send account suspension notification."""
        try:
            subject = "Account Suspended"
            context = {
                'user': user,
                'reason': reason,
                'site_name': getattr(settings, 'SITE_NAME', 'SSME Platform'),
                'support_email': getattr(settings, 'SUPPORT_EMAIL', 'support@ssme.com')
            }
            
            html_message = render_to_string('emails/account_suspended.html', context)
            text_message = render_to_string('emails/account_suspended.txt', context)
            
            send_mail(
                subject=subject,
                message=text_message,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@ssme.com'),
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False
            )
            
            logger.info(f"Account suspension notification sent to {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send suspension notification: {str(e)}")
            return False
