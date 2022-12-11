import json

from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from market.models import Product, Customer, Order, OrderRow

# Messages
bad_params = {"message": "Bad Params."}
duplicated_code = {"message": "Duplicated code."}
bad_request = {"message": "Bad request."}
product_not_found = {"message": "Product not found."}
not_enough_inventory = {"message": "Not enough inventory."}
can_not_be_zero = {"message": "Can not be Zero."}
username_already_existed = {"message": "Username already exists."}
customer_not_found = {"message": "Customer Not Found."}
can_not_edit_identity = {"message": "Cannot edit customer's identity and credentials."}
param_is_not_int = {"message": "Parameter must be integer."}
param_is_not_str = {"message": "Parameter must be string."}
incorrect_account_info = {"message": "Username or Password is incorrect."}
successfully_login = {"message": "You are logged in successfully."}
not_logged_in = {"message": "You are not logged in."}
successfully_logout = {"message": "You are logged out successfully."}
you_have_no_shopping_order = {"message": "You have no shopping order."}
not_enough_money = {"message": "Not enough money."}


@csrf_exempt
def insert_product(request):
    if request.method == 'POST':
        incoming_data = json.loads(request.body.decode('utf-8'))
        if len(incoming_data) is 3:
            if 'code' and 'name' and 'price' in incoming_data:
                product_check_exist = Product.objects.filter(code=incoming_data['code'])
                if product_check_exist:
                    return JsonResponse(duplicated_code, status=400)
                else:
                    Product.objects.create(code=incoming_data['code'],
                                           name=incoming_data['name'],
                                           price=incoming_data['price'])
                    return JsonResponse({"id": incoming_data['code']}, status=201)
            else:
                return JsonResponse(bad_params, status=400)
        if len(incoming_data) is 4:
            if 'code' and 'name' and 'price' and 'inventory' in incoming_data:
                product_check_exist = Product.objects.filter(code=incoming_data['code'])
                if product_check_exist:
                    return JsonResponse(duplicated_code, status=400)
                else:
                    Product.objects.create(code=incoming_data['code'],
                                           name=incoming_data['name'],
                                           price=incoming_data['price'],
                                           inventory=incoming_data['inventory'])
                    return JsonResponse({"id": incoming_data['code']}, status=201)
            else:
                return JsonResponse(bad_params, status=400)
        return JsonResponse({'message': 'hi'}, status=200)


def list_products(request):
    if request.method == 'GET':
        if 'search' in request.GET:
            all_products = Product.objects.filter(name__contains=request.GET['search'])
        else:
            all_products = Product.objects.all()
        ready_to_show = list()
        for product in all_products:
            i = {
                "id": product.id,
                "code": product.code,
                "name": product.name,
                "price": product.price,
                "inventory": product.inventory
            }
            ready_to_show.append(i)

        return JsonResponse({"products": ready_to_show}, status=200)
    else:
        return JsonResponse(bad_request, status=400)


def see_product(request, product_id):
    if request.method == 'GET':
        product = Product.objects.filter(pk=product_id)
        if product:
            product = product[0]
            return JsonResponse({
                "id": product.id,
                "code": product.code,
                "name": product.name,
                "price": product.price,
                "inventory": product.inventory
            }, status=200)
        else:
            return JsonResponse(product_not_found, status=404)


@csrf_exempt
def update_product(request, product_id):
    if request.method == 'POST':
        incoming_data = json.loads(request.body.decode('utf-8'))
        product = Product.objects.filter(pk=product_id)
        if product:
            product = product[0]
            if 'amount' in incoming_data:
                if isinstance(incoming_data['amount'], int):
                    if incoming_data['amount'] < 0:
                        if product.inventory >= abs(incoming_data['amount']):
                            product.decrease_inventory(abs(incoming_data['amount']))
                            return JsonResponse({
                                "id": product.id,
                                "code": product.code,
                                "name": product.name,
                                "price": product.price,
                                "inventory": product.inventory
                            }, status=200)
                        else:
                            return JsonResponse(not_enough_inventory, status=400)
                    elif incoming_data['amount'] is 0:
                        return JsonResponse(can_not_be_zero, status=400)
                    else:
                        product.increase_inventory(incoming_data['amount'])
                        return JsonResponse({
                            "id": product.id,
                            "code": product.code,
                            "name": product.name,
                            "price": product.price,
                            "inventory": product.inventory
                        }, status=200)
                else:
                    return JsonResponse(bad_params, status=400)
            else:
                return JsonResponse(bad_params, status=400)
        else:
            return JsonResponse(product_not_found, status=404)
    else:
        return JsonResponse(bad_request, status=400)


