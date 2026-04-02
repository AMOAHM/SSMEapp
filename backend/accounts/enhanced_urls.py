from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from . import enhanced_views

# Create router for admin endpoints
router = DefaultRouter()
router.register(r'users', enhanced_views.EnhancedAdminViewSet, basename='admin-users')

urlpatterns = [
    # Authentication endpoints
    path('register/', enhanced_views.EnhancedRegisterView.as_view(), name='enhanced-register'),
    path('login/', enhanced_views.EnhancedLoginView.as_view(), name='enhanced-login'),
    path('logout/', enhanced_views.EnhancedLogoutView.as_view(), name='enhanced-logout'),
    path('refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    
    # Profile management
    path('profile/', enhanced_views.EnhancedProfileView.as_view(), name='enhanced-profile'),
    path('password/change/', enhanced_views.PasswordChangeView.as_view(), name='password-change'),
    
    # Email verification
    path('verify-email/', enhanced_views.EmailVerificationView.as_view(), name='verify-email'),
    
    # Password reset
    path('password/reset/', enhanced_views.PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('password/reset/confirm/', enhanced_views.PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    
    # Two-factor authentication
    path('2fa/setup/', enhanced_views.TwoFactorSetupView.as_view(), name='2fa-setup'),
    
    # User activities
    path('activities/', enhanced_views.UserActivityViewSet.as_view({'get': 'list'}), name='user-activities'),
    path('activities/recent/', enhanced_views.UserActivityViewSet.as_view({'get': 'recent'}), name='recent-activities'),
    
    # Admin endpoints
    path('', include(router.urls)),
]
