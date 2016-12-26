from django.utils import timezone
from django.db import models
from django.core.validators import MinValueValidator

class MenuItem(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(max_length=400, help_text="What is included in this tem, e.g. cheese, brown bread, etc", blank=True)
    price = models.DecimalField(max_digits=4, decimal_places=2)
    
    def __str__(self):
        return self.name + "    $" + str(self.price)
    
    class Meta:
        ordering = ('created',)
        

class Order(models.Model):
    STATUS_CHOICES = (
        ('N', 'New'),
        ('P', 'Processing'),
        ('O', 'On the way'),
        ('D', 'Delivered')
    )    
    
    created = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey('auth.User', related_name='orders', on_delete=models.SET_NULL, null=True, editable=False)
    address = models.CharField(max_length=250)
    time_to_deliver = models.DateTimeField(blank=True, validators=[MinValueValidator(timezone.now())])
    time_delivered = models.DateTimeField(blank=True, null=True)
    status = models.CharField(default='N', choices=STATUS_CHOICES, max_length=1)
    total_price = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    
    def is_delivered(self):
        return self.status == 'D'
    
    class Meta:
        ordering = ('created',)


class OrderItem(models.Model):
    menu_item = models.ForeignKey(MenuItem, related_name='menu_item', on_delete=models.CASCADE)
    order = models.ForeignKey(Order, related_name='order_items', on_delete=models.CASCADE, null=True)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    price = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    
    def save(self, *args, **kwargs):
        self.price = self.menu_item.price * self.quantity
        super(OrderItem, self).save(*args, **kwargs)
