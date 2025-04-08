from django.urls import path
from.import views

app_name='further_management'

urlpatterns=[
       path('myorders/',views.myorders,name='myorders'),
       path('vieworder/<int:id>/',views.viewOrder, name='vieworder'),

]




