from django.urls import path
from.import views
urlpatterns=[
    path('admin_login',views.admin_login,name='admin_login'),
    path('',views.admindashboard,name='admindashboard'),
    path('manage_user',views.manage_user,name='manage_user'),
    path('delete_user/<int:pid>/', views.delete_user, name="delete_user"),
    path('<int:id>/blockuser/', views.blockuser, name='blockuser'),
    path('view_category',views.view_category,name='view_category'),
    path('edit_category/<int:pid>/',views.edit_category,name='edit_category'),
    path('delete_category/<int:pid>/',views.delete_category,name='delete_category'),
    path('add_category',views.add_category,name='add_category'),
    path('view_product',views.view_product,name='view_product'),
    path('add_product',views.add_product,name='add_product'),
    path('delete_product/<int:pid>/', views.delete_product, name="delete_product"),
    path('edit_product/<int:pid>/', views.edit_product, name="edit_product"),
    path('view_banner',views.view_banner,name='view_banner'),
    path('add_banner',views.add_banner,name='add_banner'),
    path('edit_banner/<int:pid>/',views.edit_banner,name='edit_banner'),
    path('delete_banner/<int:pid>/',views.delete_banner,name='delete_banner'),
    path('view_coupons',views.view_coupons,name='view_coupons'),
    path('delete_coupon/<int:pid>/',views.delete_coupon,name='delete_coupon'),
    path('edit_coupon/<int:pid>/',views.edit_coupon,name='edit_coupon'),
    path('add_coupons',views.add_coupons,name='add_coupons'),
    path('manage_order/', views.manage_order, name="manage_order"),
    path('view_order/<int:id>/',views.view_order, name='view_order'),
    path('update_order/<int:id>', views.update_order, name="update_order"),








]