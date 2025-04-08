from django.urls import path
from.import views

app_name='product_management'
urlpatterns=[
    path('productlist/<int:pid>/',views.productlists,name='productlist'),
    path('singleproductview/<int:id>/',views.singleproductview,name='singleproductview'),
    path('search',views.search,name='search')

]