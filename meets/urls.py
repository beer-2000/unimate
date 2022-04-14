from django.urls import path
from meets.views import *

urlpatterns = [
    path('meet_create/', MeetCreateAPI.as_view(), name='meet_create'),
    path('meet_detail/<int:pk>/', MeetDetailAPI.as_view(), name='meet_detail'),
    path('meet_entrance/<int:pk>/', MeetEntranceAPI.as_view(), name='meet_entrance'),
    path('meet_exit/<int:pk>/', MeetExitAPI.as_view(), name='meet_exit'),
    path('meet_list/<int:id>/', MeetListAPI.as_view(), name='meet_list'),
]