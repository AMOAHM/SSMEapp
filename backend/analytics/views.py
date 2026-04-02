from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Sum, Avg, Q, F
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model

from accounts.models import User
from businesses.models import Business, BusinessImage, Product
from orders.models import Order, OrderItem
from reviews.models import Review
from categories.models import Category

User = get_user_model()


class AnalyticsViewSet(viewsets.ViewSet):
    """ViewSet for analytics data."""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        """Only admins can access analytics."""
        if self.request.user.role not in ['admin', 'super_admin']:
            return [permissions.IsAuthenticated]
        return [permissions.IsAuthenticated]
    
    def check_permissions(self, request):
        """Check if user has admin permissions."""
        if request.user.role not in ['admin', 'super_admin']:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Admin access required")
    
    @action(detail=False, methods=['get'])
    def overview(self, request):
        """Get overview statistics."""
        time_range = request.query_params.get('range', '30d')
        
        # Calculate date range
        if time_range == '7d':
            start_date = timezone.now() - timedelta(days=7)
        elif time_range == '90d':
            start_date = timezone.now() - timedelta(days=90)
        else:  # 30d default
            start_date = timezone.now() - timedelta(days=30)
        
        # Get overview stats
        total_users = User.objects.filter(created_at__gte=start_date).count()
        total_businesses = Business.objects.filter(created_at__gte=start_date).count()
        total_orders = Order.objects.filter(created_at__gte=start_date).count()
        
        # Calculate total revenue — Order model uses 'total' field, not 'total_amount'
        total_revenue = Order.objects.filter(
            created_at__gte=start_date,
            status='delivered'
        ).aggregate(total=Sum('total'))['total'] or 0
        
        # Active users (users who logged in within the time range)
        active_users = User.objects.filter(
            last_login__gte=start_date,
            is_active=True
        ).count()
        
        # Pending businesses
        pending_businesses = Business.objects.filter(status='pending').count()
        
        return Response({
            'totalUsers': total_users,
            'totalBusinesses': total_businesses,
            'totalOrders': total_orders,
            'totalRevenue': float(total_revenue),
            'activeUsers': active_users,
            'pendingBusinesses': pending_businesses
        })
    
    @action(detail=False, methods=['get'])
    def user_growth(self, request):
        """Get user growth data over time."""
        time_range = request.query_params.get('range', '30d')
        
        if time_range == '7d':
            start_date = timezone.now() - timedelta(days=7)
            days = 7
        elif time_range == '90d':
            start_date = timezone.now() - timedelta(days=90)
            days = 90
        else:  # 30d default
            start_date = timezone.now() - timedelta(days=30)
            days = 30
        
        # Get daily user counts
        user_growth = []
        for i in range(days):
            date = start_date + timedelta(days=i)
            next_date = date + timedelta(days=1)
            count = User.objects.filter(
                created_at__gte=date,
                created_at__lt=next_date
            ).count()
            
            user_growth.append({
                'date': date.strftime('%Y-%m-%d'),
                'users': count
            })
        
        return Response(user_growth)
    
    @action(detail=False, methods=['get'])
    def business_growth(self, request):
        """Get business growth data over time."""
        time_range = request.query_params.get('range', '30d')
        
        if time_range == '7d':
            start_date = timezone.now() - timedelta(days=7)
            days = 7
        elif time_range == '90d':
            start_date = timezone.now() - timedelta(days=90)
            days = 90
        else:  # 30d default
            start_date = timezone.now() - timedelta(days=30)
            days = 30
        
        # Get daily business counts
        business_growth = []
        for i in range(days):
            date = start_date + timedelta(days=i)
            next_date = date + timedelta(days=1)
            count = Business.objects.filter(
                created_at__gte=date,
                created_at__lt=next_date
            ).count()
            
            business_growth.append({
                'date': date.strftime('%Y-%m-%d'),
                'businesses': count
            })
        
        return Response(business_growth)
    
    @action(detail=False, methods=['get'])
    def revenue_data(self, request):
        """Get revenue data over time."""
        time_range = request.query_params.get('range', '30d')
        
        if time_range == '7d':
            start_date = timezone.now() - timedelta(days=7)
            days = 7
        elif time_range == '90d':
            start_date = timezone.now() - timedelta(days=90)
            days = 90
        else:  # 30d default
            start_date = timezone.now() - timedelta(days=30)
            days = 30
        
        # Get daily revenue
        revenue_data = []
        for i in range(days):
            date = start_date + timedelta(days=i)
            next_date = date + timedelta(days=1)
            revenue = Order.objects.filter(
                created_at__gte=date,
                created_at__lt=next_date,
                status='delivered'
            ).aggregate(total=Sum('total'))['total'] or 0
            
            revenue_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'revenue': float(revenue)
            })
        
        return Response(revenue_data)
    
    @action(detail=False, methods=['get'])
    def category_distribution(self, request):
        """Get business distribution by category."""
        category_stats = Category.objects.annotate(
            business_count=Count('businesses')
        ).order_by('-business_count')[:10]  # Top 10 categories
        
        distribution = []
        for category in category_stats:
            distribution.append({
                'name': category.name,
                'value': category.business_count,
                'color': self._get_category_color(category.name)
            })
        
        return Response(distribution)
    
    @action(detail=False, methods=['get'])
    def top_businesses(self, request):
        """Get top performing businesses."""
        time_range = request.query_params.get('range', '30d')
        
        if time_range == '7d':
            start_date = timezone.now() - timedelta(days=7)
        elif time_range == '90d':
            start_date = timezone.now() - timedelta(days=90)
        else:  # 30d default
            start_date = timezone.now() - timedelta(days=30)
        
        # Get businesses with most orders and revenue
        top_businesses = Business.objects.filter(
            created_at__gte=start_date
        ).annotate(
            order_count=Count('orders'),
            total_revenue=Sum('orders__total_amount')
        ).filter(
            order_count__gt=0
        ).order_by('-total_revenue')[:10]
        
        result = []
        for business in top_businesses:
            result.append({
                'name': business.name,
                'orders': business.order_count,
                'revenue': float(business.total_revenue or 0)
            })
        
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def recent_activity(self, request):
        """Get recent platform activity."""
        activities = []
        
        # Recent business registrations
        recent_businesses = Business.objects.filter(
            status='pending'
        ).order_by('-created_at')[:5]
        
        for business in recent_businesses:
            activities.append({
                'id': business.id,
                'type': 'new_business',
                'message': f'New business registration: "{business.name}"',
                'time': self._format_time(business.created_at),
                'icon': 'Building2',
                'color': 'text-green-600'
            })
        
        # Recent orders
        recent_orders = Order.objects.select_related('customer').order_by('-created_at')[:5]
        
        for order in recent_orders:
            activities.append({
                'id': order.id,
                'type': 'new_order',
                'message': f'New order #{order.id} from {order.customer.get_full_name() or order.customer.email}',
                'time': self._format_time(order.created_at),
                'icon': 'ShoppingCart',
                'color': 'text-blue-600'
            })
        
        # Recent user registrations
        recent_users = User.objects.order_by('-created_at')[:5]
        
        for user in recent_users:
            activities.append({
                'id': user.id,
                'type': 'new_user',
                'message': f'New user registration: {user.email}',
                'time': self._format_time(user.created_at),
                'icon': 'Users',
                'color': 'text-purple-600'
            })
        
        # Sort by time
        activities.sort(key=lambda x: x['time'], reverse=True)
        
        return Response(activities[:10])  # Return top 10 activities
    
    def _get_category_color(self, category_name):
        """Get color for category."""
        colors = {
            'Food': '#3B82F6',
            'Fashion': '#10B981',
            'Electronics': '#F59E0B',
            'Home Decor': '#8B5CF6',
            'Health & Beauty': '#EC4899',
            'Sports & Fitness': '#F97316',
            'Bakery & Desserts': '#84CC16',
            'Other': '#6B7280'
        }
        return colors.get(category_name, '#6B7280')
    
    def _format_time(self, datetime_obj):
        """Format time relative to now."""
        now = timezone.now()
        diff = now - datetime_obj
        
        if diff.days > 0:
            return f"{diff.days} days ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hours ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minutes ago"
        else:
            return "Just now"
