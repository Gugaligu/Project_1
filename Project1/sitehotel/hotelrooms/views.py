from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import HotelRoom, RoomReservations
from .serializers import (HotelRoomSerializer,
                          RoomReservationsSerializer,
                          RoomReservationsUpdateSerializer,
                          RoomReservationsCreateSerializer, HotelRoomCreateSerializer)
from django.shortcuts import get_object_or_404



class HotelRoomListCreateView(generics.ListCreateAPIView):
    """GET(List),POST HOTEL ROOMS"""
    queryset = HotelRoom.objects.all()
    serializer_class = HotelRoomCreateSerializer

    def get_queryset(self):
        queryset = HotelRoom.objects.all()

        sort = self.request.query_params.get('sort', None)
        order = self.request.query_params.get('order', 'asc')

        if sort == 'day_price':
            if order == 'desc':
                queryset = queryset.order_by('-day_price')
            else:
                queryset = queryset.order_by('day_price')
        elif sort == 'date_create':
            if order == 'desc':
                queryset = queryset.order_by('-date_create')
            else:
                queryset = queryset.order_by('date_create')
        return queryset

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)

        return Response(
            {"room_number": response.data["room_number"]},
            status=status.HTTP_201_CREATED,
        )


class HotelRoomDetailView(APIView):
    def get_object(self, room_number):
        return get_object_or_404(HotelRoom, room_number=room_number)

    def get(self, request, room_number):
        room = get_object_or_404(HotelRoom, room_number=room_number)
        serializer = HotelRoomSerializer(room)
        return Response(serializer.data)

    def put(self, request, room_number):
        room = self.get_object(room_number)
        serializer = HotelRoomSerializer(room, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, room_number):
        room = get_object_or_404(HotelRoom, room_number=room_number)
        room.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RoomReservationsListView(APIView):
    def get(self, request):
        queryset = RoomReservations.objects.all().order_by('date_start')
        room_number = request.query_params.get('room_number')

        if room_number:
            room = get_object_or_404(HotelRoom, room_number=room_number)
            queryset = queryset.filter(room_number=room)

        serializer = RoomReservationsSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = RoomReservationsCreateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        room_number = serializer.validated_data['room_number']
        room = get_object_or_404(HotelRoom, room_number=room_number)

        reservation = serializer.save(room_number=room)

        return Response(
            {'id': reservation.id},
            status=status.HTTP_201_CREATED
        )

class RoomReservationsDetailView(APIView):
    def get_object(self, pk):
        return get_object_or_404(RoomReservations, pk=pk)

    def get(self, request, pk):
        reservation = get_object_or_404(RoomReservations, pk=pk)
        serializer = RoomReservationsSerializer(reservation)
        return Response(serializer.data)

    def put(self, request, pk):
        reservation = self.get_object(pk)
        serializer = RoomReservationsUpdateSerializer(reservation, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        reservation = get_object_or_404(RoomReservations, pk=pk)
        reservation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

