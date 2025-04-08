from django.shortcuts import render,redirect
from user_management.models import Customer
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from django.contrib import auth
from .models import Category,Products,Banner
from order_management .models import Coupon,Order,Payment,OrderProduct,UserCoupon
from .forms import CouponForm
from django.core.paginator import Paginator
from django.db.models import  Sum
from django.views.decorators.cache import never_cache
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import user_passes_test




# Create your views here.
def admin_login(request): 
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password )
        if user is not None and user.is_staff:
                auth.login(request, user)
                return redirect('admindashboard')
        else:
            messages.info(request, 'Invalid username or password')
    return render(request, 'admin/admin_login.html')

@user_passes_test(lambda u: u.is_superuser)
@never_cache
def admindashboard(request):
    user=Customer.objects.all().count()
    product=Products.objects.all().count()
    category=Category.objects.all().count()
    order=Order.objects.all().count()
    coupons=Coupon.objects.all().count()
    total_income = Payment.objects.aggregate(Sum('amount_paid'))['amount_paid__sum']
    total_income = round(total_income, 2)
    cod_sum = Payment.objects.filter(payment_method='COD').aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
    cod_sum = round(cod_sum,2)
    # Calculate the payment sum for Razorpay
    razorpay_sum = Payment.objects.filter(payment_method='Paid by Razorpay').aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
    payment_percentages = calculateNumberOfOrdersByPaymentMethod()

    context={
        'user':user,
        'product':product,
        'category':category,
        'order':order,
        'coupons':coupons,
        'total_income' :total_income,
        'payment_percentages': payment_percentages,
        'cod_sum':cod_sum,
        'razorpay_sum':razorpay_sum,

    }
    return render(request,'admin/admin_dashboard.html',context)


def calculateNumberOfOrdersByPaymentMethod():
    payments = Payment.objects.all()
    payment_count = {}
    total_payments = len(payments)

    # Count the number of payments for each payment method
    for payment in payments:
        payment_count[payment.payment_method] = payment_count.get(payment.payment_method, 0) + 1
      
    # Calculate the percentage of payments for each payment method
    payment_percentages = {}
    for payment_method, count in payment_count.items():
        #key and values
        if(payment_method=="Paid by Razorpay"):
            payment_method = "Razorpay"
        payment_percentages[payment_method] = round((count / total_payments) * 100, 2)
    return payment_percentages


@user_passes_test(lambda u: u.is_superuser)
@never_cache
def manage_user(request):
    user = Customer.objects.all().order_by('id')
    return render(request, 'admin/manage_user.html', {'user':user})
 
@user_passes_test(lambda u: u.is_superuser)
@never_cache
def delete_user(request, pid):
    user = Customer.objects.get(id=pid)
    user.delete()
    messages.success(request, "User deleted successfully")
    return redirect('manage_user') 

@user_passes_test(lambda u: u.is_superuser)
@never_cache
def blockuser(request, id):
    user = get_object_or_404(Customer, id=id)
    if user.is_active:
        user.is_active = False
        user.save()
        messages.success(request, "User blocked")
        return redirect('manage_user')
    else:
        user.is_active = True
        user.save()
        messages.success(request, "User unblocked")
        return redirect('manage_user')


@user_passes_test(lambda u: u.is_superuser)
@never_cache
def view_category(request):
    category =Category.objects.all().order_by('-created')
    return render(request,'admin/view_category.html',locals())


@user_passes_test(lambda u: u.is_superuser)
@never_cache
def add_category(request):
    if request.method == "POST":
        name = request.POST['name']
        if Category.objects.filter(category_name__iexact=name.lower().replace(' ', '')).exists():
            messages.error(request, 'Category with this name already exists.')
            return redirect('add_category') 
        else:
            Category.objects.create(category_name=name)
            messages.success(request, 'Category added successfully.')
            return redirect('view_category')
    return render(request, 'admin/add_category.html')


@user_passes_test(lambda u: u.is_superuser)
@never_cache
def edit_category(request, pid):
    category = Category.objects.get(id=pid)
    if request.method == "POST":
        name = request.POST['name']
        if Category.objects.filter(category_name__iexact=name.lower().replace(' ', '')).exists():
            messages.error(request, 'Category with this name already exists.')
            return redirect('add_category')
        else:
            category.name = name
            category.save()
            messages.info (request,'Category updated')
            return redirect(view_category)
    return render(request, 'admin/edit_category.html', locals())

@user_passes_test(lambda u: u.is_superuser)
@never_cache
def delete_category(request, pid):
    category = Category.objects.get(id=pid)
    category.delete()   
    messages.info (request,'Category deleted')
    return redirect(view_category)
  

@user_passes_test(lambda u: u.is_superuser)
@never_cache
def view_product(request):
    product = Products.objects.all().order_by('product_name')
    return render(request, 'admin/view_product.html', locals())


@user_passes_test(lambda u: u.is_superuser)
@never_cache
def delete_product(request, pid):
    product = Products.objects.get(id=pid)
    product.delete()
    messages.success(request, "Product Deleted")
    return redirect('view_product')



