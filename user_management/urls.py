from django.urls import path
from.import views
urlpatterns=[
    path('',views.home,name='homepage'),
    path('userloginpage',views.userlogin,name='userloginpage'),
    path('userregisterpage',views.userregister,name='userregisterpage'),
    path('logout', views.logout, name='logout'),
    path('forgetpassword',views.forgetpassword,name='forgetpassword'),
    path('resetpassword_validate/<uidb64>/<token>/', views.resetpassword_validate, name='resetpassword_validate'),
    path('resetpassword',views.resetpassword,name='resetpassword'),
    path('updateprofile/',views.updateprofile,name='updateprofile'),
    path('userprofile',views.userprofile,name='userprofile'),
    path('changepassword',views.changepassword,name='changepassword'),
    path('viewAddresses/',views.viewAddresses,name='viewAddresses'),
    path('deleteAddress/<int:address_id>/',views.deleteAddress ,name='deleteAddress'),
    path('editAddress/<int:address_id>/',views.editAddress ,name='editAddress'),
    path('addNewAddress/<int:form_from>/',views.addNewAddress,name='addNewAddress'),

    path('dumy/',views.dumy ,name='dumy'),








    

    
]