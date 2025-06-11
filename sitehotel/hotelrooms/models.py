from django.core.validators import MinValueValidator
from django.db import models

class HotelRoom(models.Model):
    room_number = models.CharField(max_length=10,unique=True)
    description = models.CharField(max_length=255)
    day_price = models.DecimalField(max_digits=6,decimal_places=0,validators=[MinValueValidator(0)])
    date_create = models.DateField(auto_now_add=True)

class RoomReservations(models.Model):
    room_number=models.ForeignKey(
        HotelRoom,
        db_column='room_number',
        on_delete=models.CASCADE,
        related_name='reservations')
    date_start = models.DateField()
    date_end = models.DateField()
    class Meta:
        ordering = ['date_start']