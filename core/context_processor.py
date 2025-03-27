from django.conf import settings
from django.contrib.auth.models import User
from core.models import Property, Wishlist, UserProfile, Booking

def user_profile(request):
    if request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            return {
                'user_profile': user_profile,
                'user_wishlist_count': Wishlist.objects.filter(user=request.user).count(),
                'user_bookings_count': Booking.objects.filter(user=request.user).count(),
            }
        except UserProfile.DoesNotExist:
            return {
                'user_profile': None,
                'user_wishlist_count': 0,
                'user_bookings_count': 0,
            }
    return {}

def property_list(request):
    properties = Property.objects.filter(available=True).order_by('-rating')[:5]  # Top rated available properties
    return {
        'top_properties': properties,
    }

def site_settings(request):
    return {
        'site_name': settings.SITE_NAME,
        'site_description': settings.SITE_DESCRIPTION,
    }

def amenities_list(request):
    amenities = Amenity.objects.all()
    return {
        'amenities': amenities,
    }

def booking_count(request):
    total_bookings = Booking.objects.count()
    return {
        'total_bookings': total_bookings,
    }