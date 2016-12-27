from django.urls import reverse
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate, APIClient
from rest_framework import status
from django.contrib.auth.models import User, AnonymousUser
from .views import UserViewSet, StatisticsViewSet, MenuItemViewSet, OrderViewSet
from .models import MenuItem

factory = APIRequestFactory(enforce_csrf_checks=True)

def make_super_user():
    user = User.objects.create_user('SuperUser', password='password')
    user.is_superuser = True
    user.save()
    return user

def make_normal_user():
    user = User.objects.create_user('NormalUser', password='password')
    user.save()
    return user

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
    
#   def test_admin_retrieve_user_orders(self):
#        user = make_super_user()
#        request = factory.get(reverse('user-orders', args=(1,)))
#        force_authenticate(request, user=user)
#        response = UserViewSet.as_view({'get': 'orders'})(request, pk=1)
#        self.assertEqual(response.status_code, status.HTTP_200_OK)

class MenuItemViewTests(APITestCase):
    def test_public_access_menu_items(self):
        user = AnonymousUser()
        menu_item = MenuItem.objects.create(name='test_item', price='10.00')
        menu_item.save()
        menu_item2 = MenuItem.objects.create(name='test_item2', description='test item2 desc', price='10.00')
        menu_item2.save()
        request = factory.get('/burger/menuItems/')
        force_authenticate(request, user=user)
        response = MenuItemViewSet.as_view({'get': 'list'})(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(len(response.data), 0)
        
    def test_public_access_one_menu_item(self):
        user = AnonymousUser()
        menu_item = MenuItem.objects.create(name='test_item', price='10.00')
        menu_item.save()
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
