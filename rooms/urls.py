from django.urls import path
from rooms.views import *

urlpatterns = [
    path('room_create/', RoomCreateAPI.as_view(), name='room_create'),
    path('schoolcheck/', SchoolAuthAPI.as_view(), name='schoolcheck'),
    path('room_list/', RoomListAPI.as_view(), name='room_list'),
    path('room_filter/', RoomFilterAPI.as_view(), name='room_filter'),
    path('room_search/', RoomSearchAPI.as_view(), name='room_search'),
    path('room_detail/<int:pk>', RoomDetailAPI.as_view(), name='room_detail'),
    path('room_recommend/', RoomRecommendAPI.as_view(), name='room_recommend'),
    path('room_entrance/<int:pk>/', RoomEntranceAPI.as_view(), name='room_entrance'),
    path('room_exit/<int:pk>/', RoomExitAPI.as_view(), name='room_exit'),
    path('participation/', ParticipationListAPI.as_view(), name='participation'),
]