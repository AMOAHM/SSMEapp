from rest_framework import status, generics, permissions, viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.db.models import Q, Sum, Count, Avg
from django.utils import timezone
from drf_spectacular.utils import extend_schema

from accounts.models import User
from accounts.serializers import UserUpdateSerializer, UserProfileSerializer, AdminUserUpdateSerializer
from businesses.models import Business, Product, BusinessImage
from businesses.serializers import (
    BusinessSerializer, ProductSerializer, BusinessImageSerializer,
    BusinessApprovalSerializer, BusinessDetailSerializer
)


class BusinessManagementViewSet(viewsets.ModelViewSet):
    """Enhanced business management for admins."""
    
    queryset = Business.objects.select_related('owner', 'category').prefetch_related('images', 'products')
    serializer_class = BusinessDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'city', 'owner__email']
    ordering_fields = ['name', 'created_at', 'status', 'average_rating']
    ordering = ['-created_at']
    
    def get_permissions(self):
        """Only admins can manage businesses."""
        if self.request.user.is_admin_user():
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]
    
    def check_permissions(self, request):
        """Check if user has admin permissions."""
        if not request.user.is_admin_user():
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Admin access required")
    
    def get_queryset(self):
        """Filter businesses based on user role and status."""
        user = self.request.user
        
        if user.is_admin_user():
            # Admins can see all businesses
            queryset = super().get_queryset()
        else:
            # Business owners can only see their own businesses
            queryset = super().get_queryset().filter(owner=user)
        
        # Filter by status if provided
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset
    
    @extend_schema(
        summary="Get pending businesses",
        description="Get all businesses pending approval.",
        responses={200: BusinessSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get all pending businesses."""
        if not request.user.is_admin_user():
            return Response(
                {'error': 'Admin access required'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        pending_businesses = self.get_queryset().filter(status='pending')
        serializer = self.get_serializer(pending_businesses, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Approve business",
        description="Approve a business and notify the owner.",
        request=None,
        responses={200: {'message': 'Business approved successfully'}}
    )
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a business."""
        if not request.user.is_admin_user():
            return Response(
                {'error': 'Admin access required'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        business = get_object_or_404(Business, pk=pk)
        
        # Note: Removing strict 'pending' check to allow re-approving previously 
        # rejected or suspended businesses.
        
        # Update business status
        business.status = 'approved'
        business.rejection_reason = ''  # Clear any previous rejection reason
        business.suspension_reason = '' # Clear any previous suspension reason
        business.save()
        
        # Update user's business verification status
        business.owner.is_business_verified = True
        business.owner.account_status = 'active'
        business.owner.save()
        
        # Log activity
        from accounts.models import UserActivity
        UserActivity.objects.create(
            user=request.user,
            action_type='business_approved',
            description=f"Approved business '{business.name}'"
        )
        
        return Response({
            'message': 'Business approved successfully',
            'business': BusinessSerializer(business).data
        })
    
    @extend_schema(
        summary="Reject business",
        description="Reject a business with a reason.",
        request={'application/json': {'reason': 'string'}},
        responses={200: {'message': 'Business rejected successfully'}}
    )
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a business."""
        if not request.user.is_admin_user():
            return Response(
                {'error': 'Admin access required'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        business = get_object_or_404(Business, pk=pk)
        reason = request.data.get('reason', '')
        
        # Note: Removing strict 'pending' check to allow rejecting currently 
        # approved or suspended businesses.
        
        # Update business status
        business.status = 'rejected'
        business.rejection_reason = reason
        business.save()
        
        # Log activity
        from accounts.models import UserActivity
        UserActivity.objects.create(
            user=request.user,
            action_type='business_rejected',
            description=f"Rejected business '{business.name}'. Reason: {reason}"
        )
        
        return Response({
            'message': 'Business rejected successfully',
            'business': BusinessSerializer(business).data
        })
    
    @extend_schema(
        summary="Suspend business",
        description="Suspend a business temporarily.",
        request={'application/json': {'reason': 'string'}},
        responses={200: {'message': 'Business suspended successfully'}}
    )
    @action(detail=True, methods=['post'])
    def suspend(self, request, pk=None):
        """Suspend a business."""
        if not request.user.is_admin_user():
            return Response(
                {'error': 'Admin access required'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        business = get_object_or_404(Business, pk=pk)
        reason = request.data.get('reason', '')
        
        business.status = 'suspended'
        business.suspension_reason = reason
        business.save()
        
        # Log activity
        from accounts.models import UserActivity
        UserActivity.objects.create(
            user=request.user,
            action_type='business_suspended',
            description=f"Suspended business '{business.name}'. Reason: {reason}"
        )
        
        return Response({
            'message': 'Business suspended successfully',
            'business': BusinessSerializer(business).data
        })
    
    @extend_schema(
        summary="Get businesses by status",
        description="Get businesses categorized by their approval status.",
        responses={200: {'pending': [], 'approved': [], 'rejected': [], 'suspended': []}}
    )
    @action(detail=False, methods=['get'])
    def by_status(self, request):
        """Get businesses categorized by status."""
        if not request.user.is_admin_user():
            return Response(
                {'error': 'Admin access required'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        businesses = self.get_queryset()
        serializer = self.get_serializer
        
        return Response({
            'pending': serializer(businesses.filter(status='pending'), many=True).data,
            'approved': serializer(businesses.filter(status='approved'), many=True).data,
            'rejected': serializer(businesses.filter(status='rejected'), many=True).data,
            'suspended': serializer(businesses.filter(status='suspended'), many=True).data,
        })
    
    @extend_schema(
        summary="Get business statistics",
        description="Get statistics for business management.",
        responses={200: {'statistics': 'object'}}
    )
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get business management statistics."""
        if not request.user.is_admin_user():
            return Response(
                {'error': 'Admin access required'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        stats = {
            'total_businesses': Business.objects.count(),
            'pending_businesses': Business.objects.filter(status='pending').count(),
            'approved_businesses': Business.objects.filter(status='approved').count(),
            'rejected_businesses': Business.objects.filter(status='rejected').count(),
            'suspended_businesses': Business.objects.filter(status='suspended').count(),
            'total_products': Product.objects.count(),
            'featured_businesses': Business.objects.filter(featured=True).count(),
        }
        
        return Response(stats)


class ProductManagementViewSet(viewsets.ModelViewSet):
    """Product management for businesses and admins."""
    
    queryset = Product.objects.select_related('business').all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'business__name']
    ordering_fields = ['name', 'price', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter products based on user role."""
        user = self.request.user
        
        if user.role in ['admin', 'super_admin']:
            # Admins can see all products
            return super().get_queryset()
        elif user.role == 'business':
            # Business owners can only see their own products
            return super().get_queryset().filter(business__owner=user)
        else:
            # Customers can only see products from approved businesses
            return super().get_queryset().filter(business__status='approved')
    
    def perform_create(self, serializer):
        """Create product with proper business assignment."""
        user = self.request.user
        
        if user.role == 'business':
            # Business users can only add products to their own businesses
            business_id = self.request.data.get('business')
            if business_id:
                try:
                    business = Business.objects.get(id=business_id, owner=user, status='approved')
                    serializer.save(business=business)
                except Business.DoesNotExist:
                    from rest_framework.exceptions import ValidationError
                    raise ValidationError("You can only add products to your approved businesses.")
            else:
                from rest_framework.exceptions import ValidationError
                raise ValidationError("Business ID is required.")
        elif user.role in ['admin', 'super_admin']:
            # Admins can add products to any business
            serializer.save()
        else:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only business owners and admins can add products.")


class AdminUserManagementViewSet(viewsets.ModelViewSet):
    """Enhanced user management for admins."""
    
    queryset = User.objects.all()
    serializer_class = None  # Will be set based on action
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering_fields = ['email', 'created_at', 'role', 'account_status']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action in ['create', 'update', 'partial_update']:
            return AdminUserUpdateSerializer
        return UserProfileSerializer
    
    def get_permissions(self):
        """Only admins can manage users."""
        if self.request.user.role in ['admin', 'super_admin']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]
    
    def check_permissions(self, request):
        """Check if user has admin permissions."""
        if not request.user.is_admin_user():
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Admin access required")
    
    @extend_schema(
        summary="Create admin user",
        description="Create a new admin user.",
        request={'application/json': 'UserRegistrationSerializer'},
        responses={201: UserProfileSerializer}
    )
    def create(self, request, *args, **kwargs):
        """Create a new admin user."""
        if not request.user.is_admin_user():
            return Response(
                {'error': 'Admin access required'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Set role to admin by default for admin creation
        data = request.data.copy()
        data['role'] = 'admin'
        data['account_status'] = 'active'
        
        from accounts.serializers import UserRegistrationSerializer
        serializer = UserRegistrationSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Log activity
        from accounts.models import UserActivity
        UserActivity.objects.create(
            user=request.user,
            action_type='admin_created',
            description=f"Created admin user '{user.email}'"
        )
        
        from accounts.serializers import UserProfileSerializer
        return Response(UserProfileSerializer(user).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """Toggle active/account_status of a user."""
        if not request.user.is_admin_user():
            return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
        
        user = self.get_object()
        user.is_active = not user.is_active
        user.account_status = 'active' if user.is_active else 'suspended'
        user.save()
        
        from accounts.serializers import UserProfileSerializer
        return Response(UserProfileSerializer(user).data)

    @action(detail=True, methods=['post'])
    def toggle_verified(self, request, pk=None):
        """Toggle verified status of a user."""
        if not request.user.is_admin_user():
            return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
            
        user = self.get_object()
        user.is_verified = not user.is_verified
        user.save()
        
        from accounts.serializers import UserProfileSerializer
        return Response(UserProfileSerializer(user).data)
    
    @extend_schema(
        summary="Get user statistics",
        description="Get user management statistics.",
        responses={200: {'statistics': 'object'}}
    )
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get user management statistics."""
        if not request.user.is_admin_user():
            return Response(
                {'error': 'Admin access required'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        stats = {
            'total_users': User.objects.count(),
            'admin_users': User.objects.filter(role='admin').count(),
            'business_users': User.objects.filter(role='business').count(),
            'customer_users': User.objects.filter(role='customer').count(),
            'verified_users': User.objects.filter(is_verified=True).count(),
            'business_verified_users': User.objects.filter(is_business_verified=True).count(),
            'active_users': User.objects.filter(account_status='active').count(),
            'pending_users': User.objects.filter(account_status='pending_verification').count(),
        }
        
        return Response(stats)
