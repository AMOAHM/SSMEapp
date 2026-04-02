from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, BusinessOrderViewSet

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'businesses/(?P<business_id>\d+)/orders', BusinessOrderViewSet, basename='business-order')

urlpatterns = [
    path('', include(router.urls)),
]
