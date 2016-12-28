# Burger Shop API
This is the API of a burger shop, clients (e.g. mobile, browser) can integrate with this API to enable their users to make orders from this shop.

The API is built based on Django REST Framework.

## Installation
Install the following (it is more preferred to install them and work on a virtualenv):
```
pip install Django
```
```
pip install djangorestframework
```
```
pip install httpie
```
## Running the project:
Run using this command:
```
python manage.py runserver
```
## How to use the API:
Main schema of the API can be found on:

* http://127.0.0.1:8000/burger/schema/


In addition to the statistics available for admins:

* http://127.0.0.1:8000/burger/best_customer?criteria=number/

* http://127.0.0.1:8000/burger/average_spending/

* http://127.0.0.1:8000/burger/monthly_revenue_report/

## Menu items and Users creation
Use Django manage.py to make a super user, then using the admin dashboard you can create users and menu items:

* http://127.0.0.1:8000/admin/

## Testing the API:
You can test get requests from the browser, and you can test it on the terminal after installing httpie, for example, you can retrieve menu items by entering the following command:
```
http GET http://127.0.0.1:8000/burger/menuItems/
```

For post requests you need to authenticate the request by adding:
```
-a user:password
```
