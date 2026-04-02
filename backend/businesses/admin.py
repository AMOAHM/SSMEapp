from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Business, BusinessImage, Product, Favorite


class BusinessStatusFilter(admin.SimpleListFilter):
    """Custom filter for business status categorization."""
    
    title = _('approval status')
    parameter_name = 'approval_status'
    
    def lookups(self, request, model_admin):
        return [
            ('pending', _('Pending Approval')),
            ('approved', _('Approved')),
            ('rejected', _('Rejected')),
            ('suspended', _('Suspended')),
        ]
    
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(status=self.value())
        return queryset


class BusinessImageInline(admin.TabularInline):
    """Inline admin for business images."""
    model = BusinessImage
    extra = 1
    readonly_fields = ('created_at',)


class ProductInline(admin.TabularInline):
    """Inline admin for products."""
    model = Product
    extra = 1
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    """Business admin configuration."""
    
    list_display = ('name', 'owner', 'category', 'city', 'status', 'featured', 'created_at', 'approval_status')
    list_filter = (BusinessStatusFilter, 'status', 'featured', 'category', 'city', 'created_at')
    search_fields = ('name', 'description', 'owner__email', 'city')
    list_editable = ('status', 'featured')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    inlines = [BusinessImageInline, ProductInline]
    actions = ['approve_businesses', 'reject_businesses', 'suspend_businesses']
    
    fieldsets = (
        (None, {
            'fields': ('owner', 'name', 'description', 'category')
        }),
        ('Contact Information', {
            'fields': ('phone', 'email', 'website', 'address', 'city')
        }),
        ('Status', {
            'fields': ('status', 'featured')
        }),
        ('Media', {
            'fields': ('logo',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('owner', 'category')
    
    def approval_status(self, obj):
        """Display approval status with color coding."""
        if obj.status == 'pending':
            return '⏳ Pending'
        elif obj.status == 'approved':
            return '✅ Approved'
        elif obj.status == 'rejected':
            return '❌ Rejected'
        elif obj.status == 'suspended':
            return '⚠️ Suspended'
        return obj.status
    approval_status.short_description = 'Approval Status'
    
    def approve_businesses(self, request, queryset):
        """Approve selected businesses."""
        count = queryset.filter(status='pending').update(status='approved')
        self.message_user(request, f'{count} businesses approved successfully.')
    approve_businesses.short_description = 'Approve selected businesses'
    
    def reject_businesses(self, request, queryset):
        """Reject selected businesses."""
        count = queryset.filter(status='pending').update(status='rejected')
        self.message_user(request, f'{count} businesses rejected successfully.')
    reject_businesses.short_description = 'Reject selected businesses'
    
    def suspend_businesses(self, request, queryset):
        """Suspend selected businesses."""
        count = queryset.update(status='suspended')
        self.message_user(request, f'{count} businesses suspended successfully.')
    suspend_businesses.short_description = 'Suspend selected businesses'
    
    def get_list_filter(self, request):
        """Customize list filters."""
        filters = super().get_list_filter(request)
        # Add custom filters for better categorization
        return filters


@admin.register(BusinessImage)
class BusinessImageAdmin(admin.ModelAdmin):
    """Business image admin configuration."""
    
    list_display = ('business', 'alt_text', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('business__name', 'alt_text')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Product admin configuration."""
    
    list_display = ('name', 'business', 'price', 'in_stock', 'created_at')
    list_filter = ('in_stock', 'created_at')
    search_fields = ('name', 'description', 'business__name')
    list_editable = ('in_stock',)
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (None, {
            'fields': ('business', 'name', 'description', 'price')
        }),
        ('Status', {
            'fields': ('in_stock',)
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Favorite admin configuration."""
    
    list_display = ('user', 'business', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'business__name')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
