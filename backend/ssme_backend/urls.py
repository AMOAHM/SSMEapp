"""
URL configuration for ssme_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from businesses.views import GlobalProductListView, GlobalServiceListView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/auth/', include('accounts.urls')),
    path('api/auth/enhanced/', include('accounts.enhanced_urls')),  # Now enabled for password reset
    path('api/auth/admin/', include('accounts.admin_urls')),
    path('api/auth/admin/management/', include('accounts.admin_management_urls')),
    path('api/businesses/', include('businesses.urls')),
    path('api/businesses/dashboard/', include('businesses.dashboard_urls')),
    path('api/reviews/', include('reviews.urls')),
    path('api/categories/', include('categories.urls')),
    path('api/products/', GlobalProductListView.as_view(), name='global-products'),
    path('api/services/', GlobalServiceListView.as_view(), name='global-services'),
    path('api/', include('orders.urls')),
    path('api/analytics/', include('analytics.urls')),
    path('api/reports/', include('accounts.reports_urls')),
    path('api/settings/', include('settings.urls')),
    
    # API documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
