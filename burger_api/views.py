from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.utils import timezone
import datetime
from decimal import Decimal
from .models import MenuItem, Order
from .serializers import MenuItemSerializer, OrderSerializer, UserSerializer
from .permissions import IsAdminOrReadOnly, IsAllowedToOrder
from rest_framework import permissions, renderers, viewsets
from rest_framework.decorators import list_route, detail_route
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.renderers import JSONRenderer

class UserViewSet(viewsets.ViewSet):
    """
    Used to retrieve user's orders by the admin (the user can retrieve his own orders using '/burger/orders/')
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes=(permissions.IsAdminUser,)
    
    def retrieve(self, request, pk=None):
        serializer = self.serializer_class(User.objects.filter(pk=pk), many=True, context={'request': request})
        return Response(serializer.data)
    
    @detail_route(methods=['get'], permission_classes=(permissions.IsAdminUser,))
    def orders(self, request, pk=None):
        queryset = User.objects.all()
        user = get_object_or_404(queryset, pk=pk)
        queryset = Order.objects.filter(owner=user)
        serializer = OrderSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
        
class StatisticsViewSet(viewsets.ViewSet):
    """
    Used to retrieve different statistics (admin use only)
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes=(permissions.IsAdminUser,)
    
    @list_route(methods=['get'])
    def best_customer(self, request):
        """
        Return information about best customer in a year based on the criteria selected:
        1. 'number': the most ordering customer
        2. 'revenue': the most paying customer
        """
        criteria = 'number' # the default criteria
        if request.query_params and request.query_params['criteria']:
            criteria = request.query_params['criteria']
        now = timezone.now()
        year_ago = datetime.datetime(now.year - 1, now.month, now.day, now.hour, now.minute, now.second, now.microsecond, now.tzinfo)
        best_user_criterias = {
            'number': self.get_most_ordering_customer,
            'revenue': self.get_most_paying_customer
        }
        best_user_id = best_user_criterias[criteria](year_ago, now)            
        best_user = User.objects.filter(pk=best_user_id)
        serializer = self.serializer_class(best_user, many=True, context={'request': request})
        print serializer.data
        return Response(serializer.data)
    
    @list_route(methods=['get'], renderer_classes = (JSONRenderer, ))
    def average_spending(self, request):
        """
        Return the average spending per customer
        """
        users = User.objects.all()
        content = []
        for user in users:
            total_spending = Decimal('0.0')
            user_orders = Order.objects.filter(owner=user)
            if user_orders and user_orders.count:
                for order in user_orders:
                    total_spending += order.total_price
                average_spending = total_spending / len(user_orders)
                content.append({'user': user.username, 'average spending': average_spending})
        return Response(content)
    
    @list_route(methods=['get'], renderer_classes = (JSONRenderer, ))
    def monthly_revenue_report(self, request):
        """
        Return the monthly revenue in a year
        """
        now = timezone.now()
        # read year from parameter, default is current year
        year = now.year
        if request.query_params and request.query_params['year']:
            try:
                year = int(request.query_params['year'])
            except:
                year = now.year
        months = []
        content = {}
        content['year'] = year
        for i in range(0, 12):
            current_month = i + 1
            start_date = datetime.datetime(year, current_month, 1, 0, 0, 0, 0, now.tzinfo)
            end_date = datetime.datetime(year if current_month < 12 else (year + 1), (current_month % 12) + 1, 1, 0, 0, 0, 0, now.tzinfo)
            orders = Order.objects.filter(created__range = [start_date, end_date])
            month_revenue = Decimal('0.0')
            for order in orders:
                month_revenue += order.total_price
            months.append({'month': start_date.strftime("%B"), 'revenue': month_revenue})
        content['report'] = months
        return Response(content)
    
    def get_most_ordering_customer(self, year_ago, now):
        best_user_id = -1
        highest_num_of_orders = 0
        for user in User.objects.all():
            num_of_orders = len(Order.objects.filter(owner=user, created__range=[year_ago, now]))
            if num_of_orders > highest_num_of_orders:
                highest_num_of_orders = num_of_orders
                best_user_id = user.id
        return best_user_id
    
    def get_most_paying_customer(self, year_ago, now):
        best_user_id = -1
        highest_revenue = Decimal('0.0')
        for user in User.objects.all():
            user_orders = Order.objects.filter(owner=user, created__range=[year_ago, now])
            user_revenue = Decimal('0.0')
            for order in user_orders:
                user_revenue += order.total_price
            if user_revenue > highest_revenue:
                highest_revenue = user_revenue
                best_user_id = user.id
        return best_user_id

class MenuItemViewSet(viewsets.ModelViewSet):
    """
    Allow public access to retrieve MenuItem/s
    Allow admin access only to create a MenuItem
    """
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = (IsAdminOrReadOnly,)

class OrderViewSet(viewsets.ModelViewSet):
    """
    Allow access to orders only by authinticated users
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = (permissions.IsAuthenticated, IsAllowedToOrder,)
    
    def perform_create(self, serializer):
        # set the owner before saving
        serializer.save(owner=self.request.user)
    
    def get_queryset(self):
        # admin can retrieve all the orders
        if self.request.user.is_superuser:
            return Order.objects.all()
        else: # normal user retrieve only his orders
            return Order.objects.filter(owner=self.request.user)
    

