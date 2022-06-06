from django.urls import path
from meets.views import *

urlpatterns = [
    path('create/', MeetCreateAPI.as_view(), name='meet_create'),
    path('detail/<int:pk>/', MeetDetailAPI.as_view(), name='meet_detail'),
    path('entrance/<int:pk>/', MeetEntranceAPI.as_view(), name='meet_entrance'),
    path('exit/<int:pk>/', MeetExitAPI.as_view(), name='meet_exit'),
    path('list/<int:id>/', MeetListAPI.as_view(), name='meet_list'),
]
