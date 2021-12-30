from django.db import models
from django.utils import timezone
# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=20)
    image = models.ImageField(upload_to='images', blank=True,  null=True, default=None)

    def __str__(self):
        return self.name 

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name 

class Order(models.Model):
    customer = models.CharField(max_length=50)
    ordertime = models.DateTimeField(default = timezone.now)
    status = models.SmallIntegerField(default=0)

    def __str__(self):
        return f'{self.customer[:6]}:{self.ordertime}'

class OrderDetail(models.Model):
    product = models.ForeignKey(to = Product, null=True, on_delete=models.SET_NULL)
    amount = models.SmallIntegerField()
    order = models.ForeignKey(to = Order, on_delete=models.CASCADE)