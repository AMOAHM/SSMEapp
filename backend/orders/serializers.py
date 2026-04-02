from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Order, OrderItem, OrderStatusHistory
from businesses.models import Business, Product

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField()
    product_image = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'service', 'quantity', 'price', 'product_name', 'product_image'
        ]

    def get_product_name(self, obj):
        if obj.product:
            return obj.product.name
        if obj.service:
            return obj.service.name
        return ""

    def get_product_image(self, obj):
        if obj.product and obj.product.image:
            return obj.product.image.url
        if obj.service and obj.service.image:
            return obj.service.image.url
        return None

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(source='customer.username', read_only=True)
    customer_email = serializers.CharField(source='customer.email', read_only=True)
    customer_phone = serializers.CharField(source='customer.phone', read_only=True)
    business_name = serializers.CharField(source='business.name', read_only=True)
    business_logo = serializers.ImageField(source='business.logo', read_only=True)
    business_address = serializers.CharField(source='business.address', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'customer', 'customer_name', 'customer_email', 'customer_phone',
            'business', 'business_name', 'business_logo', 'business_address',
            'status', 'subtotal', 'delivery_fee', 'tax', 'total',
            'tracking_number', 'delivery_address', 'delivery_notes', 'payment_method',
            'booking_date', 'booking_time', 'created_at', 'updated_at', 'delivered_at', 'items'
        ]
        read_only_fields = ['customer', 'subtotal', 'delivery_fee', 'tax', 'total']

class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    
    class Meta:
        model = Order
        fields = [
            'business', 'delivery_address', 'delivery_notes', 'payment_method',
            'booking_date', 'booking_time', 'items'
        ]

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        
        # Calculate totals first
        subtotal = 0
        for item_data in items_data:
            product = item_data.get('product')
            service = item_data.get('service')
            quantity = item_data.get('quantity', 1)
            
            if product:
                price = product.price
            elif service:
                price = service.price
            else:
                price = 0
                
            subtotal += price * quantity
        
        delivery_fee = 10.00
        tax = float(subtotal) * 0.03
        total = float(subtotal) + delivery_fee + tax
        
        # Create order with calculated totals
        validated_data['subtotal'] = subtotal
        validated_data['delivery_fee'] = delivery_fee
        validated_data['tax'] = tax
        validated_data['total'] = total
        
        order = Order.objects.create(**validated_data)
        
        # Create order items
        for item_data in items_data:
            product = item_data.get('product')
            service = item_data.get('service')
            
            if product:
                price = product.price
                name = product.name
                img = product.image.url if product.image else None
            elif service:
                price = service.price
                name = service.name
                img = service.image.url if service.image else None
            else:
                continue
            
            # Prepare item data
            final_item_data = {
                'product': product,
                'service': service,
                'quantity': item_data.get('quantity', 1),
                'price': price,
                'product_name': name,
                'product_image': img
            }
            
            OrderItem.objects.create(order=order, **final_item_data)
        
        return order

class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status']

class OrderStatusHistorySerializer(serializers.ModelSerializer):
    updated_by_name = serializers.CharField(source='updated_by.username', read_only=True)
    
    class Meta:
        model = OrderStatusHistory
        fields = [
            'id', 'status', 'notes', 'created_at', 'updated_by', 'updated_by_name'
        ]
        read_only_fields = ['updated_by']
