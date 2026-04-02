from rest_framework import status, generics, permissions, viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q, Sum, Count, Avg
from django.utils import timezone
from drf_spectacular.utils import extend_schema

from accounts.models import User
from businesses.models import Business, Product, BusinessImage
from .serializers import (
    BusinessSerializer, ProductSerializer, BusinessImageSerializer,
    ProductInventorySerializer, BusinessDetailSerializer
)


class BusinessDashboardViewSet(viewsets.ModelViewSet):
    """Enhanced business dashboard for approved business owners."""
    
    queryset = Business.objects.select_related('owner', 'category').prefetch_related('images', 'products')
    serializer_class = BusinessDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Business owners can only see their own approved businesses."""
        user = self.request.user
        
        if user.role == 'business':
            return super().get_queryset().filter(owner=user, status='approved')
        elif user.role in ['admin', 'super_admin']:
            return super().get_queryset()
        else:
            return Business.objects.none()
    
    @extend_schema(
        summary="Get business dashboard",
        description="Get dashboard data for business owner.",
        responses={200: {'dashboard': 'object'}}
    )
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get business dashboard data."""
        user = request.user
        
        if user.role != 'business':
            return Response(
                {'error': 'Business access required'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        businesses = self.get_queryset()
        
        if not businesses.exists():
            return Response({
                'message': 'No approved businesses found',
                'businesses': [],
                'statistics': {},
                'products': []
            })
        
        # Get business statistics
        stats = {}
        total_products = 0
        total_revenue = 0.0
        
        for business in businesses:
            business_products = business.products.all()
            product_count = business_products.count()
            in_stock_count = business_products.filter(in_stock=True).count()
            
            # Calculate revenue (placeholder - would come from orders)
            revenue = 0.0
            
            stats[business.id] = {
                'name': business.name,
                'product_count': product_count,
                'in_stock_count': in_stock_count,
                'out_of_stock_count': product_count - in_stock_count,
                'revenue': revenue,
                'average_rating': business.average_rating,
                'review_count': business.review_count,
                'featured': business.featured
            }
            total_products += product_count
            total_revenue += revenue
        
        dashboard_data = {
            'businesses': BusinessDetailSerializer(businesses, many=True).data,
            'statistics': {
                'total_businesses': businesses.count(),
                'total_products': total_products,
                'total_revenue': total_revenue,
                'featured_businesses': businesses.filter(featured=True).count()
            },
            'recent_products': self.get_recent_products(user)
        }
        
        return Response(dashboard_data)
    
    def get_recent_products(self, user):
        """Get recent products for user's businesses."""
        products = Product.objects.filter(
            business__owner=user,
            business__status='approved'
        ).select_related('business').order_by('-created_at')[:10]
        
        return ProductSerializer(products, many=True).data
    
    @extend_schema(
        summary="Get inventory management",
        description="Get inventory data for business products.",
        responses={200: ProductInventorySerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def inventory(self, request):
        """Get inventory management data."""
        user = request.user
        
        if user.role != 'business':
            return Response(
                {'error': 'Business access required'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        business_id = request.query_params.get('business_id')
        if not business_id:
            return Response(
                {'error': 'Business ID required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify business ownership
        try:
            business = Business.objects.get(id=business_id, owner=user, status='approved')
        except Business.DoesNotExist:
            return Response(
                {'error': 'Business not found or access denied'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        products = business.products.all()
        serializer = ProductInventorySerializer(products, many=True)
        
        return Response({
            'business': BusinessDetailSerializer(business).data,
            'products': serializer.data,
            'statistics': {
                'total_products': products.count(),
                'in_stock_products': products.filter(in_stock=True).count(),
                'out_of_stock_products': products.filter(in_stock=False).count()
            }
        })
    
    @extend_schema(
        summary="Update product stock",
        description="Update product inventory stock status.",
        request={'application/json': {'in_stock': 'boolean'}},
        responses={200: ProductInventorySerializer}
    )
    @action(detail=True, methods=['patch'])
    def update_stock(self, request, pk=None):
        """Update product stock status."""
        user = request.user
        
        if user.role != 'business':
            return Response(
                {'error': 'Business access required'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        product = get_object_or_404(Product, pk=pk)
        
        # Verify business ownership
        if product.business.owner != user:
            return Response(
                {'error': 'Access denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        in_stock = request.data.get('in_stock')
        if in_stock is not None:
            product.in_stock = in_stock
            product.save()
            
            # Log activity
            from accounts.models import UserActivity
            UserActivity.objects.create(
                user=user,
                action_type='product_stock_updated',
                description=f"Updated stock for product '{product.name}' to {'in stock' if in_stock else 'out of stock'}"
            )
        
        serializer = ProductInventorySerializer(product)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Get sales analytics",
        description="Get sales analytics for business products.",
        responses={200: {'analytics': 'object'}}
    )
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Get sales analytics for business."""
        user = request.user
        
        if user.role != 'business':
            return Response(
                {'error': 'Business access required'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        business_id = request.query_params.get('business_id')
        if not business_id:
            return Response(
                {'error': 'Business ID required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            business = Business.objects.get(id=business_id, owner=user, status='approved')
        except Business.DoesNotExist:
            return Response(
                {'error': 'Business not found or access denied'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Placeholder analytics (would be calculated from actual order data)
        products = business.products.all()
        analytics = {
            'business': BusinessDetailSerializer(business).data,
            'total_products': products.count(),
            'in_stock_products': products.filter(in_stock=True).count(),
            'total_revenue': 0.0,  # Placeholder
            'total_orders': 0,  # Placeholder
            'top_products': [],  # Placeholder
            'recent_sales': [],  # Placeholder
        }
        
        return Response(analytics)
    
    @extend_schema(
        summary="Toggle featured status",
        description="Toggle featured status for business advertising.",
        request=None,
        responses={200: {'message': 'Business featured status updated'}}
    )
    @action(detail=True, methods=['post'])
    def toggle_featured(self, request, pk=None):
        """Toggle featured status for business advertising."""
        user = request.user
        
        if user.role != 'business':
            return Response(
                {'error': 'Business access required'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        business = get_object_or_404(Business, pk=pk)
        
        # Verify business ownership
        if business.owner != user:
            return Response(
                {'error': 'Access denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Toggle featured status
        business.featured = not business.featured
        business.save()
        
        # Log activity
        from accounts.models import UserActivity
        UserActivity.objects.create(
            user=user,
            action_type='business_featured_toggled',
            description=f"{'Featured' if business.featured else 'Unfeatured'} business '{business.name}'"
        )
        
        return Response({
            'message': f"Business {'featured' if business.featured else 'unfeatured'} successfully",
            'business': BusinessDetailSerializer(business).data
        })


class ProductAdvertisingViewSet(viewsets.ModelViewSet):
    """Product advertising and promotion management."""
    
    queryset = Product.objects.select_related('business').all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'business__name']
    ordering_fields = ['name', 'price', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter products based on user role and business status."""
        user = self.request.user
        
        if user.role == 'business':
            # Business owners can see their own products
            return super().get_queryset().filter(business__owner=user)
        elif user.role in ['admin', 'super_admin']:
            # Admins can see all products
            return super().get_queryset()
        else:
            # Customers can only see products from approved businesses
            return super().get_queryset().filter(business__status='approved', in_stock=True)
    
    @extend_schema(
        summary="Get advertised products",
        description="Get products for advertising/promotion.",
        responses={200: ProductSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def advertised(self, request):
        """Get advertised/featured products."""
        # Get featured products from approved businesses
        featured_products = self.get_queryset().filter(
            business__featured=True,
            business__status='approved'
        )
        
        serializer = self.get_serializer(featured_products, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Promote product",
        description="Promote a product for better visibility.",
        request={'application/json': {'promotion_type': 'string'}},
        responses={200: {'message': 'Product promoted successfully'}}
    )
    @action(detail=True, methods=['post'])
    def promote(self, request, pk=None):
        """Promote a product."""
        user = request.user
        
        if user.role != 'business':
            return Response(
                {'error': 'Business access required'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        product = get_object_or_404(Product, pk=pk)
        
        # Verify business ownership
        if product.business.owner != user:
            return Response(
                {'error': 'Access denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        promotion_type = request.data.get('promotion_type', 'featured')
        
        # Log promotion activity
        from accounts.models import UserActivity
        UserActivity.objects.create(
            user=user,
            action_type='product_promoted',
            description=f"Promoted product '{product.name}' with {promotion_type} promotion"
        )
        
        return Response({
            'message': f"Product promoted successfully with {promotion_type} promotion",
            'product': ProductSerializer(product).data
        })
