from rest_framework import status, generics, permissions, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.auth import logout
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.crypto import get_random_string
from django.db import transaction
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import User, UserProfile, UserActivity
from .enhanced_serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer,
    UserUpdateSerializer, PasswordChangeSerializer, UserActivitySerializer,
    AdminUserSerializer, AdminUserCreateSerializer, AdminUserUpdateSerializer
)

User = get_user_model()


class EnhancedRegisterView(generics.CreateAPIView):
    """Enhanced user registration with security features."""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        summary="Register a new user",
        description="Create a new user account with enhanced validation and security features.",
        responses={201: UserProfileSerializer}
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        with transaction.atomic():
            user = serializer.save()
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            # Update login information
            user.last_login_ip = self.get_client_ip(request)
            user.increment_login_count()
            user.save()
            
            # Log activity
            UserActivity.objects.create(
                user=user,
                action_type='login',
                description="User logged in after registration",
                ip_address=user.last_login_ip,
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            return Response({
                'user': UserProfileSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)
    
    def get_client_ip(self, request):
        """Get client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class EnhancedLoginView(generics.GenericAPIView):
    """Enhanced login with security features and activity tracking."""
    serializer_class = UserLoginSerializer
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        summary="User login",
        description="Authenticate user with enhanced security and activity tracking.",
        responses={200: UserProfileSerializer}
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        remember_me = serializer.validated_data.get('remember_me', False)
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        # Update login information
        user.last_login_ip = self.get_client_ip(request)
        user.increment_login_count()
        user.save()
        
        # Log activity
        UserActivity.objects.create(
            user=user,
            action_type='login',
            description="User logged in successfully",
            ip_address=user.last_login_ip,
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        # Set token expiration based on remember_me
        if remember_me:
            # Long-lived session (30 days)
            refresh.set_exp(lifetime=timezone.timedelta(days=30))
        
        return Response({
            'user': UserProfileSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })
    
    def get_client_ip(self, request):
        """Get client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class EnhancedLogoutView(generics.GenericAPIView):
    """Enhanced logout with activity tracking."""
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="User logout",
        description="Logout user and track activity.",
    )
    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data.get("refresh")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            # Log activity
            UserActivity.objects.create(
                user=request.user,
                action_type='logout',
                description="User logged out",
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            return Response({"message": "Successfully logged out"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def get_client_ip(self, request):
        """Get client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class EnhancedProfileView(generics.RetrieveUpdateAPIView):
    """Enhanced user profile management."""
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        """Update user profile with enhanced tracking."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = UserUpdateSerializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        updated_user = serializer.save()
        
        return Response(UserProfileSerializer(updated_user).data)


class PasswordChangeView(generics.GenericAPIView):
    """Enhanced password change with security features."""
    serializer_class = PasswordChangeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Change password",
        description="Change user password with enhanced validation.",
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({"message": "Password changed successfully"}, status=status.HTTP_200_OK)


class UserActivityViewSet(viewsets.ReadOnlyModelViewSet):
    """View user activity logs."""
    serializer_class = UserActivitySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserActivity.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent user activities."""
        recent_activities = self.get_queryset()[:10]
        serializer = self.get_serializer(recent_activities, many=True)
        return Response(serializer.data)


class EmailVerificationView(generics.GenericAPIView):
    """Email verification endpoint."""
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        summary="Verify email",
        description="Verify user email address.",
        parameters=[
            OpenApiParameter(name='token', type=OpenApiTypes.STR, location=OpenApiParameter.QUERY)
        ]
    )
    def get(self, request, *args, **kwargs):
        token = request.GET.get('token')
        
        if not token:
            return Response({"error": "Verification token required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Find user by verification token (you'll need to add this field to User model)
            user = User.objects.get(email_verification_token=token)
            
            if user.is_verified:
                return Response({"message": "Email already verified"}, status=status.HTTP_200_OK)
            
            user.is_verified = True
            user.email_verification_token = None
            user.account_status = 'active'
            user.save()
            
            # Log activity
            UserActivity.objects.create(
                user=user,
                action_type='email_verified',
                description="Email address verified successfully"
            )
            
            return Response({"message": "Email verified successfully"}, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response({"error": "Invalid verification token"}, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(generics.GenericAPIView):
    """Request password reset."""
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        summary="Request password reset",
        description="Send password reset email to user.",
    )
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        
        if not email:
            return Response({"error": "Email required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email__iexact=email)
            
            # Generate 6-digit reset code
            reset_token = get_random_string(6, allowed_chars='0123456789')
            user.password_reset_token = reset_token
            user.password_reset_expires = timezone.now() + timezone.timedelta(hours=1)
            user.save()
            
            subject = "Password Reset Verification Code"
            message = render_to_string('emails/password_reset.html', {
                'user': user,
                'reset_token': reset_token,
            })
            
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    html_message=message,
                )
            except Exception as e:
                # Log error and return user-friendly response
                print(f"Error sending email: {str(e)}")
                if settings.DEBUG:
                    return Response({
                        "error": "Failed to send email. Check your SMTP settings in .env.",
                        "details": str(e)
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                return Response({"message": "Password reset initiated, but there was an error sending the email."}, status=status.HTTP_200_OK)

            return Response({"message": "Password reset verification code sent"}, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            # Don't reveal if email exists or not
            return Response({"message": "If email exists, reset instructions have been sent"}, status=status.HTTP_200_OK)


class PasswordResetConfirmView(generics.GenericAPIView):
    """Confirm password reset."""
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        summary="Reset password",
        description="Reset user password with valid token.",
    )
    def post(self, request, *args, **kwargs):
        token = request.data.get('token', '').strip()
        new_password = request.data.get('new_password')
        
        if not token or not new_password:
            return Response({"error": "Token and new password required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(
                password_reset_token=token,
                password_reset_expires__gt=timezone.now()
            )
            
            user.set_password(new_password)
            user.password_reset_token = None
            user.password_reset_expires = None
            user.save()
            
            # Log activity
            UserActivity.objects.create(
                user=user,
                action_type='password_change',
                description="Password reset via email"
            )
            
            return Response({"message": "Password reset successfully"}, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response({"error": "Invalid or expired reset token"}, status=status.HTTP_400_BAD_REQUEST)


class TwoFactorSetupView(generics.GenericAPIView):
    """Setup two-factor authentication."""
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Setup 2FA",
        description="Setup two-factor authentication for user account.",
    )
    def post(self, request, *args, **kwargs):
        user = request.user
        
        # Generate 2FA secret (you'll need to implement this with pyotp)
        secret = get_random_string(32)
        user.two_factor_secret = secret
        user.save()
        
        # Generate QR code (you'll need to implement this with qrcode)
        # qr_url = f"otpauth://totp/SSME:{user.email}?secret={secret}&issuer=SSME"
        
        return Response({
            "secret": secret,
            # "qr_code": qr_code_data_url  # Implement QR code generation
        })
    
    @extend_schema(
        summary="Verify 2FA",
        description="Verify and enable two-factor authentication.",
    )
    def post(self, request, *args, **kwargs):
        code = request.data.get('code')
        
        if not code:
            return Response({"error": "Verification code required"}, status=status.HTTP_400_BAD_REQUEST)
        
        user = request.user
        
        # Verify code (you'll need to implement this with pyotp)
        # totp = pyotp.TOTP(user.two_factor_secret)
        # if not totp.verify(code):
        #     return Response({"error": "Invalid verification code"}, status=status.HTTP_400_BAD_REQUEST)
        
        user.two_factor_enabled = True
        user.save()
        
        # Log activity
        UserActivity.objects.create(
            user=user,
            action_type='two_factor_enabled',
            description="Two-factor authentication enabled"
        )
        
        return Response({"message": "2FA enabled successfully"}, status=status.HTTP_200_OK)


# Enhanced admin views
class EnhancedAdminViewSet(viewsets.ModelViewSet):
    """Enhanced admin user management."""
    serializer_class = AdminUserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.has_super_admin_access():
            return User.objects.all()
        elif user.has_admin_access():
            return User.objects.filter(role__in=['customer', 'business'])
        else:
            return User.objects.none()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return AdminUserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return AdminUserUpdateSerializer
        return AdminUserSerializer
    
    @action(detail=True, methods=['post'])
    def suspend(self, request, pk=None):
        """Suspend user account."""
        user = self.get_object()
        user.account_status = 'suspended'
        user.save()
        
        UserActivity.objects.create(
            user=request.user,
            action_type='account_suspended',
            description=f"Account suspended: {user.email}"
        )
        
        return Response({"message": "Account suspended successfully"})
    
    @action(detail=True, methods=['post'])
    def reactivate(self, request, pk=None):
        """Reactivate user account."""
        user = self.get_object()
        user.account_status = 'active'
        user.save()
        
        UserActivity.objects.create(
            user=request.user,
            action_type='account_reactivated',
            description=f"Account reactivated: {user.email}"
        )
        
        return Response({"message": "Account reactivated successfully"})
    
    @action(detail=True, methods=['get'])
    def activities(self, request, pk=None):
        """Get user activities."""
        user = self.get_object()
        activities = user.activities.all()[:50]  # Last 50 activities
        serializer = UserActivitySerializer(activities, many=True)
        return Response(serializer.data)
