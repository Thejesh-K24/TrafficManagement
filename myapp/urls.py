from django.contrib import admin
from django.urls import path, include
from . import views
from .views import delete_traffic_data
from .views import update_traffic_data
urlpatterns = [
    path('', views.home, name='index'),
    path('signup/', views.signup, name ='signup'),
    path('login/', views.login, name ='login'),
    path('traffic_update/', views.traffic_update, name ='traffic_update'),
    path('logout/', views.logout, name='logout'),  # Logout page
    path('delete/<int:data_id>/', delete_traffic_data, name='delete_traffic_data'),
    path('update/<int:data_id>/', update_traffic_data, name='update_traffic_data'),
      ]
    
