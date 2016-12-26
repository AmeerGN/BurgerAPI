from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
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
    
    @detail_route(methods=['get'], permission_classes=(permissions.IsAdminUser,))
    def orders(self, request, pk=None):
        queryset = User.objects.all()
        user = get_object_or_404(queryset, pk=pk)
        queryset = Order.objects.filter(owner=user)
        serializer = OrderSerializer(queryset, many=True, context={'request': request})
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
    

