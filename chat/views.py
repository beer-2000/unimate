from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.views import View
from rest_framework import permissions
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.

class Index(View):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        return render(request, 'chatrooms/index.html')

class Room(View):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, room_name):
        return render(request, 'chatrooms/room.html', {'room_name': room_name})
