from django.utils.timezone import localdate
from rest_framework import serializers
from .models import HotelRoom, RoomReservations


class HotelRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = HotelRoom
        fields = ['room_number', 'description', 'day_price']
        read_only_fields = ['room_number']

class HotelRoomCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = HotelRoom
        fields = ['room_number', 'description', 'day_price']

class RoomReservationsSerializer(serializers.ModelSerializer):
    room_number=serializers.CharField(source='room_number.room_number')
    class Meta:
        model = RoomReservations
        fields = ['id', 'room_number', 'date_start', 'date_end']
        read_only_fields = ['id']

    def validate(self, data):
        today = localdate()
        if data['date_end'] <= data['date_start']:
            raise serializers.ValidationError(
                "Дата окончания должна быть позже даты начала"
            )

        if data['date_start'] < today:
            raise serializers.ValidationError(
                "Нельзя бронировать на прошедшие даты"
            )

        return data
class RoomReservationsCreateSerializer(RoomReservationsSerializer):
    room_number = serializers.CharField()

    def validate(self, data):
        data = super().validate(data)

        room_number = data['room_number']
        date_start = data['date_start']
        date_end = data['date_end']

        overlapping_reservations = RoomReservations.objects.filter(
            room_number__room_number=room_number,
            date_start__lt=date_end,
            date_end__gt=date_start
        )

        if overlapping_reservations.exists():
            raise serializers.ValidationError(
                "Номер уже забронирован на указанные даты"
            )

        return data

class RoomReservationsUpdateSerializer(RoomReservationsSerializer):
    room_number=serializers.CharField(source='room_number.room_number',read_only=True)