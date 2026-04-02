from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from categories.models import Category


class Business(models.Model):
    """Business model for SSME platform."""
    
    STATUS_CHOICES = (
        ('pending', _('Pending Approval')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
        ('suspended', _('Suspended')),
    )
    
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='businesses',
        verbose_name=_('owner')
    )
    name = models.CharField(_('business name'), max_length=200)
    description = models.TextField(_('description'))
    website = models.URLField(_('website'), blank=True)
    phone = models.CharField(_('phone'), max_length=20)
    email = models.EmailField(_('business email'))
    address = models.TextField(_('address'))
    city = models.CharField(_('city'), max_length=100)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='businesses',
        verbose_name=_('category')
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    featured = models.BooleanField(_('featured'), default=False)
    logo = models.ImageField(_('logo'), upload_to='business_logos/', blank=True, null=True)
    business_password = models.CharField(_('business password'), max_length=128, blank=True)
    rejection_reason = models.TextField(_('rejection reason'), blank=True)
    suspension_reason = models.TextField(_('suspension reason'), blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Business')
        verbose_name_plural = _('Businesses')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.city}"
    
    @property
    def average_rating(self):
        """Calculate average rating from reviews."""
        reviews = self.reviews.all()
        if reviews:
            return sum(review.rating for review in reviews) / len(reviews)
        return 0
    
    @property
    def review_count(self):
        """Return the number of reviews."""
        return self.reviews.count()
    
    @property
    def is_approved(self):
        """Check if business is approved."""
        return self.status == 'approved'


class BusinessImage(models.Model):
    """Business images model."""
    
    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name=_('business')
    )
    image = models.ImageField(_('image'), upload_to='business_images/')
    alt_text = models.CharField(_('alt text'), max_length=200, blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Business Image')
        verbose_name_plural = _('Business Images')
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.business.name} - {self.id}"


class Product(models.Model):
    """Product model for businesses."""
    
    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name=_('business')
    )
    name = models.CharField(_('product name'), max_length=200)
    description = models.TextField(_('description'), blank=True)
    price = models.DecimalField(_('price'), max_digits=10, decimal_places=2)
    image = models.ImageField(_('product image'), upload_to='product_images/', blank=True, null=True)
    in_stock = models.BooleanField(_('in stock'), default=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.business.name}"


class Favorite(models.Model):
    """User favorite businesses."""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name=_('user')
    )
    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name='favorited_by',
        verbose_name=_('business')
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Favorite')
        verbose_name_plural = _('Favorites')
        unique_together = ['user', 'business']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.business.name}"


class Service(models.Model):
    """Service model for businesses."""
    
    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name='services',
        verbose_name=_('business')
    )
    name = models.CharField(_('service name'), max_length=200)
    description = models.TextField(_('description'), blank=True)
    price = models.DecimalField(_('price'), max_digits=10, decimal_places=2)
    duration = models.CharField(_('duration'), max_length=100, blank=True, help_text="e.g., 1 hour, 30 mins")
    image = models.ImageField(_('service image'), upload_to='service_images/', blank=True, null=True)
    is_active = models.BooleanField(_('is active'), default=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Service')
        verbose_name_plural = _('Services')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.business.name}"
