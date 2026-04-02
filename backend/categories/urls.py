from django.urls import path
from . import views

app_name = 'categories'

urlpatterns = [
    path('', views.CategoryListCreateView.as_view(), name='category-list'),
    path('<int:pk>/', views.CategoryDetailView.as_view(), name='category-detail'),
    path('popular/', views.popular_categories, name='popular-categories'),
]
