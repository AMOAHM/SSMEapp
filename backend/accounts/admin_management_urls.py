from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import admin_management_views

# Create router for admin management endpoints
router = DefaultRouter()
router.register(r'businesses', admin_management_views.BusinessManagementViewSet, basename='admin-businesses')
router.register(r'products', admin_management_views.ProductManagementViewSet, basename='admin-products')
router.register(r'users', admin_management_views.AdminUserManagementViewSet, basename='admin-users')

# Additional admin-specific URLs
urlpatterns = [
    # Admin management endpoints
    path('', include(router.urls)),
    
    # Business approval endpoints
    path('businesses/pending/', admin_management_views.BusinessManagementViewSet.as_view({'get': 'pending'}), name='admin-pending-businesses'),
    path('businesses/by-status/', admin_management_views.BusinessManagementViewSet.as_view({'get': 'by_status'}), name='admin-businesses-by-status'),
    path('businesses/<int:pk>/approve/', admin_management_views.BusinessManagementViewSet.as_view({'post': 'approve'}), name='admin-approve-business'),
    path('businesses/<int:pk>/reject/', admin_management_views.BusinessManagementViewSet.as_view({'post': 'reject'}), name='admin-reject-business'),
    path('businesses/<int:pk>/suspend/', admin_management_views.BusinessManagementViewSet.as_view({'post': 'suspend'}), name='admin-suspend-business'),
    
    # Statistics endpoints
    path('statistics/businesses/', admin_management_views.BusinessManagementViewSet.as_view({'get': 'statistics'}), name='admin-business-stats'),
    path('statistics/users/', admin_management_views.AdminUserManagementViewSet.as_view({'get': 'statistics'}), name='admin-user-stats'),
]
