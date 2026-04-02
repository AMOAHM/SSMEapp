from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from businesses.models import Business


class Review(models.Model):
    """Review model for businesses."""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name=_('user')
    )
    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name=_('business')
    )
    rating = models.IntegerField(
        _('rating'),
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text=_('Rating from 1 to 5 stars')
    )
    comment = models.TextField(_('comment'), blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Review')
        verbose_name_plural = _('Reviews')
        unique_together = ['user', 'business']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.business.name} - {self.rating}★"
