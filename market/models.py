from django.contrib.auth.models import User
from django.db import models

# Messages
bad_value_message = "Bad value."
not_enough_inventory_message = "Not enough inventory."
not_enough_balance_message = "Not enough money."
initiate_a_order_first_message = "Initiate a order first."
you_are_shopping_message = "You are shopping."
product_not_found_message = "Product not found."
product_not_found_in_cart_message = "Product not found in your cart."
you_are_not_shopping_message = "You are not shopping."
you_have_no_rows_in_your_order_message = "You are have no rows in your order."
this_order_is_not_submitted_message = "This order is not submitted."


class Product(models.Model):
    code = models.CharField(unique=True, max_length=10)
    name = models.CharField(max_length=100)
    price = models.PositiveIntegerField()
    inventory = models.PositiveIntegerField(default=0)

    def increase_inventory(self, amount):
        if amount > 0:
            self.inventory += amount
            self.save()
        else:
            raise ValueError(bad_value_message)

    def decrease_inventory(self, amount):
        if amount > 0:
            if self.inventory >= amount:
                self.inventory -= amount
                self.save()
            else:
                raise ValueError(not_enough_inventory_message)
        else:
            raise ValueError(bad_value_message)

    def __str__(self):
        return self.code


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    balance = models.PositiveIntegerField(default=20000)

    def deposit(self, amount):
        if amount > 0:
            self.balance += amount
            self.save()
        else:
            raise ValueError(bad_value_message)

    def spend(self, amount):
        if amount > 0:
            if self.balance >= amount:
                self.balance -= amount
                self.save()
            else:
                raise ValueError(not_enough_balance_message)
        else:
            raise ValueError(bad_value_message)


class OrderRow(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    order = models.ForeignKey('Order', on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()


class Order(models.Model):
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    order_time = models.DateTimeField(auto_now_add=True)
    total_price = models.PositiveIntegerField(default=0)

    STATUS_SHOPPING = 1
    STATUS_SUBMITTED = 2
    STATUS_CANCELED = 3
    STATUS_SENT = 4
    status_choices = (
        (STATUS_SHOPPING, 'در حال خرید'),
        (STATUS_SUBMITTED, 'ثبت‌شده'),
        (STATUS_CANCELED, 'لغوشده'),
        (STATUS_SENT, 'ارسال‌شده')
    )
    status = models.IntegerField(choices=status_choices)

    @staticmethod
    def initiate(customer):
        shopping_state = Order.objects.filter(customer=customer, status=1)
        if shopping_state:
            raise Exception(you_are_shopping_message)
        else:
            Order.objects.create(customer=customer, status=1)

    def add_product(self, product, amount):
        if self.status == 1:
            cart = OrderRow.objects.filter(product=product, order=self)
            if amount > 0:
                if product.inventory >= amount:
                    self.total_price += amount * product.price
                    self.save()
                    if len(cart) is 1:
                        cart = cart[0]
                        cart.amount += amount
                        cart.save()
                        product.decrease_inventory(amount)
                    else:
                        OrderRow.objects.create(order=self, product=product, amount=amount)
                        product.decrease_inventory(amount)
                else:
                    raise ValueError(not_enough_inventory_message)
            else:
                raise ValueError(bad_value_message)
        else:
            raise Exception(initiate_a_order_first_message)

    def remove_product(self, product, amount=None):
        if self.status == 1:
            cart = OrderRow.objects.filter(order=self, product=product)
            if cart:
                cart = cart[0]
                if amount is None:
                    self.total_price -= cart.amount * product.price
                    self.save()
                    cart.delete()
                    cart.save()
                elif amount > 0:
                    if cart.amount > amount:
                        self.total_price -= amount * product.price
                        self.save()
                        cart.amount -= amount
                        cart.save()
                    elif cart.amount == amount:
                        self.total_price -= amount * product.price
                        cart.delete()
                        cart.save()
                    else:
                        raise ValueError(bad_value_message)
                else:
                    raise ValueError(bad_value_message)
            else:
                raise Exception(product_not_found_in_cart_message)
        else:
            raise Exception(initiate_a_order_first_message)

    def submit(self):
        if self.status == 1:
            rows = OrderRow.objects.filter(order=self)
            if rows:
                total_price = self.total_price
                if self.customer.balance >= total_price:
                    self.customer.spend(total_price)
                    self.status = 2
                    self.save()
                else:
                    raise Exception(not_enough_balance_message)
            else:
                raise Exception(you_have_no_rows_in_your_order_message)
        else:
            raise Exception(you_are_not_shopping_message)

    def cancel(self):
        if self.status == 2:
            cart = OrderRow.objects.filter(order=self)
            for item in cart:
                item.product.increase_inventory(item.amount)
            self.customer.deposit(self.total_price)
            self.status = 3
            self.save()
        else:
            raise Exception(this_order_is_not_submitted_message)

    def send(self):
        if self.status == 2:
            self.status = 4
            self.save()
        else:
            raise Exception(this_order_is_not_submitted_message)
