from django.urls import path
from . import views

app_name = 'businesses'

urlpatterns = [
    path('', views.BusinessListCreateView.as_view(), name='business-list'),
    path('<int:pk>/', views.BusinessDetailView.as_view(), name='business-detail'),
    path('<int:pk>/status/', views.update_business_status, name='business-status'),
    path('<int:business_id>/images/', views.BusinessImageListCreateView.as_view(), name='business-images'),
    path('<int:business_id>/products/', views.ProductListCreateView.as_view(), name='business-products'),
    path('<int:business_id>/products/<int:product_id>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('<int:business_id>/services/', views.ServiceListCreateView.as_view(), name='business-services'),
    path('<int:business_id>/services/<int:service_id>/', views.ServiceDetailView.as_view(), name='service-detail'),
    path('favorites/', views.FavoriteListCreateView.as_view(), name='favorite-list'),
    path('favorites/<int:business_id>/', views.remove_favorite, name='remove-favorite'),
    path('featured/', views.featured_businesses, name='featured-businesses'),
]
