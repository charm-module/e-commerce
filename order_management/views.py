from django.shortcuts import render,redirect
from .models import Wishlist,Cart,Order,OrderProduct,Payment
from admin_management .models import Products
from user_management .models import Customer
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from  order_management .models import DeliveryDetails,Coupon,UserCoupon,Payment
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django.shortcuts import render, redirect, get_object_or_404

#orderrelated
from django.http import JsonResponse
import datetime
import random
from django.conf import settings
from django.core.mail import send_mail
import razorpay
import shoeplaza.settings


# Create your views here.
@login_required(login_url='userloginpage')
@never_cache
def wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user)
    return render(request,'orders/wishlist.html',{'wishlist_items':wishlist_items})


@login_required(login_url='userloginpage')
@never_cache
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Products, id=product_id)
    created = Wishlist.objects.get_or_create(user=request.user, product=product)
    if created:
        messages.success(request, f'{product.product_name} was added to your wishlist.')
    else:
        messages.warning(request, f'{product.product_name} is already in your wishlist.')
    return redirect('order_management:wishlist')



@login_required(login_url='userloginpage')
@never_cache
def remove_from_wishlist(request, product_id):
    product = get_object_or_404(Products, id=product_id)
    Wishlist.objects.filter(user=request.user, product=product).delete()
    messages.success(request, f'{product.product_name} was removed from your wishlist.')
    return redirect('order_management:wishlist')


@login_required(login_url='userloginpage')
@never_cache
def cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    item_count = cart_items.count()
    total = sum(item.product.price * item.quantity for item in cart_items)
    return render(request, 'orders/cart.html',locals()) 


@login_required(login_url='userloginpage')
def add_to_cart(request, product_id):
    if request.user.is_authenticated:  
        current_user = request.user
        product = get_object_or_404(Products, id=product_id)
        if request.method == 'POST' :
            quantity = request.POST['quantity']
            # try to get existing cart object
            try :
                item = Cart.objects.get(user_id=current_user.id, product=product)
            except: 
                item=None
            if item is not None:
                item.quantity+=int(quantity)
        
                if product.stock >= item.quantity:
                    item.save()
                    messages.success(request, "Product added to cart")
                    return redirect('order_management:cart')
                else:
                    messages.warning(request, "Product Out Of Stock...! Can't be added to cart")
                    return redirect('order_management:cart')
            else :
                if product.stock >0:
                    if quantity is None:
                        quantity = 1
                    else:
                        quantity= int(quantity)

                    Cart.objects.create(user_id=current_user.id, product=product,quantity=quantity)
                    
                    messages.success(request, "Product added to cart")
                    return redirect('order_management:cart')
                else:
                    messages.warning(request, "Product Out Of Stock...! Can't be added to cart")
                    return redirect('order_management:cart')
        else :
            # create new cart object if none exists
            try :
                item = Cart.objects.get(user_id=current_user.id, product=product)
            except :
                item=None
            if item is not None :
                if product.stock >= item.quantity:
                    item.quantity+=1
                    item.save()
                    messages.success(request, "Product added to cart")
                    return redirect('order_management:cart')
                else:
                    messages.warning(request, "Product Out Of Stock...! Can't be added to cart")
                    return redirect('order_management:cart')
            else :
                
                if product.stock >0:
                    Cart.objects.create(user_id=current_user.id, product=product,quantity=1)
                    
                    return redirect('order_management:cart')
                else:
                    messages.warning(request, "Product Out Of Stock...! Can't be added to cart")
                    return redirect('order_management:cart')            
    else:
        messages.warning(request, "Please log in to add items to cart.")
        return redirect('order_management:cart')



@login_required(login_url='userloginpage')
@never_cache
def remove_from_cart(request, product_id):  
    product = get_object_or_404(Products, id=product_id)
    Cart.objects.filter(user=request.user, product=product).delete()
    messages.success(request, f'{product.product_name} was removed from your Cart.')
    return redirect('order_management:cart')



@login_required(login_url='userloginpage')
@never_cache
def add_cart_quantity(request,product_id):
    if request.user.is_authenticated :
        current_user=request.user
        product = get_object_or_404(Products, id=product_id)
        cart_item=Cart.objects.get(user_id=current_user.id, product=product)
        cart_item.quantity = cart_item.quantity + 1
        if (product.stock>cart_item.quantity):
            cart_item.save()
            return redirect('order_management:cart')
        else:
            messages.warning(request,"Product Out Of Stock...! Can't be added to cart")
            return redirect('order_management:cart')
    else:
        messages.warning(request, "Please log in to add items to cart.")
        return redirect('order_management:cart')



