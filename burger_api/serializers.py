from django.contrib.auth.models import User
from rest_framework import serializers
from .models import MenuItem, Order, OrderItem


class UserSerializer(serializers.HyperlinkedModelSerializer):
    orders = serializers.HyperlinkedRelatedField(many=True, view_name='order-detail', read_only=True)

    class Meta:
        model = User
        fields = ('url', 'id', 'username', 'orders')


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ('menu_item', 'quantity', 'price')
    
    def create(self, validated_data):
        menu_item_data = validated_data['menu_item']
        order_item = OrderItem.objects.create(**validated_data)
        print(menu_item_data.price)
        print(order_item.quanity)
        order_item.price = menu_item_data.price * order_item.quantity
        return order_item

class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ('id', 'name', 'description', 'price')


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
        return order
