from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIRequestFactory, force_authenticate
from .views import UserViewSet, StatisticsViewSet, MenuItemViewSet, OrderViewSet
from .models import MenuItem

def make_super_user():
    user = User.objects.create_user('SuperUser', password='password')
    user.is_superuser = True
    user.save()
    return user

def make_normal_user():
    user = User.objects.create_user('NormalUser', password='password')
    user.save()
    return user

class MenuItemViewTests(TestCase):
    def test_public_access_menu_items(self):
        menu_item = MenuItem.objects.create(name='test_item', price='10.00')
        menu_item.save()
        menu_item2 = MenuItem.objects.create(name='test_item2', description='test item2 desc', price='10.00')
        menu_item2.save()
        factory = APIRequestFactory()
        request = factory.get('/burger/menuItems/')
        response = MenuItemViewSet.as_view({'get': 'list'})(request)
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(len(response.data), 0)
        
    def test_public_access_one_menu_item(self):
        menu_item = MenuItem.objects.create(name='test_item', price='10.00')
        menu_item.save()
        factory = APIRequestFactory()
        request = factory.get('/burger/menuItems/')
        response = MenuItemViewSet.as_view({'get': 'retrieve'})(request, pk=menu_item.pk)
        self.assertEqual(response.status_code, 200)
        
    def test_public_make_menu_item(self):
        factory = APIRequestFactory()
        request = factory.post('/burger/menuItems/', {'name': 'Double Burger', 'description': 'Doubled burger', 'price': '20.00'})
        response = MenuItemViewSet.as_view({'post': 'create'})(request)
        self.assertEqual(response.status_code, 403)
        
    def test_user_make_menu_item(self):
        user = make_normal_user()
        factory = APIRequestFactory()
        request = factory.post('/burger/menuItems/', {'name': 'Double Burger', 'description': 'Doubled burger', 'price': '20.00'})
        force_authenticate(request, user=user)
        response = MenuItemViewSet.as_view({'post': 'create'})(request)
        self.assertEqual(response.status_code, 403)
        
    def test_make_menu_item(self):
        user = make_super_user()
        factory = APIRequestFactory()
        request = factory.post('/burger/menuItems/', {'name': 'Double Burger', 'description': 'Doubled burger', 'price': '20.00'})
        force_authenticate(request, user=user)
        response = MenuItemViewSet.as_view({'post': 'create'})(request)
        self.assertEqual(response.status_code, 201)
    
    def test_make_same_menu_item_twice(self):
        user = make_super_user()
        menu_item = MenuItem.objects.create(name='test_item', price='10.00')
        menu_item.save()
        factory = APIRequestFactory()
        request = factory.post('burger/menuItems/', {'name': 'test_item', 'description': 'test burger', 'price': '20.00'})
        force_authenticate(request, user=user)
        response = MenuItemViewSet.as_view({'post': 'create'})(request)
        self.assertEqual(response.status_code, 400)
