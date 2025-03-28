from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import UserData,TrafficData

admin.site.register(UserData)
admin.site.register(TrafficData)