@csrf_exempt
def register_customer(request):
    if request.method == 'POST':
        incoming_data = json.loads(request.body.decode('utf-8'))
        for key, value in incoming_data.items():
            if not isinstance(key, str) or not isinstance(value, str):
                return JsonResponse(bad_params, status=400)
        customer_check_exist = Customer.objects.filter(user__username=incoming_data['username'])
        if customer_check_exist:
            return JsonResponse(username_already_existed, status=400)
        else:
            user = User.objects.create(username=incoming_data['username'],
                                       password=incoming_data['password'],
                                       first_name=incoming_data['first_name'],
                                       last_name=incoming_data['last_name'],
                                       email=incoming_data['email'])
            customer = Customer.objects.create(user=user,
                                               phone=incoming_data['phone'],
                                               address=incoming_data['address'])
            return JsonResponse({"id": customer.id})

    else:
        return JsonResponse(bad_request, status=400)


def list_customer(request):
    if request.method == 'GET':
        if 'search' in request.GET:
            all_customers = Customer.objects.filter(Q(user__username__contains=request.GET['search']) |
                                                    Q(user__first_name__contains=request.GET['search']) |
                                                    Q(user__last_name__contains=request.GET['search']) |
                                                    Q(address__contains=request.GET['search']))
        else:
            all_customers = Customer.objects.all()
        ready_to_show = list()
        for customer in all_customers:
            i = {
                "id": customer.id,
                "username": customer.user.username,
                "first_name": customer.user.first_name,
                "last_name": customer.user.last_name,
                "email": customer.user.email,
                "phone": customer.phone,
                "address": customer.address,
                "balance": customer.balance
            }
            ready_to_show.append(i)

        return JsonResponse({"customers": ready_to_show}, status=200)
    else:
        return JsonResponse(bad_request, status=400)


def see_customer(request, customer_id):
    if request.method == 'GET':
        customer_check_exist = Customer.objects.filter(pk=customer_id)
        if customer_check_exist:
            customer = customer_check_exist[0]
            return JsonResponse({
                "id": customer.id,
                "username": customer.user.username,
                "first_name": customer.user.first_name,
                "last_name": customer.user.last_name,
                "email": customer.user.email,
                "phone": customer.phone,
                "address": customer.address,
                "balance": customer.balance
            }, status=200)
        else:
            return JsonResponse(customer_not_found, status=404)
    else:
        return JsonResponse(bad_request, status=400)


@csrf_exempt
def edit_customer(request, customer_id):
    if request.method == 'POST':
        customer_check_exist = Customer.objects.filter(pk=customer_id)
        if customer_check_exist:
            incoming_data = json.loads(request.body.decode('utf-8'))
            customer = customer_check_exist[0]
            if 'username' in incoming_data.keys() or 'password' in incoming_data.keys() or 'id' in incoming_data.keys():
                return JsonResponse(can_not_edit_identity, status=403)
            else:
                for key, value in incoming_data.items():
                    if key == 'first_name':
                        if not isinstance(value, str):
                            return JsonResponse(param_is_not_str, status=400)
                        customer.user.first_name = value
                        customer.user.save()
                    elif key == 'last_name':
                        if not isinstance(value, str):
                            return JsonResponse(param_is_not_str, status=400)
                        customer.user.last_name = value
                        customer.user.save()
                    elif key == 'email':
                        if not isinstance(value, str):
                            return JsonResponse(param_is_not_str, status=400)
                        customer.user.email = value
                        customer.user.save()
                    elif key == 'phone':
                        if not isinstance(value, str):
                            return JsonResponse(param_is_not_str, status=400)
                        customer.phone = value
                        customer.save()
                    elif key == 'address':
                        if not isinstance(value, str):
                            return JsonResponse(param_is_not_str, status=400)
                        customer.address = value
                        customer.save()
                    elif key == 'balance':
                        if not isinstance(value, int):
                            return JsonResponse(param_is_not_int, status=400)
                        customer.balance = value
                        customer.save()
                    else:
                        return JsonResponse(bad_params, status=400)
            return JsonResponse({
                "id": customer.id,
                "username": customer.user.username,
                "first_name": customer.user.first_name,
                "last_name": customer.user.last_name,
                "email": customer.user.email,
                "phone": customer.phone,
                "address": customer.address,
                "balance": customer.balance
            }, status=200)

        else:
            return JsonResponse(customer_not_found, status=404)
    else:
        return JsonResponse(bad_request, status=400)


