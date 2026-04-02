from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .admin_views import AdminViewSet

router = DefaultRouter()
router.register(r'users', AdminViewSet, basename='admin-management')

urlpatterns = [
    path('', include(router.urls)),
]
