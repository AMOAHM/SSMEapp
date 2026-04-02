from django.urls import path
from . import reports_views

app_name = 'reports'

urlpatterns = [
    # Export functionality
    path('export/', reports_views.export_report, name='export_report'),
    
    # Download functionality
    path('download/<str:filename>/', reports_views.download_report, name='download_report'),
    
    # Main reports endpoint
    path('', reports_views.ReportsAPIView.as_view(), name='reports'),
    
    # Specific report types (these all use the same main endpoint with query params)
    # path('overview/', reports_views.ReportsAPIView.as_view(), name='overview_report'),
    # path('sales/', reports_views.ReportsAPIView.as_view(), name='sales_report'),
    # path('users/', reports_views.ReportsAPIView.as_view(), name='users_report'),
    # path('businesses/', reports_views.ReportsAPIView.as_view(), name='businesses_report'),
    # path('orders/', reports_views.ReportsAPIView.as_view(), name='orders_report'),
    # path('activity/', reports_views.ReportsAPIView.as_view(), name='activity_report'),
]
