from rest_framework import serializers
from .models import Property, Room, PropertyImage, Booking


class PropertyImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyImage
        fields = ['id', 'image_url', 'caption', 'is_primary', 'order']


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = [
            'id', 'name', 'room_type', 'description',
            'max_guests', 'beds_single', 'beds_double',
            'price_per_night', 'monthly_price',
            'is_available', 'total_units', 'available_units',
            'has_ac', 'has_tv', 'has_private_bathroom', 'has_balcony'
        ]


class PropertyListSerializer(serializers.ModelSerializer):
    host_name = serializers.CharField(source='host.get_full_name', read_only=True)
    primary_image = serializers.SerializerMethodField()
    lowest_price = serializers.SerializerMethodField()

    class Meta:
        model = Property
        fields = [
            'id', 'name', 'property_type', 'region', 'city',
            'latitude', 'longitude', 'amenities',
            'rating_average', 'review_count',
            'primary_image', 'host_name', 'status',
            'max_guests', 'lowest_price'
        ]

    def get_primary_image(self, obj):
        img = obj.images.filter(is_primary=True).first()
        if img:
            return img.image_url
        first = obj.images.first()
        return first.image_url if first else None

    def get_lowest_price(self, obj):
        room = obj.rooms.first()
        if not room:
            return None
        if room.monthly_price:
            return str(room.monthly_price)
        return str(room.price_per_night)


class PropertyDetailSerializer(serializers.ModelSerializer):
    images = PropertyImageSerializer(many=True, read_only=True)
    rooms = RoomSerializer(many=True, read_only=True)
    host_name = serializers.CharField(source='host.get_full_name', read_only=True)
    host_phone = serializers.CharField(source='host.phone_number', read_only=True)

    class Meta:
        model = Property
        fields = [
            'id', 'host', 'host_name', 'host_phone',
            'name', 'description', 'property_type',
            'region', 'city', 'district', 'address',
            'latitude', 'longitude',
            'contact_phone', 'contact_email',
            'amenities', 'check_in_time', 'check_out_time',
            'total_rooms', 'total_beds', 'max_guests', 'bathrooms',
            'status', 'rating_average', 'review_count', 'booking_count',
            'images', 'rooms', 'created_at', 'updated_at'
        ]


class PropertyCreateSerializer(serializers.ModelSerializer):
    image_urls = serializers.ListField(child=serializers.URLField(), required=False, write_only=True)

    class Meta:
        model = Property
        fields = [
            'name', 'description', 'property_type',
            'region', 'city', 'district', 'address',
            'latitude', 'longitude',
            'contact_phone', 'contact_email',
            'amenities', 'check_in_time', 'check_out_time',
            'total_rooms', 'total_beds', 'max_guests', 'bathrooms',
            'image_urls',
        ]

    def create(self, validated_data):
        image_urls = validated_data.pop('image_urls', [])
        validated_data['host'] = self.context['request'].user
        property_obj = super().create(validated_data)

        for i, url in enumerate(image_urls):
            PropertyImage.objects.create(
                property=property_obj,
                image_url=url,
                is_primary=(i == 0),
                order=i,
            )

        return property_obj


class BookingSerializer(serializers.ModelSerializer):
    property_name = serializers.CharField(source='listing.name', read_only=True)
    room_name = serializers.CharField(source='room.name', read_only=True)
    guest_name = serializers.CharField(source='guest.get_full_name', read_only=True)
    guest_phone = serializers.CharField(source='guest.phone_number', read_only=True)
    property_type = serializers.CharField(source='listing.property_type', read_only=True)
    nights = serializers.IntegerField(source='get_nights', read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'listing', 'property_name', 'room', 'room_name',
            'guest', 'guest_name', 'guest_phone', 'property_type',
            'check_in', 'check_out', 'nights',
            'number_of_guests', 'units_booked',
            'price_per_night', 'total_price',
            'status', 'special_requests', 'created_at'
        ]
        read_only_fields = ['guest', 'price_per_night', 'total_price', 'status']