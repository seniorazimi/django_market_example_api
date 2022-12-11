from django.urls import path

from . import views

urlpatterns = [
    path('product/insert/', views.insert_product),
    path('product/list/', views.list_products,),
    path('product/<int:product_id>/', views.see_product),
    path('product/<int:product_id>/edit_inventory/', views.update_product),
    path('customer/register/', views.register_customer),
    path('customer/list/', views.list_customer),
    path('customer/<int:customer_id>/', views.see_customer),
    path('customer/<int:customer_id>/edit/', views.edit_customer),
    path('customer/login/', views.login_customer),
    path('customer/logout/', views.logout_customer),
    path('customer/profile/', views.profile_customer),
    path('shopping/cart/', views.see_cart),
    path('shopping/cart/add_items/', views.add_to_cart),
    path('shopping/cart/remove_items/', views.remove_from_cart),
    path('shopping/submit/', views.submit_order)

]
