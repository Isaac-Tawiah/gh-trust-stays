from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta
from django.utils import timezone

from .models import Property, Room, Booking, PropertyImage
from .choices import PropertyStatus, BookingStatus
from .serializers import (
    PropertyListSerializer,
    PropertyDetailSerializer,
    PropertyCreateSerializer,
    BookingSerializer,
)


# ──────────────────────────────────────
# PUBLIC
# ──────────────────────────────────────

@api_view(['GET'])
@permission_classes([AllowAny])
def property_list(request):
    queryset = Property.objects.filter(status=PropertyStatus.LIVE)

    prop_type = request.query_params.get('property_type')
    if prop_type:
        queryset = queryset.filter(property_type=prop_type.upper())

    region = request.query_params.get('region')
    if region:
        queryset = queryset.filter(region=region.upper())

    city = request.query_params.get('city')
    if city:
        queryset = queryset.filter(city__icontains=city)

    amenities = request.query_params.get('amenities')
    if amenities:
        for a in amenities.split(','):
            queryset = queryset.filter(amenities__contains=[a.strip().lower()])

    search = request.query_params.get('search')
    if search:
        from django.db.models import Q
        queryset = queryset.filter(
            Q(name__icontains=search) | Q(description__icontains=search)
        )

    serializer = PropertyListSerializer(queryset, many=True)
    return Response({'count': queryset.count(), 'results': serializer.data})


@api_view(['GET'])
@permission_classes([AllowAny])
def property_detail(request, property_id):
    prop = get_object_or_404(Property, id=property_id, status=PropertyStatus.LIVE)
    prop.view_count += 1
    prop.save(update_fields=['view_count'])
    serializer = PropertyDetailSerializer(prop)
    return Response(serializer.data)


