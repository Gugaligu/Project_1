from django.test import TestCase
from django.utils.timezone import localdate, timedelta
from rest_framework.exceptions import ValidationError
from .models import HotelRoom, RoomReservations
from .serializers import (
    HotelRoomSerializer,
    HotelRoomCreateSerializer,
    RoomReservationsSerializer,
    RoomReservationsCreateSerializer,
    RoomReservationsUpdateSerializer
)

"""ЗАПУСК: python manage.py test --settings=sitehotel.settings_test"""

class HotelRoomSerializersTest(TestCase):
    def setUp(self):
        self.room_data = {
            'room_number': '101',
            'description': 'Luxury Suite',
            'day_price': 250
        }

    def test_create_serializer_valid_data(self):
        serializer = HotelRoomCreateSerializer(data=self.room_data)
        self.assertTrue(serializer.is_valid())
        room = serializer.save()
        self.assertEqual(room.room_number, '101')

    def test_serializer_output_format(self):
        room = HotelRoom.objects.create(**self.room_data)
        serializer = HotelRoomSerializer(room)
        self.assertEqual(serializer.data['room_number'], '101')
        self.assertEqual(serializer.data['description'], 'Luxury Suite')
        self.assertEqual(serializer.data['day_price'], '250')


class RoomReservationSerializersTest(TestCase):
    def setUp(self):
        self.room = HotelRoom.objects.create(
            room_number='101',
            description='Luxury Suite',
            day_price=250
        )
        self.today = localdate()
        self.valid_reservation_data = {
            'room_number': '101',
            'date_start': self.today + timedelta(days=1),
            'date_end': self.today + timedelta(days=3)
        }

    def test_create_serializer_valid_data(self):
        serializer = RoomReservationsCreateSerializer(data=self.valid_reservation_data)
        self.assertTrue(serializer.is_valid())
        reservation = serializer.save(room_number=self.room)
        self.assertEqual(reservation.room_number.room_number, '101')
        self.assertEqual(reservation.date_start, self.valid_reservation_data['date_start'])

    def test_serializer_output_format(self):
        reservation = RoomReservations.objects.create(
            room_number=self.room,
            date_start=self.today + timedelta(days=1),
            date_end=self.today + timedelta(days=3))

        serializer = RoomReservationsSerializer(reservation)
        self.assertEqual(serializer.data['room_number'], '101')
        self.assertEqual(serializer.data['date_start'], str(self.valid_reservation_data['date_start']))
        self.assertEqual(serializer.data['date_end'], str(self.valid_reservation_data['date_end']))

    def test_update_serializer(self):
        reservation = RoomReservations.objects.create(
            room_number=self.room,
            date_start=self.today + timedelta(days=1),
            date_end=self.today + timedelta(days=3))

        update_data = {
            'date_start': self.today + timedelta(days=2),
            'date_end': self.today + timedelta(days=4)
        }

        serializer = RoomReservationsUpdateSerializer(reservation, data=update_data)
        self.assertTrue(serializer.is_valid())
        updated_reservation = serializer.save()
        self.assertEqual(updated_reservation.date_start, update_data['date_start'])

class RoomReservationDateValidationTest(TestCase):
    def setUp(self):
        self.room = HotelRoom.objects.create(room_number=101, day_price=150.00)
        self.today = localdate()
        self.valid_data = {
            'room_number': '101',
            'date_start': self.today + timedelta(days=1),
            'date_end': self.today + timedelta(days=3)
        }

    def test_create_reservation_with_valid_dates(self):
        serializer = RoomReservationsCreateSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
        reservation = serializer.save(room_number=self.room)
        self.assertEqual(reservation.date_start, self.valid_data['date_start'])

    def test_same_day_reservation(self):
        data = self.valid_data.copy()
        data['date_end'] = data['date_start']
        serializer = RoomReservationsSerializer(data=data)
        with self.assertRaises(ValidationError) as context:
            serializer.is_valid(raise_exception=True)
        self.assertIn('Дата окончания должна быть позже даты начала', str(context.exception))

    def test_past_date_reservation(self):
        data = self.valid_data.copy()
        data['date_start'] = self.today - timedelta(days=2)
        data['date_end'] = self.today - timedelta(days=1)
        serializer = RoomReservationsSerializer(data=data)
        with self.assertRaises(ValidationError) as context:
            serializer.is_valid(raise_exception=True)
        self.assertIn('Нельзя бронировать на прошедшие даты', str(context.exception))

    def test_update_reservation_date_validation(self):
        reservation = RoomReservations.objects.create(
            room_number=self.room,
            date_start=self.today + timedelta(days=1),
            date_end=self.today + timedelta(days=3)
        )

        update_data = {
            'date_start': self.today + timedelta(days=4),
            'date_end': self.today + timedelta(days=2)
        }

        serializer = RoomReservationsUpdateSerializer(reservation, data=update_data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)


class ReservationConflictTest(TestCase):
    def setUp(self):
        self.room = HotelRoom.objects.create(room_number=101, day_price=200.00)
        self.existing_reservation = RoomReservations.objects.create(
            room_number=self.room,
            date_start=localdate() + timedelta(days=1),
            date_end=localdate() + timedelta(days=3)
        )

    def test_overlapping_reservation(self):
        new_data = {
            'room_number': '101',
            'date_start': localdate() + timedelta(days=2),
            'date_end': localdate() + timedelta(days=4)
        }

        serializer = RoomReservationsCreateSerializer(data=new_data)
        with self.assertRaises(ValidationError) as context:
            serializer.is_valid(raise_exception=True)
        self.assertIn('Номер уже забронирован на указанные даты', str(context.exception))

    def test_non_overlapping_reservation(self):
        new_data = {
            'room_number': '101',
            'date_start': localdate() + timedelta(days=4),
            'date_end': localdate() + timedelta(days=6)
        }

        serializer = RoomReservationsCreateSerializer(data=new_data)
        self.assertTrue(serializer.is_valid())

class HotelRoomSortingTest(TestCase):
    def setUp(self):
        HotelRoom.objects.create(room_number=101, day_price=150.00)
        HotelRoom.objects.create(room_number=102, day_price=100.00)
        HotelRoom.objects.create(room_number=103, day_price=200.00)

    def test_sort_by_price_asc(self):
        queryset = HotelRoom.objects.order_by('day_price')
        self.assertEqual(queryset[0].room_number, '102')
        self.assertEqual(queryset[1].room_number, '101')
        self.assertEqual(queryset[2].room_number, '103')

    def test_sort_by_price_desc(self):
        queryset = HotelRoom.objects.order_by('-day_price')
        self.assertEqual(queryset[0].room_number, '103')
        self.assertEqual(queryset[1].room_number, '101')
        self.assertEqual(queryset[2].room_number, '102')