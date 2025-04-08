from django.contrib import admin
from .models import Wishlist,Cart,DeliveryDetails,Coupon,UserCoupon,Payment,Order,OrderProduct

# Register your models here.
admin.site.register(Wishlist)
admin.site.register(Cart)
admin.site.register(DeliveryDetails)
admin.site.register(Coupon)
admin.site.register(UserCoupon)
admin.site.register(Payment)
admin.site.register(Order)
admin.site.register(OrderProduct)





