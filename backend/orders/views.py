from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from .models import Order, OrderItem, OrderStatusHistory
from .serializers import (
    OrderSerializer, OrderCreateSerializer, OrderStatusUpdateSerializer,
    OrderStatusHistorySerializer
)
from businesses.models import Business

def _send_order_receipt_email(order):
    """Helper to send order receipt email to customer."""
    try:
        subject = f"Order Confirmation #{order.id} - {order.business.name}"
        html_message = render_to_string('emails/order_receipt.html', {
            'order': order,
            'frontend_url': getattr(settings, 'FRONTEND_URL', 'http://localhost:5173'),
        })
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [order.customer.email],
            html_message=html_message,
            fail_silently=True
        )
    except Exception as e:
        print(f"Failed to send order receipt email: {str(e)}")

def _send_status_update_email(order, notes=""):
    """Helper to send status update email to customer."""
    try:
        subject = f"Order #{order.id} update: {order.get_status_display()} - {order.business.name}"
        html_message = render_to_string('emails/order_status_update.html', {
            'order': order,
            'notes': notes,
            'frontend_url': getattr(settings, 'FRONTEND_URL', 'http://localhost:5173'),
        })
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [order.customer.email],
            html_message=html_message,
            fail_silently=True
        )
    except Exception as e:
        print(f"Failed to send order status update email: {str(e)}")

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(customer=user)

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        if self.action in ['update_status', 'partial_update']:
            return OrderStatusUpdateSerializer
        return OrderSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save(customer=request.user)
        
        # Create initial status history
        OrderStatusHistory.objects.create(
            order=order,
            status='pending',
            updated_by=request.user
        )
        
        # Send receipt email
        _send_order_receipt_email(order)
            
        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        order = self.get_object()
        serializer = OrderStatusUpdateSerializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        old_status = order.status
        new_status = serializer.validated_data['status']
        
        serializer.save()
        
        # Create status history entry
        OrderStatusHistory.objects.create(
            order=order,
            status=new_status,
            notes=request.data.get('notes', ''),
            updated_by=request.user
        )
        
        # Set delivered_at if status is delivered
        if new_status == 'delivered' and old_status != 'delivered':
            order.delivered_at = timezone.now()
            order.save()
        
        # Notify customer
        _send_status_update_email(order, request.data.get('notes', ''))
        
        return Response(OrderSerializer(order).data)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        order = self.get_object()
        
        if order.status in ['shipped', 'delivered']:
            return Response(
                {'error': 'Cannot cancel order that has been shipped or delivered'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = 'cancelled'
        order.save()
        
        # Create status history entry
        OrderStatusHistory.objects.create(
            order=order,
            status='cancelled',
            notes=request.data.get('notes', 'Order cancelled by customer'),
            updated_by=request.user
        )
        
        return Response(OrderSerializer(order).data)

    @action(detail=True, methods=['get'])
    def status_history(self, request, pk=None):
        order = self.get_object()
        history = OrderStatusHistory.objects.filter(order=order).order_by('-created_at')
        serializer = OrderStatusHistorySerializer(history, many=True)
        return Response(serializer.data)


class BusinessOrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        business_id = self.kwargs['business_id']
        business = get_object_or_404(Business, id=business_id, owner=self.request.user)
        return Order.objects.filter(business=business)

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return OrderStatusUpdateSerializer
        return OrderSerializer

    @action(detail=True, methods=['patch'])
    def update_status(self, request, business_id=None, pk=None):
        order = self.get_object()
        serializer = OrderStatusUpdateSerializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        old_status = order.status
        new_status = serializer.validated_data['status']
        
        serializer.save()
        
        # Create status history entry
        OrderStatusHistory.objects.create(
            order=order,
            status=new_status,
            notes=request.data.get('notes', ''),
            updated_by=request.user
        )
        
        # Set delivered_at if status is delivered
        if new_status == 'delivered' and old_status != 'delivered':
            order.delivered_at = timezone.now()
            order.save()
        
        # Notify customer
        _send_status_update_email(order, request.data.get('notes', ''))
        
        return Response(OrderSerializer(order).data)
