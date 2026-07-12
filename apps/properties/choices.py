class PropertyType:
    HOTEL = 'HOTEL'
    GUESTHOUSE = 'GUESTHOUSE'
    SHORT_STAY = 'SHORT_STAY'
    LONG_TERM = 'LONG_TERM'

    CHOICES = [
        (HOTEL, 'Hotel'),
        (GUESTHOUSE, 'Guesthouse / B&B'),
        (SHORT_STAY, 'Short-Stay Apartment'),
        (LONG_TERM, 'Long-Term Rental'),
    ]


class PropertyStatus:
    DRAFT = 'DRAFT'
    PENDING_VERIFICATION = 'PENDING_VERIFICATION'
    LIVE = 'LIVE'
    REJECTED = 'REJECTED'
    SUSPENDED = 'SUSPENDED'

    CHOICES = [
        (DRAFT, 'Draft'),
        (PENDING_VERIFICATION, 'Pending Verification'),
        (LIVE, 'Live on Platform'),
        (REJECTED, 'Rejected'),
        (SUSPENDED, 'Suspended'),
    ]


class RoomType:
    SINGLE = 'SINGLE'
    DOUBLE = 'DOUBLE'
    SUITE = 'SUITE'
    APARTMENT = 'APARTMENT'
    STUDIO = 'STUDIO'
    ENTIRE_HOUSE = 'ENTIRE_HOUSE'

    CHOICES = [
        (SINGLE, 'Single Room'),
        (DOUBLE, 'Double Room'),
        (SUITE, 'Suite'),
        (APARTMENT, 'Apartment'),
        (STUDIO, 'Studio'),
        (ENTIRE_HOUSE, 'Entire House/Villa'),
    ]


class BookingStatus:
    PENDING = 'PENDING'
    CONFIRMED = 'CONFIRMED'
    CHECKED_IN = 'CHECKED_IN'
    CHECKED_OUT = 'CHECKED_OUT'
    CANCELLED = 'CANCELLED'

    CHOICES = [
        (PENDING, 'Pending'),
        (CONFIRMED, 'Confirmed'),
        (CHECKED_IN, 'Checked In'),
        (CHECKED_OUT, 'Checked Out'),
        (CANCELLED, 'Cancelled'),
    ]


class GhanaRegion:
    GREATER_ACCRA = 'GREATER_ACCRA'
    ASHANTI = 'ASHANTI'
    CENTRAL = 'CENTRAL'
    EASTERN = 'EASTERN'
    WESTERN = 'WESTERN'
    VOLTA = 'VOLTA'
    NORTHERN = 'NORTHERN'
    UPPER_EAST = 'UPPER_EAST'
    UPPER_WEST = 'UPPER_WEST'
    BONO = 'BONO'
    BONO_EAST = 'BONO_EAST'
    AHAFO = 'AHAFO'
    SAVANNAH = 'SAVANNAH'
    NORTH_EAST = 'NORTH_EAST'
    OTI = 'OTI'
    WESTERN_NORTH = 'WESTERN_NORTH'

    CHOICES = [
        (GREATER_ACCRA, 'Greater Accra'),
        (ASHANTI, 'Ashanti'),
        (CENTRAL, 'Central'),
        (EASTERN, 'Eastern'),
        (WESTERN, 'Western'),
        (VOLTA, 'Volta'),
        (NORTHERN, 'Northern'),
        (UPPER_EAST, 'Upper East'),
        (UPPER_WEST, 'Upper West'),
        (BONO, 'Bono'),
        (BONO_EAST, 'Bono East'),
        (AHAFO, 'Ahafo'),
        (SAVANNAH, 'Savannah'),
        (NORTH_EAST, 'North East'),
        (OTI, 'Oti'),
        (WESTERN_NORTH, 'Western North'),
    ]


class Amenity:
    WIFI = 'wifi'
    AC = 'ac'
    PARKING = 'parking'
    TV = 'tv'
    KITCHEN = 'kitchen'
    POOL = 'pool'
    GYM = 'gym'
    RESTAURANT = 'restaurant'
    SECURITY = 'security'
    GENERATOR = 'generator'
    WATER_STORAGE = 'water_storage'

    CHOICES = [
        (WIFI, 'WiFi'),
        (AC, 'Air Conditioning'),
        (PARKING, 'Parking'),
        (TV, 'TV'),
        (KITCHEN, 'Kitchen'),
        (POOL, 'Swimming Pool'),
        (GYM, 'Gym'),
        (RESTAURANT, 'Restaurant'),
        (SECURITY, '24/7 Security'),
        (GENERATOR, 'Backup Generator'),
        (WATER_STORAGE, 'Water Storage'),
    ]