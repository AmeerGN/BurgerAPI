from django.utils import timezone
from datetime import datetime
from django.urls import reverse
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate, APIClient
from rest_framework import status
from django.contrib.auth.models import User, AnonymousUser
from .views import UserViewSet, StatisticsViewSet, MenuItemViewSet, OrderViewSet
from .models import MenuItem, Order

factory = APIRequestFactory(enforce_csrf_checks=True)

def make_super_user():
    user = User.objects.create_user('SuperUser', password='password')
    user.is_superuser = True
    user.is_staff = True
    user.save()
    return user

def make_normal_user():
    user = User.objects.create_user('NormalUser', password='password')
    user.save()
    return user
    
def create_menu_item(name, desc, price):
    menu_item = MenuItem.objects.create(name=name, description=desc, price=price)
    menu_item.save()
    return menu_item

class UserViewTests(APITestCase):
    def test_public_retrieve_user_orders(self):
        user = AnonymousUser()
        request = factory.get(reverse('user-orders', args=(1,)))
        force_authenticate(request, user=user)
        response = UserViewSet.as_view({'get': 'orders'})(request, pk=1)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_user_retrieve_user_orders(self):
        user = make_normal_user()
        request = factory.get(reverse('user-orders', args=(1,)))
        force_authenticate(request, user=user)
        response = UserViewSet.as_view({'get': 'orders'})(request, pk=1)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_admin_retrieve_user_orders(self):
        user = make_super_user()
        request = factory.get(reverse('user-orders', args=(1,)))
        force_authenticate(request, user=user)
        response = UserViewSet.as_view({'get': 'orders'})(request, pk=1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class MenuItemViewTests(APITestCase):
    def test_public_access_menu_items(self):
        user = AnonymousUser()
        menu_item = create_menu_item('test_item', '', '10.00')
        menu_item2 = create_menu_item('test_item2', 'test item2 desc', '10.00')
        request = factory.get('/burger/menuItems/')
        force_authenticate(request, user=user)
        response = MenuItemViewSet.as_view({'get': 'list'})(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        
    def test_public_access_one_menu_item(self):
        user = AnonymousUser()
        menu_item = create_menu_item('test_item', '', '10.00')
        request = factory.get('/burger/menuItems/')
        force_authenticate(request, user=user)
        response = MenuItemViewSet.as_view({'get': 'retrieve'})(request, pk=menu_item.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_public_make_menu_item(self):
        user = AnonymousUser()
        request = factory.post('/burger/menuItems/', {'name': 'Double Burger', 'description': 'Doubled burger', 'price': '20.00'})
        force_authenticate(request, user=user)
        response = MenuItemViewSet.as_view({'post': 'create'})(request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_user_make_menu_item(self):
        user = make_normal_user()
        request = factory.post('/burger/menuItems/', {'name': 'Double Burger', 'description': 'Doubled burger', 'price': '20.00'})
        force_authenticate(request, user=user)
        response = MenuItemViewSet.as_view({'post': 'create'})(request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_make_menu_item(self):
        user = make_super_user()
        request = factory.post('/burger/menuItems/', {'name': 'Double Burger', 'description': 'Doubled burger', 'price': '20.00'})
        force_authenticate(request, user=user)
        response = MenuItemViewSet.as_view({'post': 'create'})(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_make_same_menu_item_twice(self):
        user = make_super_user()
        menu_item = MenuItem.objects.create(name='test_item', price='10.00')
        menu_item.save()
        request = factory.post('burger/menuItems/', {'name': 'test_item', 'description': 'test burger', 'price': '20.00'})
        force_authenticate(request, user=user)
        response = MenuItemViewSet.as_view({'post': 'create'})(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class OrderViewTests(APITestCase):
    def test_public_retrieve_orders(self):
        user = AnonymousUser()
        request = factory.get('/burger/orders/')
        force_authenticate(request, user=user)
        response = OrderViewSet.as_view({'get': 'list'})(request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_make_order_without_login(self):
        client = self.client
        now = timezone.now()
        delivery_date = datetime(now.year, now.month, now.day + 1, 0, 0, 0, 0, now.tzinfo)
        response = client.post('/burger/orders/', {'address': 'Ramallah', 'time_to_deliver': str(delivery_date)}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_make_order_without_items(self):
        user = make_normal_user()
        client = self.client
        client.login(username='NormalUser', password='password')
        now = timezone.now()
        delivery_date = datetime(now.year, now.month, now.day + 1, 0, 0, 0, 0, now.tzinfo)
        response = client.post('/burger/orders/', {'address': 'Ramallah', 'time_to_deliver': str(delivery_date)}, format='json')
        client.logout()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_make_order_with_earlier_delivery(self):
        user = make_normal_user()
        menu_item = create_menu_item('item1', 'item1 desc', '18.00')
        client = self.client
        client.login(username='NormalUser', password='password')
        now = timezone.now()
        delivery_date = datetime(now.year, now.month, now.day - 1, 0, 0, 0, 0, now.tzinfo)
        response = client.post('/burger/orders/', {
            'address': 'Ramallah',
            'time_to_deliver': str(delivery_date),
            'order_items': [
                {
                    'menu_item': str(menu_item.pk),
                    'quantity': '2'
                }
            ]
        }, format='json')
        client.logout()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_make_order_with_item(self):
        user = make_normal_user()
        menu_item = create_menu_item('item1', 'item1 desc', '18.00')
        client = self.client
        client.login(username='NormalUser', password='password')
        now = timezone.now()
        delivery_date = datetime(now.year, now.month, now.day + 1, 0, 0, 0, 0, now.tzinfo)
        response = client.post('/burger/orders/', {
            'address': 'Ramallah',
            'time_to_deliver': str(delivery_date),
            'order_items': [
                {
                    'menu_item': str(menu_item.pk),
                    'quantity': '2'
                }
            ]
        }, format='json')
        client.logout()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
    def test_make_order_nonexisting_item(self):
        normal_user = make_normal_user()
        client = self.client
        now = timezone.now()
        delivery_date = datetime(now.year, now.month, now.day + 1, 0, 0, 0, 0, now.tzinfo)
        # create normal user order with an item that doesn't exist
        client.login(username='NormalUser', password='password')
        response = client.post('/burger/orders/', {
            'address': 'Ramallah',
            'time_to_deliver': str(delivery_date),
            'order_items': [
                {
                    'menu_item': '1',
                    'quantity': '2'
                }
            ]
        }, format='json')
        client.logout()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_retrieve_order(self):
        normal_user = make_normal_user()
        super_user = make_super_user()
        menu_item1 = create_menu_item('item1', 'item1 desc', '17.00')
        menu_item2 = create_menu_item('item2', 'item2 desc', '15.50')
        client = self.client
        now = timezone.now()
        delivery_date = datetime(now.year, now.month, now.day + 1, 0, 0, 0, 0, now.tzinfo)
        # create super user orders
        client.login(username='SuperUser', password='password')
        response = client.post('/burger/orders/', {
            'address': 'Ramallah',
            'time_to_deliver': str(delivery_date),
            'order_items': [
                {
                    'menu_item': str(menu_item1.pk),
                    'quantity': '2'
                }
            ]
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        order_id1 = response.data['id']
        response = client.post('/burger/orders/', {
            'address': 'Ramallah',
            'time_to_deliver': str(delivery_date),
            'order_items': [
                {
                    'menu_item': str(menu_item2.pk),
                    'quantity': '1'
                }
            ]
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        order_id2 = response.data['id']
        client.logout()
        # create normal user orders
        client.login(username='NormalUser', password='password')
        response = client.post('/burger/orders/', {
            'address': 'Ramallah',
            'time_to_deliver': str(delivery_date),
            'order_items': [
                {
                    'menu_item': str(menu_item1.pk),
                    'quantity': '2'
                },
                {
                    'menu_item': str(menu_item2.pk),
                    'quantity': '1'
                }
            ]
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        order_id3 = response.data['id']
        client.logout()
        
        # login using super user and try to get orders, it should return three orders
        client.login(username='SuperUser', password='password')
        response = client.get('/burger/orders/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)
        
        # super user should be able to view its own order
        response = client.get('/burger/orders/' + str(order_id1) + '/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # super user should be able to view other users' orders
        response = client.get('/burger/orders/' + str(order_id3) + '/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        client.logout()
        
        # login using normal user and try to get order, it should return one order
        client.login(username='NormalUser', password='password')
        response = client.get('/burger/orders/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        
        # normal user shouldn't be able to view other users' orders
        response = client.get('/burger/orders/' + str(order_id1) + '/', format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # normal user should be able to view his own order
        response = client.get('/burger/orders/' + str(order_id3) + '/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        client.logout()
        
        # anonymous user shouldn't be able to view orders or specific order
        response = client.get('/burger/orders/' + str(order_id1) + '/', format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        response = client.get('/burger/orders/' + str(order_id3) + '/', format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class StatisticsViewTests(APITestCase):
    def test_best_customer(self):
        menu_item1 = create_menu_item('item cheap', '', '5.00')
        menu_item2 = create_menu_item('item expensive', '', '20.65')
        super_user = make_super_user()
        normal_user = make_normal_user()
        now = timezone.now()
        delivery_date = datetime(now.year, now.month, now.day + 1, 0, 0, 0, 0, now.tzinfo)
        
        client = self.client
        client.login(username='NormalUser', password='password')
        # create one order with a total of 30.65
        response = client.post('/burger/orders/', {
            'address': 'Ramallah',
            'time_to_deliver': str(delivery_date),
            'order_items': [
                {
                    'menu_item': str(menu_item1.pk),
                    'quantity': '2'
                },
                {
                    'menu_item': str(menu_item2.pk),
                    'quantity': '1'
                }
            ]
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        client.logout()
        
        client.login(username='SuperUser', password='password')
        # create two orders with a total of 25.65
        response = client.post('/burger/orders/', {
            'address': 'Ramallah',
            'time_to_deliver': str(delivery_date),
            'order_items': [
                {
                    'menu_item': str(menu_item1.pk),
                    'quantity': '1'
                }
            ]
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = client.post('/burger/orders/', {
            'address': 'Ramallah',
            'time_to_deliver': str(delivery_date),
            'order_items': [
                {
                    'menu_item': str(menu_item2.pk),
                    'quantity': '1'
                }
            ]
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        response = client.get('/burger/statistics/best_customer/', {'criteria': 'number'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['id'], super_user.pk)
        response = client.get('/burger/statistics/best_customer/', {'criteria': 'revenue'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['id'], normal_user.pk)
        client.logout()
