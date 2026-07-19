import uuid
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from .choices import (
    PropertyType, PropertyStatus, RoomType,
    BookingStatus, GhanaRegion
)


class Property(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    host = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='properties'
    )
    name = models.CharField(max_length=200)
    description = models.TextField()
    property_type = models.CharField(max_length=20, choices=PropertyType.CHOICES, db_index=True)
    region = models.CharField(max_length=20, choices=GhanaRegion.CHOICES, db_index=True)
    city = models.CharField(max_length=100, db_index=True)
    district = models.CharField(max_length=100, blank=True)
    address = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    contact_phone = models.CharField(max_length=20)
    contact_email = models.EmailField(blank=True)
    amenities = models.JSONField(default=list)
    check_in_time = models.TimeField(default='14:00')
    check_out_time = models.TimeField(default='11:00')
    total_rooms = models.PositiveIntegerField(default=1)
    total_beds = models.PositiveIntegerField(default=1)
    max_guests = models.PositiveIntegerField(default=2)
    bathrooms = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=25, choices=PropertyStatus.CHOICES, default=PropertyStatus.DRAFT, db_index=True)
    rejection_reason = models.TextField(blank=True)
    rating_average = models.FloatField(default=0.0)
    review_count = models.PositiveIntegerField(default=0)
    booking_count = models.PositiveIntegerField(default=0)
    view_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Property'
        verbose_name_plural = 'Properties'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.city}"

    @property
    def starting_price(self):
        """Returns the lowest room price for this property"""
        cheapest = self.rooms.first()
        if not cheapest:
            return None
        if cheapest.monthly_price:
            return cheapest.monthly_price
        return cheapest.price_per_night


class Room(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='rooms')
    name = models.CharField(max_length=200)
    room_type = models.CharField(max_length=20, choices=RoomType.CHOICES)
    description = models.TextField(blank=True)
    max_guests = models.PositiveIntegerField(default=2)
    beds_single = models.PositiveIntegerField(default=0)
    beds_double = models.PositiveIntegerField(default=1)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    monthly_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)])
    is_available = models.BooleanField(default=True)
    total_units = models.PositiveIntegerField(default=1)
    available_units = models.PositiveIntegerField(default=1,
    help_text="Number of rooms currently available for booking")
    has_ac = models.BooleanField(default=False)
    has_tv = models.BooleanField(default=False)
    has_private_bathroom = models.BooleanField(default=True)
    has_balcony = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Room'
        verbose_name_plural = 'Rooms'
        ordering = ['property', 'price_per_night']

    def __str__(self):
        return f"{self.name} at {self.property.name}"


class PropertyImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image_url = models.URLField(max_length=500)
    caption = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Property Image'
        verbose_name_plural = 'Property Images'
        ordering = ['-is_primary', 'order']

    def __str__(self):
        return f"Image for {self.property.name}"


class Booking(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    guest = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings_as_guest')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='bookings')
    listing = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='bookings')
    check_in = models.DateField()
    check_out = models.DateField()
    number_of_guests = models.PositiveIntegerField(default=1)
    units_booked = models.PositiveIntegerField(default=1)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=BookingStatus.CHOICES, default=BookingStatus.PENDING, db_index=True)
    special_requests = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Booking'
        verbose_name_plural = 'Bookings'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.guest.get_full_name()} - {self.room.name} ({self.check_in} to {self.check_out})"

    def get_nights(self):
        return (self.check_out - self.check_in).days