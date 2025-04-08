from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import auth
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .forms import CreateUserForm
from .models import Customer, UserOTP
from django.contrib.auth.models import User
from order_management.models import DeliveryDetails,Products
from admin_management.models import Banner
import re


import random
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from .forms import UpdateUserForm
from django.views.decorators.cache import never_cache



# Create your views here.


def dumy(request):
    return render(request,'dumy.html')



@never_cache
def home(request):
    banner = Banner.objects.all()
    products_latest = products_random = Products.objects.all().order_by('?')[:8]
    products_bestseller = products_random = Products.objects.all().order_by('?')[:8]

    return render(request,'index.html',locals())



def userregister(request):
    usr = None
    #Register Form
    if request.method=='POST':
        get_otp=request.POST.get('otp')
        # OTP Verification
        if get_otp:
            get_usr=request.POST.get('usr')
            usr=Customer.objects.get(username=get_usr)
            if int(get_otp)==UserOTP.objects.filter(user=usr).last().otp:
                usr.is_active=True
                usr.save()
                messages.success(request,f'Account is created for {usr.username}')
                return redirect(userlogin)
            else:
                messages.warning(request,f'You Entered a wrong OTP')
                return render(request,'userregister.html',{'otp':True,'usr':usr})
        form = CreateUserForm(request.POST)
        #Form Validation
        if form.is_valid():
            form.save()
            email=form.cleaned_data.get('email')
            username=form.cleaned_data.get('username')
            usr=Customer.objects.get(username=username)
            usr.email=email
            usr.username=username
            usr.is_active=False
            usr.save()
            usr_otp=random.randint(100000,999999)
            UserOTP.objects.create(user=usr,otp=usr_otp)
            mess=f'Hello\t{usr.username},\nYour OTP to verify your account for Shoeplaza is {usr_otp}\nThanks!'
            send_mail(
                    "welcome to ShoePlaza E-commerce-Verify your Email",
                    mess,
                    settings.EMAIL_HOST_USER,
                    [usr.email],
                    fail_silently=False
                )
            messages.info(request,f'OTP send to your email')

            return render(request,'userregister.html',{'otp':True,'usr':usr})
            
        else:
            errors = form.errors
            for field, errors in errors.items():
              for error in errors:
                messages.error(request, f" {error}")
                       
    #Resend OTP
    elif (request.method == "GET" and 'username' in request.GET):
        get_usr = request.GET['username']
        if (Customer.objects.filter(username = get_usr).exists() and not Customer.objects.get(username = get_usr).is_active):
            usr = Customer.objects.get(username=get_usr)
            id = usr.id
            
            otp_usr = UserOTP.objects.get(user_id=id)
            usr_otp=otp_usr.otp
            mess = f"Hello, {usr.username},\nYour OTP is {usr_otp}\nThanks!"
            
            send_mail(
        "Welcome to ShoePlaza E-commerce - Verify Your Email",
        mess,
        settings.EMAIL_HOST_USER,
        [usr.email],
        messages.success(request,f'OTP resend to  {usr.email}'),

         )
        return render(request,'userregister.html',{'otp':True,'usr':usr})
    else:
            errors = ''
    form=CreateUserForm()
    context = {'form': form, 'errors': errors}
    return render(request,'userregister.html',context)



@never_cache
def userlogin(request):
    if request.method == 'POST':
        form_username = request.POST['username']
        form_password = request.POST['password']
        user = auth.authenticate(username=form_username, password=form_password)
        if user is not None:
            auth.login(request, user)
            return redirect('homepage')
        else:
            messages.info(request, 'Invalid username or password')
    return render(request, 'userlogin.html')



def forgetpassword(request):
    if request.method=="POST":
        email=request.POST['email']
        if Customer.objects.filter(email=email).exists():
            user=Customer.objects.get(email__exact=email)
           #reset password email
            current_site = get_current_site(request)
            mail_subject = 'Reset your password'
            message = render_to_string('reset_password_email.html', {
                'user': user,
                'domain': current_site,
             
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                 # Generate a token for a user also
                'token':default_token_generator.make_token(user),
            })
            to_email = email
            send_email=EmailMessage(
                        mail_subject, message, to=[to_email]
            )
            send_email.send()

            messages.success(request,"Password reset email has been sent to your email")
            
            return redirect('userloginpage')
        else:
            messages.error(request,'Account does not exists')
            return redirect('userloginpage')
    return render(request,'forgetpassword.html')



