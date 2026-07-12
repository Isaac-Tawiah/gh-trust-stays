from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Property, Room, PropertyImage, Booking


class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1
    fields = ('image_url', 'caption', 'is_primary', 'order')


class RoomInline(admin.TabularInline):
    model = Room
    extra = 1
    fields = ('name', 'room_type', 'price_per_night', 'monthly_price', 'is_available', 'total_units')


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('name', 'host', 'property_type', 'city', 'region', 'status', 'created_at')
    list_filter = ('property_type', 'status', 'region')
    search_fields = ('name', 'city', 'host__first_name')
    inlines = [PropertyImageInline, RoomInline]


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'property', 'room_type', 'price_per_night', 'monthly_price', 'is_available')
    list_filter = ('room_type', 'is_available', 'has_ac')
    search_fields = ('name', 'property__name')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'guest', 'listing', 'room', 'check_in', 'check_out', 'status', 'total_price')
    list_filter = ('status', 'check_in')
    search_fields = ('guest__first_name', 'listing__name')