@user_passes_test(lambda u: u.is_superuser)
@never_cache
def edit_product(request, pid):
    product = Products.objects.get(id=pid)
    category = Category.objects.all()
    if request.method == "POST":
        name = request.POST['name']
        price = request.POST['price']
        cat = request.POST['category']
        desc = request.POST['desc']
        try:
            image = request.FILES['image']
            product.image = image
            product.save()
        except:
            pass
        catobj = Category.objects.get(id=cat)
        if int(price) >= 0 :
            Products.objects.filter(id=pid).update(product_name=name, price=price, category=catobj, description=desc)
            messages.success(request, "Product Updated")
            return redirect('view_product')
        else:
            messages.success(request, "Price must positive numbers")

    return render(request, 'admin/edit_product.html', locals())
 


@user_passes_test(lambda u: u.is_superuser)
@never_cache
def add_product(request):
    category = Category.objects.all()
    if request.method == "POST":
        name = request.POST['name']
        price = request.POST['price']
        cat = request.POST['category']
        stock = request.POST['stock']
        desc = request.POST['desc']
        image = request.FILES['image']
        catobj = Category.objects.get(id=cat)
        if int(price) >= 0 and int(stock)>= 0:
             Products.objects.create(product_name=name, price=price, stock=stock, category=catobj, description=desc, images=image)
             messages.success(request, "Product added")
             return redirect('view_product')
        else:
            messages.success(request, "Price and stock must positive numbers")

    return render(request,'admin/add_product.html', locals())



@user_passes_test(lambda u: u.is_superuser)
@never_cache
def view_banner(request):
    banner = Banner.objects.all()
    return render(request,'admin/view_banner.html',{'banner':banner})



@user_passes_test(lambda u: u.is_superuser)
@never_cache
def edit_banner(request, pid):
    banner = Banner.objects.get(id=pid)
    if request.method == "POST":
        title = request.POST['title']
        description = request.POST['description']
        image = request.FILES['image']
        banner.title = title
        banner.description = description
        banner.images = image
        banner.save()
        messages.info (request,'Banner updated')
        return redirect(view_banner)
    return render(request, 'admin/edit_banner.html', locals())


@user_passes_test(lambda u: u.is_superuser)
@never_cache
def add_banner(request):
    banner = Banner.objects.all()
    if request.method == "POST":
        title = request.POST['title']
        description = request.POST['description']
        image = request.FILES['image']
        Banner.objects.create(title=title,  description=description,  images=image)
        messages.success(request, "Banner added")
    return render(request,'admin/add_banner.html', locals())



@user_passes_test(lambda u: u.is_superuser)
@never_cache
def delete_banner(request, pid):
    banner = Banner.objects.get(id=pid)
    banner.delete()   
    messages.info (request,'Banner deleted')
    return redirect(view_banner)


@user_passes_test(lambda u: u.is_superuser)
@never_cache
def view_coupons(request):
    coupons = Coupon.objects.all().order_by('valid_at')
    return render(request,'admin/view_coupons.html',{'coupons':coupons})


@user_passes_test(lambda u: u.is_superuser)
@never_cache
def edit_coupon(request, pid):
    coupon = Coupon.objects.get(id=pid)

    if request.method == "POST":
        form = CouponForm(request.POST, instance=coupon)
        if form.is_valid():
            form.save()
            messages.success(request, "Coupon Updated")
            return redirect('view_coupons')
    else:
        form = CouponForm(instance=coupon)

    return render(request, 'admin/edit_coupon.html', {'form': form, 'coupon': coupon})



@user_passes_test(lambda u: u.is_superuser)
@never_cache
def delete_coupon(request, pid):
    coupon = Coupon.objects.get(id=pid)
    coupon.delete()
    messages.success(request, "Coupon Deleted")
    return redirect('view_coupons')



@user_passes_test(lambda u: u.is_superuser)
@never_cache
def add_coupons(request):
    if request.method == 'POST':
        form = CouponForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('view_coupons')
    else:
        form = CouponForm()
    return render(request, 'admin/add_coupons.html', {'form': form})



@user_passes_test(lambda u: u.is_superuser)
@never_cache
def manage_order(request):
    orders=Order.objects.all().order_by('-status')
    return render(request, 'admin/manage_order.html', {'orders':orders})



@user_passes_test(lambda u: u.is_superuser)
@never_cache
def update_order(request, id):
    if request.method == 'POST':
        order = Order.objects.get(id=id)
        status = request.POST.get('status')
        if(status):
            order.status = status
            order.save()
            messages.success(request, "Status changed")
        if status  == "Delivered":
            try:
                payment = Payment.objects.get(payment_id = order.order_number, status = False)
                if payment.payment_method == 'Cash on Delivery':
                    payment.paid = True
                    payment.save()
            except:
                pass
    return redirect('manage_order')



@user_passes_test(lambda u: u.is_superuser)
@never_cache
def view_order(request,id):
    order = Order.objects.filter(id=id).first()
    orderitems = OrderProduct.objects.filter(order=order)
    try:
     userCoupon = UserCoupon.objects.get(order=order)
    except:
      userCoupon={"used":False}
    context={
        'order': order,
        'orderitems':orderitems,
        'userCoupon':userCoupon
    }
    return render(request, 'admin/view_order.html',context)


