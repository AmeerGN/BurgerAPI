from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.utils import timezone
import datetime
from .models import MenuItem, Order
from .serializers import MenuItemSerializer, OrderSerializer, UserSerializer
from .permissions import IsAdminOrReadOnly, IsAllowedToOrder
from rest_framework import permissions, renderers, viewsets
from rest_framework.decorators import list_route, detail_route
from rest_framework.response import Response
from rest_framework.request import Request

class UserViewSet(viewsets.ViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes=(permissions.IsAdminUser,)
    
    def retrieve(self, request, pk=None):
        queryset = User.objects.all()
        user = get_object_or_404(queryset, pk=pk)
        serializer = self.serializer_class(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    
    @detail_route(methods=['get'], permission_classes=(permissions.IsAdminUser,))
    def orders(self, request, pk=None):
        queryset = User.objects.all()
        user = get_object_or_404(queryset, pk=pk)
        queryset = Order.objects.filter(owner=user)
        serializer = OrderSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    
    @list_route(methods=['get'], permission_classes=(permissions.IsAdminUser,))
    def best_customer(self, request):
        now = timezone.now()
        year_ago = datetime.datetime(now.year - 1, now.month, now.day, now.hour, now.minute, now.second, now.microsecond, now.tzinfo)
        orders_in_a_year = Order.objects.filter(created__range = [year_ago, now])
        highest_num_of_orders = 0
        user_order_map = dict()
        best_user_id = -1
        for order in orders_in_a_year:
            order_owner = order.owner
            if order_owner not in user_order_map:
                user_order_map[order_owner] = set()
            user_order_map[order_owner].add(order)
            if len(user_order_map[order_owner]) > highest_num_of_orders:
                highest_num_of_orders = len(user_order_map[order_owner])
                best_user_id = order_owner.id
        best_user = User.objects.filter(pk=best_user_id)
        serializer = self.serializer_class(best_user, many=True, context={'request': request})
        return Response(serializer.data)
        

class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = (permissions.IsAuthenticated, IsAdminOrReadOnly)

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = (permissions.IsAuthenticated, IsAllowedToOrder)
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    
    def get_queryset(self):
        if self.request.user.is_superuser:
            return Order.objects.all()
        else:
            return Order.objects.filter(owner=self.request.user)
    

