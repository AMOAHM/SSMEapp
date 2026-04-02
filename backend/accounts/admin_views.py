from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from .models import User
from .admin_serializers import AdminSerializer, AdminCreateSerializer, AdminUpdateSerializer

User = get_user_model()

class AdminViewSet(viewsets.ModelViewSet):
    """ViewSet for admin user management."""
    
    queryset = User.objects.filter(role='admin')
    serializer_class = AdminSerializer
    permission_classes = [permissions.IsAuthenticated]  # Restore proper authentication
    pagination_class = None
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_active', 'is_verified', 'role']
    search_fields = ['email', 'first_name', 'last_name']
    ordering_fields = ['created_at', 'email']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return AdminCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return AdminUpdateSerializer
        return AdminSerializer
    
    def get_queryset(self):
        user = self.request.user
        # Superusers can manage all admins, regular admins can only manage themselves
        if user.is_superuser:
            return User.objects.filter(role='admin')
        else:
            return User.objects.filter(role='admin', id=user.id)
    
    def perform_create(self, serializer):
        # Only superusers can create new admins
        if not self.request.user.is_superuser:
            return Response(
                {'error': 'Only superusers can create admin accounts'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().perform_create(serializer)
    
    def perform_update(self, serializer):
        # Superusers can update any admin, regular admins can only update themselves
        if not self.request.user.is_superuser and serializer.instance.id != self.request.user.id:
            return Response(
                {'error': 'You can only update your own account'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().perform_update(serializer)
    
    def perform_destroy(self, instance):
        # Superusers can delete any admin, regular admins cannot delete any admin (including themselves)
        if not self.request.user.is_superuser:
            return Response(
                {'error': 'Admin accounts cannot be deleted'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().perform_destroy(instance)
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """Toggle active status of an admin."""
        admin = self.get_object()
        admin.is_active = not admin.is_active
        admin.save()
        
        serializer = self.get_serializer(admin)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def toggle_verified(self, request, pk=None):
        """Toggle verified status of an admin."""
        admin = self.get_object()
        admin.is_verified = not admin.is_verified
        admin.save()
        
        serializer = self.get_serializer(admin)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get admin statistics."""
        user = request.user
        
        if not user.is_superuser:
            return Response(
                {'error': 'Access denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        total_admins = User.objects.filter(role='admin').count()
        active_admins = User.objects.filter(role='admin', is_active=True).count()
        verified_admins = User.objects.filter(role='admin', is_verified=True).count()
        
        return Response({
            'total_admins': total_admins,
            'active_admins': active_admins,
            'verified_admins': verified_admins,
            'inactive_admins': total_admins - active_admins,
            'unverified_admins': total_admins - verified_admins
        })
