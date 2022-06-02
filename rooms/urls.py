from django.urls import path
from rooms.views import *

urlpatterns = [
    path('create/', RoomCreateAPI.as_view(), name='room_create'),
    # path('schoolcheck/', SchoolAuthAPI.as_view(), name='schoolcheck'),
    path('list/', RoomListAPI.as_view(), name='room_list'),
    path('filter/', RoomFilterAPI.as_view(), name='room_filter'),
    path('search/', RoomSearchAPI.as_view(), name='room_search'),
    path('detail/<int:pk>', RoomDetailAPI.as_view(), name='room_detail'),
    path('recommend/', RoomRecommendAPI.as_view(), name='room_recommend'),
    path('entrance/<int:pk>/', RoomEntranceAPI.as_view(), name='room_entrance'),
    path('exit/<int:pk>/', RoomExitAPI.as_view(), name='room_exit'),
    path('participation/', ParticipationListAPI.as_view(), name='participation'),
]