@login_required(login_url='userloginpage')
@never_cache
def remove_cart_quantity(request,product_id):
    current_user = request.user
    product = get_object_or_404(Products, id=product_id)
    cart_items = Cart.objects.filter(user_id=current_user.id, product=product)
    for cart_item in cart_items:
        if cart_item.quantity == 1:
            cart_item.delete()  # remove the item from the cart if the quantity is 1
        else:
            cart_item.quantity -= 1
            cart_item.save()  # decrement the quantity by 1
    
        return redirect('order_management:cart')



@login_required(login_url='userloginpage')
@never_cache
def checkout(request):
    total=0
    quantity=0
    amountToBePaid =0
    cart_items=None
    msg=''
    coupon_discount = 0
    coupon_code = ''
    discount = False
    coupon = ''
    try:
        current_user=request.user
        user=Customer.objects.get(id=current_user.id)
        cart_items=Cart.objects.filter(user_id=current_user.id)
        for cart_item in cart_items:
            total+=(cart_item.product.price*cart_item.quantity)
            quantity+=cart_item.quantity
        tax=(5 * total)/100
        grand_total=total+tax
        amountToBePaid = grand_total
        if ('couponCode' in request.POST):
            coupon_code = request.POST.get('couponCode')
            request.session['coupon_code']=coupon_code

            try:
                coupon = Coupon.objects.get(code = coupon_code)
                grand_total = request.POST['grand_total']
                coupon_discount = 0
                if (coupon.active):
                    try:
                        instance = UserCoupon.objects.get(user=request.user, coupon=coupon)
                    except ObjectDoesNotExist: 
                        instance = None
                    # instance = UserCoupon.objects.get(user = request.user ,coupon = coupon)
                    if(instance):
                        pass
                    else:
                        instance = UserCoupon.objects.create(user = request.user ,coupon = coupon)
                    if(not instance.used):
                        if float(grand_total) >= float(instance.coupon.min_value):
                            coupon_discount = ((float(grand_total) * float(instance.coupon.discount))/100)
                            amountToBePaid = float(grand_total) - coupon_discount
                            amountToBePaid = format(amountToBePaid, '.2f')
                            coupon_discount = format(coupon_discount, '.2f')
                            messages.success(request, "Coupon applied successfully")
                            discount=True
                            request.session['coupon_discount']=coupon_discount
                            
                        else:
                            messages.warning(request, "This coupon is only applicable for orders more than ₹{}- only!".format(instance.coupon.min_value))
                    else:
                         messages.warning(request, "Coupon is already used")
                else:
                        messages.warning(request, "Coupon is not Active!")
            except:
                  messages.warning(request, "Invalid Coupon Code!")
        else:
            try:
                instance = UserCoupon.objects.get(user=request.user, used= False)
                instance.delete()
            except ObjectDoesNotExist:
                instance = None
    except ObjectDoesNotExist:
        pass

    addresses=DeliveryDetails.objects.filter(user=current_user)
    context={
        'total':total,
        'quantity':quantity,
        'cart_items':cart_items,
        'tax':tax,
        'grand_total':grand_total,
        'user':user,
        'amountToBePaid': amountToBePaid,
        'msg':msg,
        'coupon':coupon,
        'coupon_discount': coupon_discount,
        'discount': discount,
        'addresses':addresses
    }
    return render(request,'orders/checkout.html',context)



@login_required(login_url='userloginpage')
@never_cache
def confirmation(request):
    try:
        total = request.POST.get('total')
        grand_total = request.POST.get('grand_total')
        amountToBePaid = request.POST.get('amountToBePaid')
        coupon_discount = request.POST.get('coupon_discount')
        couponCode = request.POST.get('couponCode')
        tax = request.POST.get('tax')
        newAddress_id = request.POST.get('addressSelected')
        if(newAddress_id == None):
            messages.warning(request,'Select An Address to Proceed to Checkout.')
            return redirect('order_management:checkout')
        else:
            address  = DeliveryDetails.objects.get(id = newAddress_id)

    except ObjectDoesNotExist:
        pass
    context={
        'addressSelected':address,
        'coupon_discount':coupon_discount,
        'total':total,
        'grand_total' :grand_total,
        'amountToBePaid' :amountToBePaid,
        'tax': tax,
        'couponCode':couponCode
    }
    return render (request,'orders/confirmation.html',context)



def calculateCartTotal(request):
   cart_items   = Cart.objects.filter(user=request.user)
   if not cart_items:
       pass
    #   return redirect('product_management:productlist',0)
   else:
      total = 0
      tax=0
      grand_total=0
      for cart_item in cart_items:
         total  += (cart_item.product.price * cart_item.quantity)
         tax = (5 * total) / 100
         grand_total = tax + total
   return total, tax, grand_total



