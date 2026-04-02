from rest_framework import generics, permissions, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
# from django_filters.rest_framework import DjangoFilterBackend
# from django_filters import rest_framework as drf_filters
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import Business, BusinessImage, Product, Service, Favorite
from .serializers import (
    BusinessSerializer,
    BusinessCreateSerializer,
    BusinessUpdateSerializer,
    BusinessListSerializer,
    BusinessImageSerializer,
    ProductSerializer,
    ProductListSerializer,
    ServiceSerializer,
    ServiceListSerializer,
    FavoriteSerializer,
    BusinessDetailSerializer
)
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

def _send_business_status_email(business, status):
    """Send email notification to business owner about status change."""
    try:
        if status == 'approved':
            template = 'emails/business_approved.html'
            subject = f"Congratulations! Your business '{business.name}' is approved"
        elif status == 'rejected':
            template = 'emails/business_rejected.html'
            subject = f"Update on your business application: {business.name}"
        else:
            return

        html_message = render_to_string(template, {
            'business': business,
            'frontend_url': getattr(settings, 'FRONTEND_URL', 'http://localhost:5173'),
        })
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [business.owner.email],
            html_message=html_message,
            fail_silently=True
        )
    except Exception as e:
        print(f"Failed to send business status email: {str(e)}")


class IsAdminUser(permissions.BasePermission):
    """Custom permission class to check if user is admin."""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_admin_user()


