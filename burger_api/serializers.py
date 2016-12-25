from django.contrib.auth.models import User
from rest_framework import serializers
from .models import MenuItem, Order, OrderItem
from decimal import Decimal


class UserSerializer(serializers.HyperlinkedModelSerializer):
    orders = serializers.HyperlinkedRelatedField(many=True, view_name='order-detail', read_only=True)

    class Meta:
        model = User
        fields = ('url', 'id', 'username', 'orders')


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ('id', 'name', 'description', 'price')


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ('menu_item', 'quantity', 'price', 'order')
        


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True)
    class Meta:
        model = Order
        fields = ('url', 'id', 'owner', 'order_items', 'total_price', 'address', 'time_to_deliver', 'time_delivered', 'status')
    
    def create(self, validated_data):
        items_data = validated_data.pop('order_items')
        order = Order.objects.create(**validated_data)
        for item in items_data:
            OrderItem.objects.create(order=order, **item)
        order.total_price = Decimal(0.0)
        for item in OrderItem.objects.filter(order=order):
            order.total_price += item.price
        order.save()
        return order
