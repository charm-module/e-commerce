from django.db import models
from admin_management.models import Products
from user_management.models import Customer
from django.core.validators import MinValueValidator
from django.core.validators import MaxValueValidator


class Wishlist(models.Model):
    user = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username}'s wishlist item: {self.product.product_name}"
    
class Cart(models.Model):
    user = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    quantity=models.IntegerField(default=1)
    created_at=models.DateTimeField(auto_now_add=True)

    # def __str__(self):
    #     return f"{self.quantity} x {self.product}"
    # def __str__(self):
    #     return f"{self.user.username}'s cart item: {self.product.product_name}"
    def __str__(self):
        return f"{self.quantity} x {self.product}"
    
    def sub_total(self):
        return self.product.price * self.quantity
    


class DeliveryDetails(models.Model):
    user = models.ForeignKey(Customer, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    email = models.EmailField(max_length=50)
    order_address = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=10)

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def full_address(self):
        return f"{self.order_address},{self.city}, {self.state}, {self.country}, PIN: {self.zip_code}"
    
    def __str__(self):
        return self.user.username
    
    


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(500)])
    min_value = models.IntegerField(validators=[MinValueValidator(0)])
    valid_from = models.DateTimeField()
    valid_at = models.DateTimeField()
    active = models.BooleanField(default=False)

    def __str__(self):
     return self.code
    


class Payment(models.Model):
    customer = models.ForeignKey(Customer,on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=30)
    refund_id = models.CharField(max_length=30)
    order_id = models.CharField(max_length=100,blank=True,default='empty')
    payment_method = models.CharField(max_length=100)
    amount_paid = models.FloatField(default=0)
    paid = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.username} {self.payment_id}"

    
class Order(models.Model):
    STATUS = (
        ('Order Confirmed', 'Order Confirmed'),
        ('Shipped',"Shipped"),
        ('Out for delivery',"Out for delivery"),
        ('Delivered', 'Delivered'),
        ('Cancelled','Cancelled'),
        ('Returned','Returned'),
    )
    user = models.ForeignKey(Customer,on_delete=models.SET_NULL,null=True)
    order_number = models.CharField(max_length=50)
    address = models.ForeignKey(DeliveryDetails, on_delete=models.CASCADE)
    order_total = models.FloatField()
    order_discount = models.FloatField(default=0)
    paid_amount = models.FloatField()
    tax = models.FloatField()
    payment = models.ForeignKey(Payment,on_delete=models.SET_NULL,blank=True,null=True)
    status = models.CharField(max_length=50,choices=STATUS,default='Order Confirmed')
    ip = models.CharField(blank=True,max_length=20)
    is_ordered = models.BooleanField(default=False)
    is_returned = models.BooleanField(default=False)
    return_reason = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)    
    refund_completed = models.BooleanField(default=False)
    def __str__(self):
        return self.order_number


class UserCoupon(models.Model):
    user =  models.ForeignKey(Customer,on_delete=models.CASCADE, null= True)
    coupon = models.ForeignKey(Coupon,on_delete = models.CASCADE, null = True)
    order  = models.ForeignKey(Order,on_delete=models.SET_NULL,null = True,related_name='order_coupon')
    used = models.BooleanField(default = False)
    def __str__(self):
        return str(self.id)
  
     
class OrderProduct(models.Model):
    order = models.ForeignKey(Order,on_delete=models.CASCADE,related_name='user_order_page')
    customer = models.ForeignKey(Customer,on_delete=models.CASCADE)
    product = models.ForeignKey(Products,on_delete=models.CASCADE)
    quantity = models.IntegerField()
    product_price = models.FloatField()
    ordered = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    def __str__(self):
        return self.product.product_name
    def sub_total(self):
        return self.product.price * self.quantity