@login_required(login_url='userloginpage')
@csrf_protect
@never_cache
def placeOrder(request):
   if request.method =='POST':
         if ('couponCode' in request.POST):
            instance = checkCoupon(request)
         cart_items   = Cart.objects.filter(user=request.user)
         if not cart_items:
            return redirect('product_management:productlist',0)
         newAddress_id = request.POST.get('addressSelected')
         address  = DeliveryDetails.objects.get(id = newAddress_id)
         newOrder =Order()
         newOrder.user=request.user
         newOrder.address = address
         yr = int(datetime.date.today().strftime('%Y'))
         dt = int(datetime.date.today().strftime('%d'))
         mt = int(datetime.date.today().strftime('%m'))
         d = datetime.date(yr,mt,dt)
         current_date = d.strftime("%Y%m%d")
         rand = str(random.randint(1111111,9999999))
         order_number = current_date + rand
         newPayment = Payment()
         if('payment_id' in request.POST ):
            newPayment.payment_id = request.POST.get('payment_id')
            newPayment.paid = True
         else:
            newPayment.payment_id = order_number
            payment_id  =order_number
         newPayment.payment_method = request.POST.get('payment_method')
         newPayment.customer = request.user
         newPayment.save()
         newOrder.payment = newPayment
         total, tax, grand_total = calculateCartTotal(request)
         newOrder.order_total = grand_total
         if(instance):
            if(instance.used == False):
                if float(grand_total) >= float(instance.coupon.min_value):
                    coupon_discount = ((float(grand_total) * float(instance.coupon.discount))/100)
                    amountToBePaid = float(grand_total) - coupon_discount
                    amountToBePaid = format(amountToBePaid, '.2f')
                    coupon_discount = format(coupon_discount, '.2f')
                    newOrder.order_discount = coupon_discount
                    newOrder.paid_amount = amountToBePaid
                    instance.used = True
                    newOrder.paid_amount = amountToBePaid
                    newPayment.amount_paid = amountToBePaid
                    instance.save()
                else:
                    msg='This coupon is only applicable for orders more than ₹'+ str(instance.coupon.min_value)+ '\-only!'
            else:
                newOrder.paid_amount = grand_total
                newPayment.amount_paid = grand_total
                newOrder.discount=0
                msg = 'Coupon is not valid'
         else:
            newOrder.paid_amount = grand_total
            newPayment.amount_paid = grand_total
            msg = 'Coupon not Added'
         newPayment.save()
         newOrder.payment = newPayment
         order_number = 'Shoeplaza'+ order_number
         newOrder.order_number =order_number
         #to making order number unique
         while Order.objects.filter(order_number=order_number) is None:
            order_number = 'Shoeplaza'+order_number
         newOrder.tax=tax
         newOrder.save()
         newPayment.order_id = newOrder.id
         newPayment.save()
         newOrderItems = Cart.objects.filter(user=request.user)
         for item in newOrderItems:
            OrderProduct.objects.create(
                order = newOrder,
                customer=request.user,
                product=item.product,
                product_price=item.product.price,
                quantity=item.quantity
            )
            #TO DECRESE THE QUANTITY OF PRODUCT FROM CART
            orderproduct = Products.objects.filter(id=item.product_id).first()
            if(orderproduct.stock<=0):
               messages.warning(request,'Sorry, Product out of stock!')
               orderproduct.is_available = False
               orderproduct.save()
               item.delete()
               return redirect('order_management:cart')
            elif(orderproduct.stock < item.quantity):
               messages.warning(request,  f"{orderproduct.stock} only left in cart.")
               return redirect('order_management:cart')
            else:
               orderproduct.stock -=  item.quantity
            orderproduct.save()
         if(instance):
            instance.order = newOrder
            instance.save()
        # TO CLEAR THE USER'S CART
         cart_item=Cart.objects.filter(user=request.user)
         cart_item.delete()
         messages.success(request,'Order Placed Successfully')
         payMode =  request.POST.get('payment_method')
         if (payMode == "Paid by Razorpay" ):
            return JsonResponse ({'status':"Your order has been placed successfully"})
         elif (payMode == "COD" ):
            request.session['my_context'] = {'payment_id':payment_id}
            messages.success(request,"Order Placed Succesfuly")
            return redirect('order_management:order_complete')
   return redirect('order_management:checkout')



def checkCoupon(request):
   coupon_code = request.POST['couponCode']
   try:
      coupon = Coupon.objects.get(code = coupon_code)
      try:
         instance = UserCoupon.objects.get(user=request.user, coupon=coupon)
      except ObjectDoesNotExist:
         instance = None
         if(instance):
            pass
         else:
            instance = UserCoupon.objects.create(user = request.user ,coupon = coupon)
   except:
      instance = None
   return instance



