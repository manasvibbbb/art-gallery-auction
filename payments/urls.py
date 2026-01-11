from django.urls import path
from . import views

urlpatterns = [
    # Cart management
    path('cart/', views.view_cart, name='view_cart'),
    path('add-to-cart/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),

    # Custom art orders
    path('customize/', views.customize_art, name='customize_art'),
    path('custom-order/<int:pk>/', views.custom_order_detail, name='custom_order_detail'),
    path('my-custom-orders/', views.my_custom_orders, name='my_custom_orders'),
    path('artist-update-order/<int:pk>/', views.artist_update_order_status, name='artist_update_order_status'),

    # Regular orders and payments
    path('checkout/<int:pk>/', views.checkout, name='checkout'),
    path('payment/<int:order_id>/', views.payment, name='payment'),
    path('payment-success/<int:payment_id>/', views.payment_success, name='payment_success'),
    path('my-orders/', views.my_orders, name='my_orders'),
]