class BusinessListCreateView(generics.ListCreateAPIView):
    """List and create businesses."""
    queryset = Business.objects.select_related('owner', 'category').prefetch_related('images', 'reviews')
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = None
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'city']
    ordering_fields = ['name', 'created_at', 'average_rating']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return BusinessCreateSerializer
        return BusinessListSerializer
    
    def get_permissions(self):
        # Allow anyone to create a business, but require authentication for other operations
        if self.request.method == 'POST':
            return []
        return [permissions.IsAuthenticatedOrReadOnly()]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # Only show approved businesses to public
        if not self.request.user.is_authenticated or self.request.user.role == 'customer':
            queryset = queryset.filter(status='approved')
        elif self.request.user.is_business_owner():
            queryset = queryset.filter(owner=self.request.user)
        return queryset
    
    @extend_schema(
        summary="List businesses",
        description="Retrieve a list of businesses with filtering and search capabilities.",
        parameters=[
            OpenApiParameter('category', OpenApiTypes.INT, description='Category ID'),
            OpenApiParameter('city', OpenApiTypes.STR, description='City name'),
            OpenApiParameter('featured', OpenApiTypes.BOOL, description='Featured businesses only'),
            OpenApiParameter('min_rating', OpenApiTypes.NUMBER, description='Minimum rating'),
            OpenApiParameter('max_rating', OpenApiTypes.NUMBER, description='Maximum rating'),
            OpenApiParameter('search', OpenApiTypes.STR, description='Search query'),
        ],
        responses={200: BusinessListSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Create business",
        description="Create a new business listing (business owners only).",
        responses={201: BusinessSerializer}
    )
    def post(self, request, *args, **kwargs):
        # Allow anyone to create a business (registration)
        return super().post(request, *args, **kwargs)


class BusinessDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, and delete businesses."""
    queryset = Business.objects.select_related('owner', 'category').prefetch_related('images', 'reviews', 'products')
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return BusinessUpdateSerializer
        return BusinessSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # Only show approved businesses to public
        if not self.request.user.is_authenticated or self.request.user.role == 'customer':
            queryset = queryset.filter(status='approved')
        return queryset
    
    @extend_schema(
        summary="Get business details",
        description="Retrieve detailed information about a specific business.",
        responses={200: BusinessSerializer}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update business",
        description="Update business information (business owner only).",
        responses={200: BusinessSerializer}
    )
    def patch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.owner != request.user and not request.user.is_admin_user():
            return Response(
                {'error': 'Only the business owner can update this business.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().patch(request, *args, **kwargs)
    
    @extend_schema(
        summary="Delete business",
        description="Delete a business (business owner or admin only).",
        responses={204: None}
    )
    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.owner != request.user and not request.user.is_admin_user():
            return Response(
                {'error': 'Only the business owner can delete this business.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().delete(request, *args, **kwargs)


class BusinessImageListCreateView(generics.ListCreateAPIView):
    """List and create business images."""
    serializer_class = BusinessImageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        business_id = self.kwargs['business_id']
        return BusinessImage.objects.filter(business_id=business_id)
    
    def perform_create(self, serializer):
        business_id = self.kwargs['business_id']
        business = Business.objects.get(id=business_id)
        
        # Check if user owns the business or is admin
        if business.owner != self.request.user and not self.request.user.is_admin_user():
            raise permissions.PermissionDenied("You can only add images to your own businesses.")
        
        serializer.save(business=business)


class ProductListCreateView(generics.ListCreateAPIView):
    """List and create products for a business."""
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        business_id = self.kwargs['business_id']
        return Product.objects.filter(business_id=business_id)
    
    def perform_create(self, serializer):
        business_id = self.kwargs['business_id']
        business = Business.objects.get(id=business_id)
        
        # Check if user owns the business or is admin
        if business.owner != self.request.user and not self.request.user.is_admin_user():
            raise permissions.PermissionDenied("You can only add products to your own businesses.")
        
        serializer.save(business=business)


class FavoriteListCreateView(generics.ListCreateAPIView):
    """List and create favorite businesses."""
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user).select_related('business', 'business__category')
    
    def perform_create(self, serializer):
        business_id = self.request.data.get('business')
        business = Business.objects.get(id=business_id)
        
        # Only allow favoriting approved businesses
        if business.status != 'approved':
            raise permissions.PermissionDenied("You can only favorite approved businesses.")
        
        serializer.save(user=self.request.user)


@extend_schema(
    summary="Remove favorite business",
    description="Remove a business from user's favorites.",
    responses={204: None}
)
@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def remove_favorite(request, business_id):
    """Remove a business from favorites."""
    try:
        favorite = Favorite.objects.get(user=request.user, business_id=business_id)
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Favorite.DoesNotExist:
        return Response(
            {'error': 'Business not found in favorites.'},
            status=status.HTTP_404_NOT_FOUND
        )


@extend_schema(
    summary="Get featured businesses",
    description="Retrieve featured businesses.",
    responses={200: BusinessListSerializer(many=True)}
)
@api_view(['PATCH'])
@permission_classes([permissions.IsAuthenticated, IsAdminUser])
def update_business_status(request, business_id):
    """Update business status (admin only)."""
    try:
        business = Business.objects.get(id=business_id)
        
        new_status = request.data.get('status')
        rejection_reason = request.data.get('rejection_reason', '')
        
        if new_status not in ['pending', 'approved', 'rejected']:
            return Response(
                {'error': 'Invalid status. Must be pending, approved, or rejected.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        business.status = new_status
        if new_status == 'rejected' and rejection_reason:
            business.rejection_reason = rejection_reason
        elif new_status == 'approved':
            business.rejection_reason = ''  # Clear rejection reason when approved
        
        business.save()
        
        # Notify owner
        _send_business_status_email(business, new_status)
        
        serializer = BusinessDetailSerializer(business, context={'request': request})
        return Response(serializer.data)
        
    except Business.DoesNotExist:
        return Response(
            {'error': 'Business not found.'},
            status=status.HTTP_404_NOT_FOUND
        )


@extend_schema(
    summary="Get featured businesses",
    description="Retrieve featured businesses.",
    responses={200: BusinessListSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def featured_businesses(request):
    """Get featured businesses."""
    businesses = Business.objects.filter(
        status='approved',
        featured=True
    ).select_related('owner', 'category').prefetch_related('images', 'reviews')
    
    serializer = BusinessListSerializer(businesses, many=True, context={'request': request})
    return Response(serializer.data)


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, and delete products for a business."""
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'
    lookup_url_kwarg = 'product_id'
    
    def get_queryset(self):
        business_id = self.kwargs['business_id']
        return Product.objects.filter(business_id=business_id)
    
    def check_object_permissions(self, request, obj):
        super().check_object_permissions(request, obj)
        if obj.business.owner != request.user and not request.user.is_admin_user():
            raise permissions.PermissionDenied("You can only manage products for your own businesses.")


class ServiceListCreateView(generics.ListCreateAPIView):
    """List and create services for a business."""
    serializer_class = ServiceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        business_id = self.kwargs['business_id']
        return Service.objects.filter(business_id=business_id)
    
    def perform_create(self, serializer):
        business_id = self.kwargs['business_id']
        business = Business.objects.get(id=business_id)
        
        # Check if user owns the business or is admin
        if business.owner != self.request.user and not self.request.user.is_admin_user():
            raise permissions.PermissionDenied("You can only add services to your own businesses.")
        
        serializer.save(business=business)


class ServiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, and delete services for a business."""
    serializer_class = ServiceSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'
    lookup_url_kwarg = 'service_id'
    
    def get_queryset(self):
        business_id = self.kwargs['business_id']
        return Service.objects.filter(business_id=business_id)
    
    def check_object_permissions(self, request, obj):
        super().check_object_permissions(request, obj)
        if obj.business.owner != request.user and not request.user.is_admin_user():
            raise permissions.PermissionDenied("You can only manage services for your own businesses.")


class GlobalProductListView(generics.ListAPIView):
    """Global list of products across all approved businesses."""
    serializer_class = ProductListSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Product.objects.filter(business__status='approved', in_stock=True).select_related('business')
    pagination_class = None # Or use standard pagination if preferred
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'business__name', 'business__city']
    ordering_fields = ['price', 'created_at']


class GlobalServiceListView(generics.ListAPIView):
    """Global list of services across all approved businesses."""
    serializer_class = ServiceListSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Service.objects.filter(business__status='approved', is_active=True).select_related('business')
    pagination_class = None
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'business__name', 'business__city']
    ordering_fields = ['price', 'created_at']