def razorPayCheck(request):
   total=0
   coupon_discount =0
   amountToBePaid = 0
   current_user=request.user
   cart_items=Cart.objects.filter(user_id=current_user.id)
   if cart_items:
      for cart_item in cart_items:
         total+=(cart_item.product.price*cart_item.quantity)
      tax=(5 * total)/100
      grand_total=total+tax
      grand_total = round(grand_total,2)
      try:
         instance = UserCoupon.objects.get(user=request.user, used=False)
         coupon = instance.coupon.code
         if float(grand_total) >= float(instance.coupon.min_value):
            coupon_discount = ((float(grand_total) * float(instance.coupon.discount))/100)
            amountToBePaid = float(grand_total) - coupon_discount
            amountToBePaid = format(amountToBePaid, '.2f')
            coupon_discount = format(coupon_discount, '.2f')
      except ObjectDoesNotExist:
         instance = None
         amountToBePaid = grand_total
         coupon_discount = 0
         coupon =None
      return JsonResponse({
         'grand_total' : grand_total,
         'coupon': coupon,
         'coupon_discount':coupon_discount,
         'amountToBePaid':amountToBePaid
      })
   else:
      return redirect('product_management:productlist',0)
   



@login_required(login_url='userloginpage')
@csrf_protect
@never_cache
def orderComplete(request):
    product_items = []
    total=0
    if ('payment_id' in request.GET):
      payment_id = request.GET.get('payment_id')
      payment = Payment.objects.get(payment_id=payment_id)
    else:
      try:
         my_context = request.session.get('my_context', {})
         payment_id = my_context['payment_id']
         payment = Payment.objects.get(payment_id=payment_id)
      except:
         user=request.user
         payment = Payment.objects.filter(customer=user, payment_method ='COD').order_by('-created_at').first()
    order_details = Order.objects.get(payment=payment)
    orderitems = OrderProduct.objects.filter(order=order_details.id)
    for order_item in orderitems:
            product = Products.objects.get(id=order_item.product.id)
            quantity = order_item.quantity
            price = order_item.product_price * quantity
            total += price
            product_items.append({
                'product': product,
                'quantity': quantity,
                'price': price
            })
    context={
        'total':total,
        'order': order_details,
        'orderitems':orderitems,
        'product_items': product_items,
    }

    return render(request, 'orders/order_completed.html',context)



@login_required(login_url='userloginpage')
@csrf_protect
@never_cache
def cancelOrder(request, id):
    client = razorpay.Client(auth=(shoeplaza.settings.API_KEY, shoeplaza.settings.RAZORPAY_SECRET_KEY))
    order = Order.objects.get(id=id, user=request.user)
    payment = order.payment
    msg = ''

    if payment.payment_method == 'Paid by Razorpay':
        payment_id = payment.payment_id
        amount = payment.amount_paid
        amount = amount * 100
        captured_amount = client.payment.capture(payment_id, amount)
        if captured_amount['status'] == 'captured':
            refund_data = {
                "payment_id": payment_id,
                "amount": amount,  # amount to be refunded in paise
                "currency": "INR",
            }
        else:
            msg = "Your bank has not completed the payment yet."
            messages.warning(request, msg)
            orderitems = OrderProduct.objects.filter(order=order)
            context = {
                'order': order,
                'orderitems': orderitems,
                'msg': msg
            }
            return render(request, 'further/vieworder.html', context)

        refund = client.payment.refund(payment_id, refund_data)

        if refund is not None:
            current_user = request.user
            order.refund_completed = True
            order.status = 'Cancelled'
            payment = order.payment
            payment.refund_id = refund['id']
            payment.save()
            order.save()
            msg = "Your order has been successfully cancelled and amount has been refunded!"
            mess = f'Hello\t{current_user.first_name},\nYour order has been canceled,Money will be refunded with in 1 hour\nThanks!'
            send_mail(
                "Shoeplaza India pvt limited - Order Cancelled",
                mess,
                settings.EMAIL_HOST_USER,
                [current_user.email],
                fail_silently=False
            )
            messages.success(request, msg)
        else:
            msg = "Your order is not cancelled because the refund could not be completed now. Please try again later. If the issue continues, CONTACT THE SUPPORT TEAM!"
            messages.warning(request, msg)
            pass
    else:
        if payment.paid:
            order.refund_completed = True
            order.status = 'Cancelled'
            msg = "YOUR ORDER HAS BEEN SUCCESSFULLY CANCELLED!"
            order.save()
            messages.success(request, msg)
        else:
            order.status = 'Cancelled'
            order.save()
            msg = "YOUR ORDER HAS BEEN SUCCESSFULLY CANCELLED!"
            messages.success(request, msg)

    orderitems = OrderProduct.objects.filter(order=order)
    context = {
        'order': order,
        'orderitems': orderitems,
        'msg': msg
    }
    return render(request, 'further/vieworder.html', context)
 