@csrf_exempt
def login_customer(request):
    if request.method == 'POST':
        incoming_data = json.loads(request.body.decode('utf-8'))
        if 'username' in incoming_data.keys() and 'password' in incoming_data.keys():
            customer_check_exist = Customer.objects.filter(user__username=incoming_data['username'],
                                                           user__password=incoming_data['password'])
            if customer_check_exist:
                customer = customer_check_exist[0]
                user = customer.user
                login(request, user)
                return JsonResponse(successfully_login, status=200)
            else:
                return JsonResponse(incorrect_account_info, status=404)
        else:
            return JsonResponse(bad_params, status=400)
    else:
        return JsonResponse(bad_request, status=400)


@csrf_exempt
def logout_customer(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            logout(request)
            return JsonResponse(successfully_logout, status=200)
        else:
            return JsonResponse(not_logged_in, status=403)
    else:
        return JsonResponse(bad_request, status=400)


def profile_customer(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            customer = Customer.objects.get(user=request.user)
            return JsonResponse({
                "id": customer.id,
                "username": customer.user.username,
                "first_name": customer.user.first_name,
                "last_name": customer.user.last_name,
                "email": customer.user.email,
                "phone": customer.phone,
                "address": customer.address,
                "balance": customer.balance
            }, status=200)
        else:
            return JsonResponse(not_logged_in, status=403)
    else:
        return JsonResponse(bad_request, status=400)


def see_cart(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            customer = Customer.objects.get(user=request.user)
            shopping_order = Order.objects.filter(customer=customer, status=1)
            if shopping_order:
                order = shopping_order[0]
                rows = OrderRow.objects.filter(order=order)
                items = list()
                for row in rows:
                    i = {
                        "code": row.product.code,
                        "name": row.product.name,
                        "price": row.product.price,
                        "amount": row.amount
                    }
                    items.append(i)
                if rows:
                    total_price = order.total_price
                    return JsonResponse({
                        "total_price": total_price,
                        "items": items
                    }, status=200)
                else:
                    return JsonResponse({
                        "items": items
                    }, status=200)

            else:
                return JsonResponse(you_have_no_shopping_order, status=404)

        else:
            return JsonResponse(not_logged_in, status=403)
    return JsonResponse(bad_request, status=400)


@csrf_exempt
def add_to_cart(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            incoming_data = json.loads(request.body.decode('utf-8'))
            if not incoming_data:
                return JsonResponse(bad_params, status=400)
            customer = Customer.objects.get(user=request.user)
            errors = list()
            items = list()
            for data in incoming_data:
                if 'code' in data.keys() and 'amount' in data.keys():
                    if isinstance(data['code'], str) and isinstance(data['amount'], int):
                        check_product_exist = Product.objects.filter(code=data['code'])
                        if len(check_product_exist) is 1:
                            product = check_product_exist[0]
                            order = Order.objects.filter(status=1)
                            if len(order) is 1:
                                order = order[0]
                            else:
                                Order.initiate(customer)
                                order = Order.objects.get(status=1)
                            if data['amount'] <= product.inventory:
                                Order.add_product(order, product, data['amount'])

                            else:
                                error = {
                                    "code": data['code'],
                                    "message": "Not enough inventory."
                                }
                                errors.append(error)

                        else:
                            error = {
                                "code": data['code'],
                                "message": "Product not found."
                            }
                            errors.append(error)
                    else:
                        return JsonResponse(bad_params, status=400)

                else:
                    return JsonResponse(bad_params, status=400)
            order = Order.objects.get(customer=customer, status=1)
            rows = OrderRow.objects.filter(order=order)
            total_price = order.total_price
            for row in rows:
                i = {
                    "code": row.product.code,
                    "name": row.product.name,
                    "price": row.product.price,
                    "amount": row.amount
                }
                items.append(i)
            if rows and len(errors) is 0:
                return JsonResponse({
                    "total_price": total_price,
                    "items": items
                }, status=200)
            elif rows and len(errors) > 0:
                return JsonResponse({
                    "total_price": total_price,
                    "errors": errors,
                    "items": items
                }, status=400)
            else:
                return JsonResponse({
                    "errors": errors,
                    "items": items
                }, status=200)
        else:
            return JsonResponse(not_logged_in, status=403)
    else:
        return JsonResponse(bad_request, status=400)


@csrf_exempt
def remove_from_cart(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            incoming_data = json.loads(request.body.decode('utf-8'))
            errors = list()
            items = list()
            if not incoming_data:
                return JsonResponse(bad_params, status=400)
            customer = Customer.objects.get(user=request.user)
            order = Order.objects.filter(status=1, customer=customer)
            if order:
                order = order[0]
                for data in incoming_data:
                    if 'code' in data.keys():
                        if isinstance(data['code'], str):
                            product = Product.objects.filter(code=data['code'])
                            if product:
                                product = product[0]
                                row = OrderRow.objects.filter(order=order)
                                if row:
                                    row = row[0]
                                    if 'amount' in data.keys():
                                        if isinstance(data['amount'], int):
                                            amount = data['amount']
                                        else:
                                            return JsonResponse(bad_params, status=400)
                                    else:
                                        amount = None
                                    try:
                                        Order.remove_product(order, product, amount)
                                    except ValueError:
                                        error = {
                                            "code": data['code'],
                                            "message": "Not enough amount in cart."
                                        }
                                        errors.append(error)

                                else:
                                    error = {
                                        "code": data['code'],
                                        "message": "Product not found in cart."
                                    }
                                    errors.append(error)
                            else:
                                error = {
                                    "code": data['code'],
                                    "message": "Product not found."
                                }
                                errors.append(error)
                        else:
                            return JsonResponse(bad_params, status=400)
                    else:
                        return JsonResponse(bad_params, status=400)
                order = Order.objects.get(customer=customer, status=1)
                rows = OrderRow.objects.filter(order=order)
                total_price = order.total_price
                for row in rows:
                    i = {
                        "code": row.product.code,
                        "name": row.product.name,
                        "price": row.product.price,
                        "amount": row.amount
                    }
                    items.append(i)
                if rows and len(errors) is 0:
                    return JsonResponse({
                        "total_price": total_price,
                        "items": items
                    }, status=200)
                elif rows and len(errors) > 0:
                    return JsonResponse({
                        "total_price": total_price,
                        "errors": errors,
                        "items": items
                    }, status=400)
                else:
                    return JsonResponse({
                        "errors": errors,
                        "items": items
                    }, status=200)
            else:
                return JsonResponse(you_have_no_shopping_order, status=404)
        else:
            return JsonResponse(not_logged_in, status=403)
    else:
        return JsonResponse(bad_request, status=400)


@csrf_exempt
def submit_order(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            customer = Customer.objects.get(user=request.user)
            items = list()
            try:
                order = Order.objects.get(status=1, customer=customer)
                order_id = order.pk
                Order.submit(order)
            except ValueError:
                return JsonResponse(you_have_no_shopping_order, status=404)
            except Exception as e:
                return JsonResponse({"message": "%s" % e}, status=400)
            else:
                order = Order.objects.get(pk=order_id)
                rows = OrderRow.objects.filter(order=order)
                for row in rows:
                    i = {
                        "code": row.product.code,
                        "name": row.product.name,
                        "price": row.product.price,
                        "amount": row.amount
                    }
                    items.append(i)
                return JsonResponse({
                    "id": order.pk,
                    "order_time": order.order_time,
                    "status": "submitted",
                    "total_price": order.total_price,
                    "rows": items
                }, status=200)
        else:
            return JsonResponse(not_logged_in, status=403)
    else:
        return JsonResponse(bad_request, status=400)
