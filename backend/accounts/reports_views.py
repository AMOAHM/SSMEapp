from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Count, Sum, Avg, Q, F, ExpressionWrapper, FloatField
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models.functions import TruncDay, TruncMonth, TruncYear
from decimal import Decimal

from accounts.models import User, UserActivity
from businesses.models import Business, Product, BusinessImage
from categories.models import Category
from reviews.models import Review
from orders.models import Order, OrderItem


class ReportsAPIView(APIView):
    """Main API endpoint for admin reports and analytics."""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        """Only admins can access reports."""
        user = self.request.user
        if user.is_authenticated and user.is_admin_user():
            return [permissions.IsAuthenticated]
        return [permissions.IsAuthenticated]
    
    def check_permissions(self, request):
        """Check if user has admin permissions."""
        user = request.user
        if not user.is_authenticated or not user.is_admin_user():
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Admin access required")
    
    def get_date_range_filter(self, date_range):
        """Get date range filter based on selected period."""
        now = timezone.now()
        
        if date_range == '7d':
            start_date = now - timedelta(days=7)
        elif date_range == '30d':
            start_date = now - timedelta(days=30)
        elif date_range == '90d':
            start_date = now - timedelta(days=90)
        elif date_range == '1y':
            start_date = now - timedelta(days=365)
        else:
            start_date = now - timedelta(days=30)
        
        return start_date
    
    def get_overview_stats(self, date_range='30d'):
        """Get overview statistics."""
        start_date = self.get_date_range_filter(date_range)
        
        # Count new users/businesses within date range
        total_users = User.objects.filter(
            created_at__gte=start_date,
            role='customer'
        ).count()
        
        total_businesses = Business.objects.filter(
            created_at__gte=start_date
        ).count()
        
        # Order statistics — Order model uses 'total' field, not 'total_amount'
        try:
            orders = Order.objects.filter(
                created_at__gte=start_date
            )
            total_orders = orders.count()
            total_revenue = orders.aggregate(
                total=Sum('total')
            )['total'] or Decimal('0')
            
            average_order_value = total_revenue / total_orders if total_orders > 0 else Decimal('0')
        except Exception:
            total_orders = 0
            total_revenue = Decimal('0')
            average_order_value = Decimal('0')
        
        # User activity (users with any logged activity)
        active_users = UserActivity.objects.filter(
            timestamp__gte=start_date
        ).values('user').distinct().count()
        
        # Conversion rate: approved vs total businesses in range
        approved_businesses = Business.objects.filter(
            created_at__gte=start_date,
            status='approved'
        ).count()
        conversion_rate = (approved_businesses / total_businesses * 100) if total_businesses > 0 else 0
        
        return {
            'totalRevenue': float(total_revenue),
            'totalOrders': total_orders,
            'totalUsers': total_users,
            'totalBusinesses': total_businesses,
            'averageOrderValue': float(average_order_value),
            'conversionRate': round(conversion_rate, 2),
            'activeUsers': active_users
        }
    
    def get_sales_by_month(self, date_range='30d'):
        """Get monthly sales data."""
        start_date = self.get_date_range_filter(date_range)
        
        try:
            # Group orders by month — Order model uses 'total' field
            monthly_data = Order.objects.filter(
                created_at__gte=start_date
            ).annotate(
                month=TruncMonth('created_at')
            ).values('month').annotate(
                revenue=Sum('total'),
                orders=Count('id')
            ).order_by('month')
            
            # Format data for charts
            month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            
            result = []
            for data in monthly_data:
                month_num = data['month'].month
                result.append({
                    'month': month_names[month_num - 1],
                    'revenue': float(data['revenue'] or 0),
                    'orders': data['orders']
                })
            
            # If no real data, return empty list so frontend shows empty chart
            return result
        except Exception:
            return []
    
    def get_top_categories(self, date_range='30d'):
        """Get top performing categories."""
        start_date = self.get_date_range_filter(date_range)
        
        try:
            # Get categories with business counts
            categories = Category.objects.annotate(
                business_count=Count('business', filter=Q(business__created_at__gte=start_date))
            ).filter(business_count__gt=0).order_by('-business_count')[:10]
            
            result = []
            colors = ['#3B82F6', '#10B981', '#F59E0B', '#8B5CF6', '#EF4444', 
                     '#06B6D4', '#84CC16', '#F97316', '#EC4899', '#6366F1']
            
            for i, category in enumerate(categories):
                result.append({
                    'name': category.name,
                    'value': category.business_count * 1000,  # Mock revenue
                    'orders': category.business_count * 50,  # Mock orders
                    'color': colors[i % len(colors)]
                })
            
            return result
        except:
            return [
                {'name': 'Food', 'value': 45230, 'orders': 1234, 'color': '#3B82F6'},
                {'name': 'Fashion', 'value': 32100, 'orders': 892, 'color': '#10B981'},
                {'name': 'Electronics', 'value': 28900, 'orders': 678, 'color': '#F59E0B'},
                {'name': 'Home Decor', 'value': 19200, 'orders': 445, 'color': '#8B5CF6'}
            ]
    
    def get_top_businesses(self, date_range='30d'):
        """Get top performing businesses."""
        start_date = self.get_date_range_filter(date_range)
        
        businesses = Business.objects.filter(
            created_at__lte=start_date
        ).select_related('owner').order_by('-created_at')[:10]
        
        result = []
        for business in businesses:
            # Mock performance data
            revenue = business.id * 100 + 5000  # Mock revenue based on ID
            orders = business.id * 5 + 50  # Mock orders based on ID
            growth = f"+{business.id % 20 + 1}%" if business.id % 5 != 0 else f"-{business.id % 5}%"  # Mock growth
            
            result.append({
                'name': business.name,
                'revenue': revenue,
                'orders': orders,
                'growth': growth,
                'status': business.status,
                'category': business.category.name if business.category else 'Unknown',
                'city': business.city,
                'created_at': business.created_at.isoformat()
            })
        
        return sorted(result, key=lambda x: x['revenue'], reverse=True)[:5]
    
    def get_user_activity(self, date_range='30d'):
        """Get user activity data."""
        start_date = self.get_date_range_filter(date_range)
        
        # Get daily user activity
        daily_activity = UserActivity.objects.filter(
            timestamp__gte=start_date
        ).annotate(
            date=TruncDay('timestamp')
        ).values('date').annotate(
            active_users=Count('user', distinct=True),
            total_activities=Count('id')
        ).order_by('date')
        
        # Get new users per day
        new_users = User.objects.filter(
            created_at__gte=start_date
        ).annotate(
            date=TruncDay('created_at')
        ).values('date').annotate(
            new_users=Count('id')
        ).order_by('date')
        
        # Combine data
        result = []
        for activity in daily_activity:
            date_str = activity['date'].strftime('%Y-%m-%d')
            new_user_count = next(
                (u['new_users'] for u in new_users if u['date'] == activity['date']), 
                0
            )
            
            result.append({
                'date': date_str,
                'activeUsers': activity['active_users'],
                'newUsers': new_user_count,
                'orders': activity['total_activities'] // 10  # Mock orders
            })
        
        # Return last 7 days if no data
        if not result:
            result = []
            for i in range(7):
                date = (timezone.now() - timedelta(days=i)).strftime('%Y-%m-%d')
                result.append({
                    'date': date,
                    'activeUsers': 800 + i * 10,
                    'newUsers': 15 + i * 2,
                    'orders': 50 + i * 5
                })
        
        return result[:10]
    
    def get_system_activity(self, date_range='30d'):
        """Get system activity logs."""
        start_date = self.get_date_range_filter(date_range)
        
        activities = UserActivity.objects.filter(
            timestamp__gte=start_date
        ).select_related('user').order_by('-timestamp')[:20]
        
        result = []
        for activity in activities:
            action_type = 'info'
            if 'approved' in activity.description:
                action_type = 'success'
            elif 'rejected' in activity.description:
                action_type = 'warning'
            elif 'error' in activity.description.lower():
                action_type = 'error'
            
            result.append({
                'time': self.get_time_ago(activity.timestamp),
                'action': activity.description,
                'user': activity.user.email if activity.user else 'System',
                'type': action_type,
                'timestamp': activity.timestamp.isoformat()
            })
        
        return result
    
    def get_time_ago(self, timestamp):
        """Get human readable time ago."""
        now = timezone.now()
        diff = now - timestamp
        
        if diff < timedelta(hours=1):
            minutes = int(diff.total_seconds() / 60)
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        elif diff < timedelta(days=1):
            hours = int(diff.total_seconds() / 3600)
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif diff < timedelta(days=7):
            days = diff.days
            return f"{days} day{'s' if days != 1 else ''} ago"
        else:
            weeks = int(diff.days / 7)
            return f"{weeks} week{'s' if weeks != 1 else ''} ago"
    
    def get(self, request):
        """Get reports data based on report type and date range."""
        report_type = request.GET.get('type', 'overview')
        date_range = request.GET.get('date_range', '30d')
        
        try:
            if report_type == 'overview':
                data = self.get_overview_stats(date_range)
            elif report_type == 'sales':
                data = {
                    'monthly': self.get_sales_by_month(date_range),
                    'categories': self.get_top_categories(date_range)
                }
            elif report_type == 'users':
                data = self.get_user_activity(date_range)
            elif report_type == 'businesses':
                data = self.get_top_businesses(date_range)
            elif report_type == 'orders':
                # Order statistics — statuses: pending/confirmed/processing/shipped/delivered/cancelled
                start_date = self.get_date_range_filter(date_range)
                try:
                    orders = Order.objects.filter(created_at__gte=start_date)
                    data = {
                        'total': orders.count(),
                        'completed': orders.filter(status='delivered').count(),
                        'pending': orders.filter(
                            status__in=['pending', 'confirmed', 'processing']
                        ).count(),
                        'cancelled': orders.filter(status='cancelled').count(),
                        'shipped': orders.filter(status='shipped').count(),
                    }
                except Exception:
                    data = {
                        'total': 0,
                        'completed': 0,
                        'pending': 0,
                        'cancelled': 0,
                        'shipped': 0,
                    }
            elif report_type == 'activity':
                data = self.get_system_activity(date_range)
            else:
                return Response(
                    {'error': 'Invalid report type'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            return Response(data)
            
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def export_report(request):
    """Export report data in various formats."""
    user = request.user
    if not user.is_authenticated or not user.is_admin_user():
        return Response(
            {'error': 'Admin access required'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    report_type = request.GET.get('type', 'overview')
    format_type = request.GET.get('format', 'pdf')
    date_range = request.GET.get('date_range', '30d')
    
    # Mock export functionality
    # In a real implementation, you would generate actual PDF/Excel files
    return Response({
        'message': f'Report {report_type} exported as {format_type}',
        'download_url': f'/api/reports/download/{report_type}.{format_type}',
        'generated_at': timezone.now().isoformat()
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def download_report(request, filename):
    """Mock download endpoint for generated reports."""
    # In a real implementation, you would return a FileResponse
    return Response({
        'message': f'Downloading file: {filename}',
        'status': 'success'
    })
