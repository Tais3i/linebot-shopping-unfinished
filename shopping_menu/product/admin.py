from django.contrib import admin

from .models import Category,OrderDetail,Order
from .models import Product

class OrderDetailInline(admin.TabularInline):
    model = OrderDetail

class OrderAdmin(admin.ModelAdmin):
    inlines = (OrderDetailInline,)
    list_display = ('customer','ordertime')

# Register your models here
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderDetail)