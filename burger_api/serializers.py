from django.contrib.auth.models import User
from rest_framework import serializers
from .models import MenuItem, Order, OrderItem
from decimal import Decimal


class UserSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializes User model
    """
    # Serialize the orders requested by this user
    orders = serializers.HyperlinkedRelatedField(many=True, view_name='order-detail', read_only=True)

    class Meta:
        model = User
        fields = ('url', 'id', 'username', 'orders')


class MenuItemSerializer(serializers.ModelSerializer):
    """
    Serializes MenuItem model
    """
    class Meta:
        model = MenuItem
        fields = ('id', 'url', 'name', 'description', 'price')


class OrderItemSerializer(serializers.ModelSerializer):
    """
    Serializes OrderItem model
    """
    class Meta:
        model = OrderItem
        fields = ('menu_item', 'quantity', 'price', 'order')
        


class OrderSerializer(serializers.ModelSerializer):
    """
    Serializes Order model
    """
    
    # Serialize the items included in this order
    order_items = OrderItemSerializer(many=True)
    class Meta:
        model = Order
        fields = ('url', 'id', 'owner', 'order_items', 'total_price', 'address', 'time_to_deliver', 'time_delivered', 'status')
    
    # this is needed in order to create order items and associate them with the order
    def create(self, validated_data):
        items_data = validated_data.pop('order_items')
        order = Order.objects.create(**validated_data) # create the order first
        # create order items and assciate them with the order
        for item in items_data:
            OrderItem.objects.create(order=order, **item)
        # compute order total price and save it
        order.total_price = Decimal(0.0)
        for item in OrderItem.objects.filter(order=order):
            order.total_price += item.price
        order.save()
        return order
