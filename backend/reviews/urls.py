from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('', views.ReviewListCreateView.as_view(), name='review-list'),
    path('<int:pk>/', views.ReviewDetailView.as_view(), name='review-detail'),
    path('business/<int:business_id>/', views.business_reviews, name='business-reviews'),
    path('user/', views.user_reviews, name='user-reviews'),
]