# ──────────────────────────────────────
# HOST
# ──────────────────────────────────────

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_property(request):
    if not request.user.is_host:
        return Response({'error': 'Only hosts can create listings.'}, status=status.HTTP_403_FORBIDDEN)

    price = request.data.get('price_per_night') or request.data.get('monthly_price')
    room_name = request.data.get('room_name', 'Standard Room')

    serializer = PropertyCreateSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        prop = serializer.save()

        room_type = 'ENTIRE_HOUSE' if prop.property_type == 'LONG_TERM' else 'SINGLE'
        total_rooms = prop.total_rooms

        if price:
            Room.objects.create(
                property=prop,
                name=room_name,
                room_type=room_type,
                price_per_night=float(price) if prop.property_type != 'LONG_TERM' else 0,
                monthly_price=float(price) if prop.property_type == 'LONG_TERM' else None,
                max_guests=prop.max_guests,
                beds_single=0,
                beds_double=1,
                total_units=total_rooms,
                available_units=total_rooms,
            )

        return Response({
            'message': 'Property created.',
            'property_id': str(prop.id),
            'status': prop.status
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def host_properties(request):
    if not request.user.is_host:
        return Response({'error': 'Only hosts can view their listings.'}, status=status.HTTP_403_FORBIDDEN)

    props = Property.objects.filter(host=request.user)
    serializer = PropertyListSerializer(props, many=True)
    return Response({'count': props.count(), 'results': serializer.data})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_for_verification(request, property_id):
    if not request.user.is_host:
        return Response({'error': 'Only hosts can submit listings.'}, status=status.HTTP_403_FORBIDDEN)

    prop = get_object_or_404(Property, id=property_id, host=request.user, status=PropertyStatus.DRAFT)
    prop.status = PropertyStatus.LIVE
    prop.save(update_fields=['status'])
    return Response({'message': 'Property is now live!', 'status': prop.status})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_property(request, property_id):
    if not request.user.is_host:
        return Response({'error': 'Only hosts can delete listings.'}, status=status.HTTP_403_FORBIDDEN)

    prop = get_object_or_404(Property, id=property_id, host=request.user)
    prop.delete()
    return Response({'message': 'Property deleted.'})


# ──────────────────────────────────────
# BOOKINGS
# ──────────────────────────────────────

def _calculate_months(start_date, end_date):
    """Calculate the number of calendar months between two dates."""
    months = 0
    current = start_date.replace(day=1)
    end = end_date.replace(day=1)
    while current < end:
        months += 1
        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1)
        else:
            current = current.replace(month=current.month + 1)
    return max(months, 1)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_booking(request):
    room_id = request.data.get('room_id')
    check_in = request.data.get('check_in')
    check_out = request.data.get('check_out')
    units_requested = int(request.data.get('units', 1))

    if not all([room_id, check_in, check_out]):
        return Response({'error': 'room_id, check_in, and check_out are required.'}, status=status.HTTP_400_BAD_REQUEST)

    room = get_object_or_404(Room, id=room_id, is_available=True)
    prop = room.property

    if prop.status != PropertyStatus.LIVE:
        return Response({'error': 'Property is not accepting bookings.'}, status=status.HTTP_400_BAD_REQUEST)

    # Check inventory
    if units_requested > room.available_units:
        return Response({
            'error': f'Only {room.available_units} unit(s) available.'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date()
        check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date()
    except ValueError:
        return Response({'error': 'Dates must be in YYYY-MM-DD format.'}, status=status.HTTP_400_BAD_REQUEST)

    nights = (check_out_date - check_in_date).days
    if nights < 1:
        return Response({'error': 'Check-out must be after check-in.'}, status=status.HTTP_400_BAD_REQUEST)

    # Calculate total price based on property type
    if room.monthly_price and room.monthly_price > 0:
        months = _calculate_months(check_in_date, check_out_date)
        total = room.monthly_price * months * units_requested
        price_per_night_at_booking = room.monthly_price
    else:
        total = room.price_per_night * nights * units_requested
        price_per_night_at_booking = room.price_per_night

    booking = Booking.objects.create(
        guest=request.user,
        room=room,
        listing=prop,
        check_in=check_in_date,
        check_out=check_out_date,
        number_of_guests=request.data.get('number_of_guests', 1),
        price_per_night=price_per_night_at_booking,
        total_price=total,
        special_requests=request.data.get('special_requests', '')
    )

    # Decrease available units
    room.available_units -= units_requested
    if room.available_units <= 0:
        room.available_units = 0
        room.is_available = False
    room.save(update_fields=['available_units', 'is_available'])

    # Update property booking count
    prop.booking_count += 1
    prop.save(update_fields=['booking_count'])

    serializer = BookingSerializer(booking)
    return Response({
        'message': 'Booking created.',
        'booking': serializer.data
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_bookings(request):
    bookings = Booking.objects.filter(guest=request.user)
    serializer = BookingSerializer(bookings, many=True)
    return Response({'count': bookings.count(), 'results': serializer.data})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    if request.user != booking.guest and request.user != booking.listing.host:
        return Response({'error': 'Not authorized.'}, status=status.HTTP_403_FORBIDDEN)

    if booking.status not in [BookingStatus.PENDING, BookingStatus.CONFIRMED]:
        return Response({'error': 'Only pending or confirmed bookings can be cancelled.'}, status=status.HTTP_400_BAD_REQUEST)

    booking.status = BookingStatus.CANCELLED
    booking.save()

    # Restore available units
    room = booking.room
    room.available_units += 1
    room.is_available = True
    room.save(update_fields=['available_units', 'is_available'])

    return Response({'message': 'Booking cancelled.'})


# ──────────────────────────────────────
# HOST BOOKINGS
# ──────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def host_bookings(request):
    if not request.user.is_host:
        return Response({'error': 'Only hosts can view guest bookings.'}, status=status.HTTP_403_FORBIDDEN)

    bookings = Booking.objects.filter(listing__host=request.user)
    serializer = BookingSerializer(bookings, many=True)
    return Response({'count': bookings.count(), 'results': serializer.data})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def approve_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    if request.user != booking.listing.host:
        return Response({'error': 'Only the property host can approve bookings.'}, status=status.HTTP_403_FORBIDDEN)

    if booking.status != BookingStatus.PENDING:
        return Response({'error': 'Only pending bookings can be approved.'}, status=status.HTTP_400_BAD_REQUEST)

    booking.status = BookingStatus.CONFIRMED
    booking.save()

    return Response({'message': 'Booking confirmed.'})