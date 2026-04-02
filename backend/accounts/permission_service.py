from django.contrib.auth.models import Permission
from django.utils import timezone
from django.db import transaction
from .models import User, Role, UserRole, ResourcePermission, AccessPolicy, PermissionAuditLog


class PermissionService:
    """Service for managing user permissions and access control."""
    
    @staticmethod
    def assign_role(user, role_name, assigned_by=None, expires_at=None):
        """Assign a role to a user."""
        try:
            role = Role.objects.get(name=role_name)
            
            # Check if user already has this role
            user_role, created = UserRole.objects.get_or_create(
                user=user,
                role=role,
                defaults={
                    'assigned_by': assigned_by,
                    'expires_at': expires_at,
                    'is_active': True
                }
            )
            
            if not created:
                user_role.assigned_by = assigned_by
                user_role.expires_at = expires_at
                user_role.is_active = True
                user_role.save()
            
            # Log the action
            PermissionAuditLog.objects.create(
                user=assigned_by or user,
                target_user=user,
                action_type='role_assigned',
                description=f"Role '{role.display_name}' assigned to {user.email}",
                details={
                    'role_name': role_name,
                    'role_id': role.id,
                    'expires_at': expires_at.isoformat() if expires_at else None
                }
            )
            
            return True, f"Role '{role.display_name}' assigned successfully"
            
        except Role.DoesNotExist:
            return False, f"Role '{role_name}' not found"
        except Exception as e:
            return False, f"Error assigning role: {str(e)}"
    
    @staticmethod
    def remove_role(user, role_name, removed_by=None):
        """Remove a role from a user."""
        try:
            role = Role.objects.get(name=role_name)
            user_role = UserRole.objects.get(user=user, role=role)
            
            user_role.is_active = False
            user_role.save()
            
            # Log the action
            PermissionAuditLog.objects.create(
                user=removed_by or user,
                target_user=user,
                action_type='role_removed',
                description=f"Role '{role.display_name}' removed from {user.email}",
                details={
                    'role_name': role_name,
                    'role_id': role.id
                }
            )
            
            return True, f"Role '{role.display_name}' removed successfully"
            
        except (Role.DoesNotExist, UserRole.DoesNotExist):
            return False, f"Role assignment not found"
        except Exception as e:
            return False, f"Error removing role: {str(e)}"
    
    @staticmethod
    def grant_resource_permission(user, resource_type, permission_type, resource_id=None, granted_by=None, expires_at=None):
        """Grant a resource-specific permission to a user."""
        try:
            permission, created = ResourcePermission.objects.get_or_create(
                user=user,
                resource_type=resource_type,
                resource_id=resource_id,
                permission_type=permission_type,
                defaults={
                    'granted_by': granted_by,
                    'expires_at': expires_at,
                    'is_active': True
                }
            )
            
            if not created:
                permission.granted_by = granted_by
                permission.expires_at = expires_at
                permission.is_active = True
                permission.save()
            
            # Log the action
            PermissionAuditLog.objects.create(
                user=granted_by or user,
                target_user=user,
                action_type='permission_granted',
                description=f"Permission '{permission_type}' granted for {resource_type}",
                details={
                    'resource_type': resource_type,
                    'resource_id': resource_id,
                    'permission_type': permission_type,
                    'expires_at': expires_at.isoformat() if expires_at else None
                }
            )
            
            return True, "Permission granted successfully"
            
        except Exception as e:
            return False, f"Error granting permission: {str(e)}"
    
    @staticmethod
    def revoke_resource_permission(user, resource_type, permission_type, resource_id=None, revoked_by=None):
        """Revoke a resource-specific permission from a user."""
        try:
            permission = ResourcePermission.objects.get(
                user=user,
                resource_type=resource_type,
                resource_id=resource_id,
                permission_type=permission_type
            )
            
            permission.is_active = False
            permission.save()
            
            # Log the action
            PermissionAuditLog.objects.create(
                user=revoked_by or user,
                target_user=user,
                action_type='permission_revoked',
                description=f"Permission '{permission_type}' revoked for {resource_type}",
                details={
                    'resource_type': resource_type,
                    'resource_id': resource_id,
                    'permission_type': permission_type
                }
            )
            
            return True, "Permission revoked successfully"
            
        except ResourcePermission.DoesNotExist:
            return False, "Permission not found"
        except Exception as e:
            return False, f"Error revoking permission: {str(e)}"
    
    @staticmethod
    def has_permission(user, permission_codename):
        """Check if user has a specific permission."""
        # Check direct permissions
        if user.user_permissions.filter(codename=permission_codename).exists():
            return True
        
        # Check role-based permissions
        active_roles = UserRole.objects.filter(
            user=user,
            is_active=True
        ).select_related('role')
        
        for user_role in active_roles:
            if user_role.is_expired:
                continue
            if user_role.role.has_permission(permission_codename):
                return True
        
        # Check superuser access
        if user.is_superuser:
            return True
        
        return False
    
    @staticmethod
    def has_resource_permission(user, resource_type, permission_type, resource_id=None):
        """Check if user has permission for a specific resource."""
        # Check resource-specific permissions
        resource_permissions = ResourcePermission.objects.filter(
            user=user,
            resource_type=resource_type,
            permission_type=permission_type,
            resource_id__in=[resource_id, None] if resource_id else [None],
            is_active=True
        )
        
        for permission in resource_permissions:
            if permission.is_expired:
                continue
            return True
        
        # Check role-based permissions
        active_roles = UserRole.objects.filter(
            user=user,
            is_active=True
        ).select_related('role')
        
        for user_role in active_roles:
            if user_role.is_expired:
                continue
            
            # Check if role has manage permission for this resource type
            if user_role.role.has_permission(f'manage_{resource_type}'):
                return True
            
            # Check for specific permission type
            if user_role.role.has_permission(f'{permission_type}_{resource_type}'):
                return True
        
        # Check ownership permissions
        if permission_type == 'own' and resource_id:
            return PermissionService.check_ownership(user, resource_type, resource_id)
        
        # Check superuser access
        if user.is_superuser:
            return True
        
        return False
    
    @staticmethod
    def check_ownership(user, resource_type, resource_id):
        """Check if user owns a specific resource."""
        try:
            if resource_type == 'business':
                from businesses.models import Business
                return Business.objects.filter(id=resource_id, owner=user).exists()
            elif resource_type == 'order':
                from orders.models import Order
                return Order.objects.filter(id=resource_id, customer=user).exists()
            # Add more resource types as needed
            return False
        except:
            return False
    
    @staticmethod
    def get_user_permissions(user):
        """Get all permissions for a user."""
        permissions = set()
        
        # Direct permissions
        direct_perms = user.user_permissions.values_list('codename', flat=True)
        permissions.update(direct_perms)
        
        # Role-based permissions
        active_roles = UserRole.objects.filter(
            user=user,
            is_active=True
        ).select_related('role__permissions')
        
        for user_role in active_roles:
            if user_role.is_expired:
                continue
            role_perms = user_role.role.permissions.values_list('codename', flat=True)
            permissions.update(role_perms)
        
        return list(permissions)
    
    @staticmethod
    def get_user_roles(user):
        """Get all active roles for a user."""
        active_roles = UserRole.objects.filter(
            user=user,
            is_active=True
        ).select_related('role')
        
        roles = []
        for user_role in active_roles:
            if not user_role.is_expired:
                roles.append({
                    'id': user_role.role.id,
                    'name': user_role.role.name,
                    'display_name': user_role.role.display_name,
                    'description': user_role.role.description,
                    'assigned_at': user_role.assigned_at,
                    'expires_at': user_role.expires_at
                })
        
        return roles
    
    @staticmethod
    def evaluate_access_policies(user, resource_type=None, resource_id=None):
        """Evaluate all applicable access policies for a user."""
        applicable_permissions = set()
        
        policies = AccessPolicy.objects.filter(is_active=True).order_by('-priority')
        
        for policy in policies:
            if policy.evaluate(user, resource_type, resource_id):
                applicable_permissions.update(policy.permissions)
        
        return list(applicable_permissions)
    
    @staticmethod
    def create_default_roles():
        """Create default roles and permissions."""
        with transaction.atomic():
            # Create Customer role
            customer_role, created = Role.objects.get_or_create(
                name='customer',
                defaults={
                    'display_name': 'Customer',
                    'description': 'Regular customer with basic permissions',
                    'is_system_role': True
                }
            )
            
            # Create Business Owner role
            business_role, created = Role.objects.get_or_create(
                name='business',
                defaults={
                    'display_name': 'Business Owner',
                    'description': 'Business owner with management permissions',
                    'is_system_role': True
                }
            )
            
            # Create Admin role
            admin_role, created = Role.objects.get_or_create(
                name='admin',
                defaults={
                    'display_name': 'Administrator',
                    'description': 'System administrator with broad permissions',
                    'is_system_role': True
                }
            )
            
            # Create Super Admin role
            super_admin_role, created = Role.objects.get_or_create(
                name='super_admin',
                defaults={
                    'display_name': 'Super Administrator',
                    'description': 'Super administrator with full system access',
                    'is_system_role': True
                }
            )
            
            # Add default permissions to roles
            # (In a real implementation, you'd map actual Django permissions here)
            
    @staticmethod
    def sync_user_permissions(user):
        """Synchronize user permissions based on roles and policies."""
        # Get all permissions from roles
        role_permissions = set()
        active_roles = UserRole.objects.filter(
            user=user,
            is_active=True
        ).select_related('role__permissions')
        
        for user_role in active_roles:
            if not user_role.is_expired:
                role_perms = user_role.role.permissions.all()
                role_permissions.update(role_perms)
        
        # Get permissions from policies
        policy_permissions = PermissionService.evaluate_access_policies(user)
        
        # Combine all permissions
        all_permissions = role_permissions.union(policy_permissions)
        
        # Update user permissions (this is a simplified approach)
        # In production, you might want to handle this differently
        user.user_permissions.set(all_permissions)


