from django.shortcuts import render
from order_management .models import Order,OrderProduct,UserCoupon
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required



# Create your views here.

@login_required(login_url='userloginpage')
@never_cache
def myorders(request):
    orders=Order.objects.filter(user=request.user).order_by('-created_at')
    context ={
        'orders':orders
    }

    return render(request,'further/myorders.html',context)


@login_required(login_url='userloginpage')
@never_cache
def viewOrder(request, id):
    order =Order.objects.filter(id=id,user=request.user).first()
    order =Order.objects.filter(id=id,user=request.user).first()
    orderitems = OrderProduct.objects.filter(order=order)
    try:
     userCoupon = UserCoupon.objects.get(order=order)
    except:
      userCoupon={"used":False}
   
    context={
        'order': order,
        'orderitems':orderitems,
        'UserCoupon':UserCoupon,
    }
    return render(request,'further/vieworder.html',context)

