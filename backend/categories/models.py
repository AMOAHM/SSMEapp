from django.db import models
from django.utils.translation import gettext_lazy as _


class Category(models.Model):
    """Business category model."""
    
    name = models.CharField(_('name'), max_length=100, unique=True)
    description = models.TextField(_('description'), blank=True)
    icon = models.CharField(_('icon'), max_length=50, blank=True, help_text=_('Emoji or icon name'))
    is_active = models.BooleanField(_('active'), default=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @property
    def business_count(self):
        """Return the number of businesses in this category."""
        return self.businesses.filter(status='approved').count()
