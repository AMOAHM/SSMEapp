from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import dashboard_views

# Create router for business dashboard endpoints
router = DefaultRouter()
router.register(r'', dashboard_views.BusinessDashboardViewSet, basename='business-dashboard')
router.register(r'products/advertising', dashboard_views.ProductAdvertisingViewSet, basename='product-advertising')

urlpatterns = [
    # Business dashboard endpoints
    path('', include(router.urls)),
    
    # Additional dashboard-specific URLs
    path('dashboard/', dashboard_views.BusinessDashboardViewSet.as_view({'get': 'dashboard'}), name='business-dashboard-data'),
    path('inventory/', dashboard_views.BusinessDashboardViewSet.as_view({'get': 'inventory'}), name='business-inventory'),
    path('analytics/', dashboard_views.BusinessDashboardViewSet.as_view({'get': 'analytics'}), name='business-analytics'),
    path('products/<int:pk>/stock/', dashboard_views.BusinessDashboardViewSet.as_view({'patch': 'update_stock'}), name='product-update-stock'),
    path('businesses/<int:pk>/featured/', dashboard_views.BusinessDashboardViewSet.as_view({'post': 'toggle_featured'}), name='business-toggle-featured'),
    path('products/<int:pk>/promote/', dashboard_views.ProductAdvertisingViewSet.as_view({'post': 'promote'}), name='product-promote'),
]
