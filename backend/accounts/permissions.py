from django.contrib.auth.models import Permission
from django.db import models
from django.utils.translation import gettext_lazy as _


class Role(models.Model):
    """Role model for granular permissions management."""
    
    name = models.CharField(_('role name'), max_length=100, unique=True)
    display_name = models.CharField(_('display name'), max_length=100)
    description = models.TextField(_('description'), blank=True)
    permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('permissions'),
        blank=True,
        related_name='roles'
    )
    is_system_role = models.BooleanField(_('system role'), default=False)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Role')
        verbose_name_plural = _('Roles')
        ordering = ['name']
    
    def __str__(self):
        return self.display_name
    
    def has_permission(self, permission_codename):
        """Check if role has a specific permission."""
        return self.permissions.filter(codename=permission_codename).exists()


class UserRole(models.Model):
    """User role assignment with additional metadata."""
    
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='user_roles'
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='role_users'
    )
    assigned_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_roles'
    )
    assigned_at = models.DateTimeField(_('assigned at'), auto_now_add=True)
    expires_at = models.DateTimeField(_('expires at'), blank=True, null=True)
    is_active = models.BooleanField(_('active'), default=True)
    
    class Meta:
        verbose_name = _('User Role')
        verbose_name_plural = _('User Roles')
        unique_together = ['user', 'role']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['role', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.role.display_name}"
    
    @property
    def is_expired(self):
        """Check if role assignment has expired."""
        from django.utils import timezone
        return self.expires_at and self.expires_at < timezone.now()


class PermissionGroup(models.Model):
    """Group of permissions for easier management."""
    
    name = models.CharField(_('group name'), max_length=100, unique=True)
    display_name = models.CharField(_('display name'), max_length=100)
    description = models.TextField(_('description'), blank=True)
    permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('permissions'),
        blank=True,
        related_name='permission_groups'
    )
    
    class Meta:
        verbose_name = _('Permission Group')
        verbose_name_plural = _('Permission Groups')
        ordering = ['name']
    
    def __str__(self):
        return self.display_name


class ResourcePermission(models.Model):
    """Resource-specific permissions for fine-grained access control."""
    
    RESOURCE_TYPES = (
        ('business', _('Business')),
        ('order', _('Order')),
        ('product', _('Product')),
        ('review', _('Review')),
        ('category', _('Category')),
        ('user', _('User')),
        ('admin', _('Admin')),
    )
    
    PERMISSION_TYPES = (
        ('create', _('Create')),
        ('read', _('Read')),
        ('update', _('Update')),
        ('delete', _('Delete')),
        ('list', _('List')),
        ('manage', _('Manage')),
        ('own', _('Own')),
    )
    
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='resource_permissions'
    )
    resource_type = models.CharField(_('resource type'), max_length=20, choices=RESOURCE_TYPES)
    resource_id = models.PositiveIntegerField(_('resource ID'), null=True, blank=True)
    permission_type = models.CharField(_('permission type'), max_length=10, choices=PERMISSION_TYPES)
    granted_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='granted_permissions'
    )
    granted_at = models.DateTimeField(_('granted at'), auto_now_add=True)
    expires_at = models.DateTimeField(_('expires at'), blank=True, null=True)
    is_active = models.BooleanField(_('active'), default=True)
    
    class Meta:
        verbose_name = _('Resource Permission')
        verbose_name_plural = _('Resource Permissions')
        indexes = [
            models.Index(fields=['user', 'resource_type', 'permission_type']),
            models.Index(fields=['resource_type', 'resource_id']),
            models.Index(fields=['user', 'is_active']),
        ]
        unique_together = ['user', 'resource_type', 'resource_id', 'permission_type']
    
    def __str__(self):
        return f"{self.user.email} - {self.permission_type} {self.resource_type}"
    
    @property
    def is_expired(self):
        """Check if permission has expired."""
        from django.utils import timezone
        return self.expires_at and self.expires_at < timezone.now()


class AccessPolicy(models.Model):
    """Access policies for automated permission management."""
    
    name = models.CharField(_('policy name'), max_length=100, unique=True)
    description = models.TextField(_('description'))
    conditions = models.JSONField(_('conditions'), default=dict)
    permissions = models.JSONField(_('permissions'), default=list)
    is_active = models.BooleanField(_('active'), default=True)
    priority = models.PositiveIntegerField(_('priority'), default=0)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Access Policy')
        verbose_name_plural = _('Access Policies')
        ordering = ['-priority', 'name']
    
    def __str__(self):
        return self.name
    
    def evaluate(self, user, resource_type=None, resource_id=None):
        """Evaluate if policy applies to user and resource."""
        # This is a simplified evaluation - in production, you'd want more sophisticated logic
        if not self.is_active:
            return False
        
        conditions = self.conditions
        
        # Check user role conditions
        if 'roles' in conditions:
            if not any(role in conditions['roles'] for role in user.get_roles()):
                return False
        
        # Check user status conditions
        if 'account_status' in conditions:
            if user.account_status not in conditions['account_status']:
                return False
        
        # Check verification conditions
        if 'is_verified' in conditions:
            if user.is_verified != conditions['is_verified']:
                return False
        
        # Check resource-specific conditions
        if resource_type and 'resource_types' in conditions:
            if resource_type not in conditions['resource_types']:
                return False
        
        return True


class PermissionAuditLog(models.Model):
    """Audit log for permission changes."""
    
    ACTION_TYPES = (
        ('role_assigned', _('Role Assigned')),
        ('role_removed', _('Role Removed')),
        ('permission_granted', _('Permission Granted')),
        ('permission_revoked', _('Permission Revoked')),
        ('policy_created', _('Policy Created')),
        ('policy_updated', _('Policy Updated')),
        ('policy_deleted', _('Policy Deleted')),
    )
    
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='permission_audit_logs'
    )
    target_user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='target_permission_logs'
    )
    action_type = models.CharField(_('action type'), max_length=20, choices=ACTION_TYPES)
    description = models.TextField(_('description'))
    details = models.JSONField(_('details'), default=dict)
    ip_address = models.GenericIPAddressField(_('IP address'), blank=True, null=True)
    user_agent = models.TextField(_('user agent'), blank=True)
    timestamp = models.DateTimeField(_('timestamp'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Permission Audit Log')
        verbose_name_plural = _('Permission Audit Logs')
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['target_user', 'timestamp']),
            models.Index(fields=['action_type']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.get_action_type_display()} - {self.timestamp}"
