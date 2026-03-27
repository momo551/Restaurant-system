from django.contrib import admin
from .models import Table, Reservation


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ['number', 'capacity', 'status', 'floor', 'is_active']
    list_filter = ['status', 'floor', 'is_active']
    search_fields = ['number', 'notes']


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ['customer_name', 'table', 'reservation_time', 'guests_count', 'is_confirmed']
    list_filter = ['is_confirmed', 'reservation_time']
    search_fields = ['customer_name', 'customer_phone']
