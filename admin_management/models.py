from django.db import models

# Create your models here.

class Category(models.Model):
    category_name = models.CharField(max_length=100, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    description= models.TextField(max_length=255, blank=True)
    cat_image = models.ImageField(upload_to='photos/categories', blank=True)
  
    def __str__(self):
        return self.category_name

class Products(models.Model):
    product_name    = models.CharField(max_length=200, unique=True)
    description     = models.TextField(max_length=500, blank=True)
    price           = models.PositiveIntegerField()    
    images          = models.ImageField(upload_to ='photos/products')
    stock           = models.PositiveIntegerField()
    is_available    = models.BooleanField(default=True) 
    category        = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_date    = models.DateTimeField(auto_now_add=True)
    modified_date   = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.product_name
    
class Banner(models.Model):
      title   = models.CharField(max_length=200)
      description  = models.TextField(max_length=500)
      images   = models.FileField(upload_to ='photos/banner')

      def __str__(self):
         
         return self.title