def resetpassword_validate(request,uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Customer._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError,Customer.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid']=uid
        messages.success(request,"  Please reset your password")
        return redirect('resetpassword')
    else:
        messages.error(request,"This link has been expired")
        return redirect('userloginpage')

    
    
@never_cache   
def resetpassword(request):
    if request.method == "POST":
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Customer.objects.get(pk=uid)

            # Check if password is strong enough
            regex = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
            if not re.match(regex, password):
                messages.warning(request, "Password must contain at least 8 characters, including one uppercase letter, one lowercase letter, one number, and one special character")
                return redirect('resetpassword')

            user.set_password(password)
            user.save()
            messages.success(request,"Password reset successful")
            return redirect('userloginpage')
        else:
            messages.warning(request,"Password not match")
            return redirect('resetpassword')
    else:
        return render(request, 'resetPassword.html')



@login_required(login_url='userloginpage')
def logout(request):
     auth.logout(request)
     return redirect('homepage')



@login_required(login_url='userloginpage')
@never_cache
def userprofile(request):
    return render(request,'userprofile.html')



@login_required(login_url='userloginpage')
@never_cache
def updateprofile(request):
    user_id= request.user.id
    user = Customer.objects.get(pk=user_id)
    
    if request.method == 'POST':
        form = UpdateUserForm(request.POST, request.FILES, instance=user)
        
     
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('userprofile')
        else:
            messages.error(request, 'There was an error while updating your profile.')
    else:
        form = UpdateUserForm(instance=user)
        context = {'form': form}
    return render(request, 'updateprofile.html', context)



@login_required(login_url='userloginpage')
@never_cache
def changepassword(request):
    if request.method == 'POST':
        current_password = request.POST["current_password"]
        new_password = request.POST["new_password"]
        confirm_password = request.POST["confirm_password"]

        user = Customer.objects.get(username__exact=request.user.username)

        if new_password == confirm_password:
            success = user.check_password(current_password)

            if success:
                # Check if new password is strong enough
                regex = r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$"
                if not re.match(regex, new_password):
                    messages.warning(request, "New password must contain at least 8 characters, including one letter, one number, and one special character")
                    return redirect('changepassword')

                user.set_password(new_password)
                user.save()
                auth.logout(request)
                messages.success(request,"Password updated successfully")
                return redirect('userloginpage')

            messages.error(request,"Please enter valid current password")
            return redirect('changepassword')
        else:
            messages.error(request,"Password does not match")
            return redirect('changepassword')
    
    return render(request, "changepassword.html")



@login_required(login_url='userloginpage')
@never_cache
def viewAddresses(request):
    current_user = request.user
    addresses=DeliveryDetails.objects.filter(user_id=current_user.id)
    return render(request, 'viewaddresses.html',{'AllAddress': addresses})



@login_required(login_url='userloginpage')
@never_cache
def deleteAddress(request, address_id):
    address=DeliveryDetails.objects.get(id = address_id)
    address.delete()
    messages.success(request,"Address removed successfully")
    return redirect('viewAddresses')



@login_required(login_url='userloginpage')
@never_cache
def editAddress(request, address_id):
    if request.method == 'POST':
        address=DeliveryDetails.objects.get(id = address_id)
        address.first_name = request.POST['first_name']
        address.last_name = request.POST['last_name']
        address.phone = request.POST['phone']
        address.email = request.POST['email']
        address.order_address = request.POST['address']
        address.city = request.POST['city']
        address.state = request.POST['state']
        address.country = request.POST['country']
        address.zip_code = request.POST['zip_code']
        address.user = request.user
        try:
            address.save()
        except:
            messages.warning(request,f'There are some errors with the values you entered.')

        messages.success(request,"Address Edited successfully")
        return redirect('viewAddresses')
    else:
        address=DeliveryDetails.objects.get(id = address_id)
        return render(request,'editaddress.html', {"address": address})



@login_required(login_url='userloginpage')
@never_cache
def addNewAddress(request, form_from):
    if request.method == 'POST':
        form_from = request.POST['form_from']
        address=DeliveryDetails()
        address.first_name = request.POST['first_name']
        address.last_name = request.POST['last_name']
        address.phone = request.POST['phone']
        address.email = request.POST['email']
        address.order_address = request.POST['address']
        address.city = request.POST['city']
        address.state = request.POST['state']
        address.country = request.POST['country']
        address.zip_code = request.POST['zip_code']
        address.user = request.user
        try:
            address.save()
            if(form_from == "0"):
                messages.success(request,"Address added successfully")
                return redirect('viewAddresses')
            else:
                messages.success(request,"Address added successfully")
                return redirect('order_management:checkout')

        except:
            messages.warning(request,f'There are some errors with the values you entered.')
    else:
        return render(request,'addaddress.html',{ "form_from" : form_from})
