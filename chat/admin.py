from django.contrib import admin
from .models import *
from rooms.models import Room

# Register your models here.

admin.site.register(Chat)
admin.site.register(Room)