class PermissionRequiredMixin:
    """Mixin for views that require specific permissions."""
    
    required_permissions = []
    require_all = False  # If True, user must have all permissions; if False, any permission
    
    def has_permission(self, user):
        """Check if user has required permissions."""
        if not self.required_permissions:
            return True
        
        if self.require_all:
            return all(PermissionService.has_permission(user, perm) for perm in self.required_permissions)
        else:
            return any(PermissionService.has_permission(user, perm) for perm in self.required_permissions)
    
    def dispatch(self, request, *args, **kwargs):
        """Override dispatch to check permissions."""
        if not self.has_permission(request.user):
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("You don't have permission to access this resource.")
        
        return super().dispatch(request, *args, **kwargs)


class ResourcePermissionMixin:
    """Mixin for views that require resource-specific permissions."""
    
    resource_type = None
    required_permission = 'read'
    resource_id_param = 'pk'
    
    def get_resource_id(self):
        """Get the resource ID from request parameters."""
        return self.kwargs.get(self.resource_id_param)
    
    def has_resource_permission(self, user):
        """Check if user has permission for the resource."""
        resource_id = self.get_resource_id()
        
        if not resource_id and self.required_permission in ['create', 'list']:
            # For create/list operations, resource_id might not be required
            return PermissionService.has_resource_permission(user, self.resource_type, self.required_permission)
        
        return PermissionService.has_resource_permission(user, self.resource_type, self.required_permission, resource_id)
    
    def dispatch(self, request, *args, **kwargs):
        """Override dispatch to check resource permissions."""
        if not self.has_resource_permission(request.user):
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied(f"You don't have {self.required_permission} permission for this {self.resource_type}.")
        
        return super().dispatch(request, *args, **kwargs)
