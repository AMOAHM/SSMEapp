from django.urls import path, include
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('business-login/', views.BusinessLoginView.as_view(), name='business-login'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('refresh/', views.refresh_token, name='refresh_token'),
    path('logout/', views.logout, name='logout'),
]
