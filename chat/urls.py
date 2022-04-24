from django.urls import path

from .views import *

# urlpatterns = [
#     path('', views.home, name='home'),
#     path('<str:room_name>/', views.room, name='room'),
# ]
urlpatterns = [
    path('', Index.as_view(), name='index'),
    path('<str:room_name>/', Room.as_view(), name='room'),
]