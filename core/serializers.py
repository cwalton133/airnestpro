from rest_framework import serializers
from .models import (
    PropertyCategory,
    Realtor,
    Property,
    Booking,
    PropertyReview,
    Wishlist,
    Address,
    Amenity,
    PropertyImages,
    Payment,  
)


class PropertyCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyCategory
        fields = '__all__'
        read_only_fields = ['cid']


class RealtorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Realtor
        fields = '__all__'
        read_only_fields = ['rid', 'user']


class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = '__all__'
        read_only_fields = ['pid', 'realtor', 'price_per_night', 'date_added', 'updated']



class BookingSerializer(serializers.ModelSerializer):
    payment = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ['user', 'check_in_date', 'check_out_date', 'total+price']

    def get_payment(self, obj):
        payment = Payment.objects.filter(booking=obj).first()
        if payment:
            return PaymentSerializer(payment).data
        return None  

class PropertyReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyReview
        fields = '__all__'
        read_only_fields = ['user', 'comment', 'date']


class WishlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wishlist
        fields = '__all__'
        read_only_fields = ['user']


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'
        read_only_fields = ['user']


class AmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenity
        fields = '__all__'


class PropertyImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyImages
        fields = '__all__'

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"
        read_only_fields = ['amount', 'transaction_id', 'timestamp']