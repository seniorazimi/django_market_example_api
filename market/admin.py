from django.contrib import admin
from django.contrib.auth.models import User

from market.models import Customer, Order, OrderRow, Product

# Register your models here.
admin.site.register(Customer)
admin.site.register(Order)
admin.site.register(OrderRow)
admin.site.register(Product)