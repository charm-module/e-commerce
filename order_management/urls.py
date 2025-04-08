from django.urls import path
from.import views
app_name = 'order_management'

urlpatterns=[
    path('wishlist/',views.wishlist,name='wishlist'),
    path('add_to_wishlist/<int:product_id>/',views.add_to_wishlist,name='add_to_wishlist'),
    path('remove_from_wishlist/<int:product_id>/',views.remove_from_wishlist,name='remove_from_wishlist'),
    path('cart',views.cart,name='cart'),
    path('add_to_cart/<int:product_id>/',views.add_to_cart,name='add_to_cart'),
    path('remove_from_cart/<int:product_id>/cart',views.remove_from_cart,name='remove_from_cart'),
    path('confirmation',views.confirmation,name='confirmation'),
    path('checkout',views.checkout,name='checkout'),
    path('remove_cart_quantity/<int:product_id>/',views.remove_cart_quantity,name='remove_cart_quantity'),
    path('add_cart_quantity/<int:product_id>/',views.add_cart_quantity,name='add_cart_quantity'),
    path('proceed_to_pay/',views.razorPayCheck,name="razorpaycheck"),
    path('place_order/', views.placeOrder, name='place_order'),
    path('order-complete/',views.orderComplete, name='order_complete'),
    path('cancel-order/<int:id>/',views.cancelOrder, name='cancel_order'),
]
        






    
