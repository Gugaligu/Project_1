from django.contrib import admin
from django.urls import path

from hotelrooms import views

urlpatterns = [
    # Room endpoints
    path('rooms/', views.HotelRoomListCreateView.as_view(),name='rooms'),
    path('rooms/<int:room_number>/', views.HotelRoomDetailView.as_view(), name='room-detail'),

    # reservation endpoints
    path('reservation/', views.RoomReservationsListView.as_view(), name='reservations'),
    path('reservation/<int:pk>/', views.RoomReservationsDetailView.as_view(), name='reservation-detail'),
]
