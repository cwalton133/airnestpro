from django.contrib import admin
from core.models import (
    Property,
    Booking,
    PropertyReview,
    PropertyCategory,
    Amenity,
    PropertyImages,
    Wishlist,
    Address,
    Realtor,
    Payment,
)
from .forms import PropertyAdminForm  
from tinymce.models import HTMLField
from tinymce.widgets import TinyMCE
from django import forms

class PropertyImagesAdmin(admin.TabularInline):
    model = PropertyImages
    extra = 1  

class PropertyAdmin(admin.ModelAdmin):
    form = PropertyAdminForm 
        
    
class PropertyCategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'category_image', 'cid')  
    search_fields = ('title',)  
    ordering = ('title',)  
    list_filter = ('title',)  
  

    def category_image(self, obj):
        return obj.category_image()
    category_image.short_description = 'Image'
    category_image.allow_tags = True 


class PropertyAdmin(admin.ModelAdmin):
    inlines = [PropertyImagesAdmin]
    list_display = ['title', 'image', 'realtor', 'price_per_night', 'location', 'available']
    list_editable = ['price_per_night', 'available']
    search_fields = ['title', 'realtor__username']
    list_filter = ['available', 'location', 'tags']
    form = PropertyAdminForm
    
    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj, change, **kwargs)
        return form

class BookingAdmin(admin.ModelAdmin):
    list_display = ['property', 'user', 'check_in_date', 'check_out_date', 'status']
    list_editable = ['status']
    search_fields = ['user__username', 'property__title']
    list_filter = ['status', 'check_in_date', 'check_out_date']

class PropertyReviewAdmin(admin.ModelAdmin):
    list_display = ['property', 'user', 'rating', 'date']
    search_fields = ['user__username', 'property__title']
    list_filter = ['rating', 'date']

# class UserProfileAdmin(admin.ModelAdmin):
#     list_display = ['user', 'bio', 'phone', 'location']
#     search_fields = ['user__username', 'bio']

class AmenityAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']

class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'property', 'date_added']  
    search_fields = ['user__username', 'property__title']  
    list_filter = ['user', 'date_added']

class AddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'address_line', 'city', 'state', 'zip_code']
    list_editable = ['address_line', 'city', 'state', 'zip_code']
    
class RealtorAdmin(admin.ModelAdmin):
    list_display = ('rid', 'user',)  
    search_fields = ('user__username',)  
    list_filter = ('user__is_active',)   
    ordering = ('rid',)  

    def __str__(self):
        return self.user.username
    
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'user', 'amount', 'payment_method', 'status', 'timestamp')
    list_filter = ('payment_method', 'status', 'timestamp')
    search_fields = ('transaction_id', 'user__username', 'booking__id')  
    ordering = ('-timestamp',)  

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('booking', 'user')  
        return queryset

    def __str__(self):
        return self.transaction_id



admin.site.register(Property, PropertyAdmin)
admin.site.register(Booking, BookingAdmin)
admin.site.register(PropertyReview, PropertyReviewAdmin)
admin.site.register(PropertyCategory, PropertyCategoryAdmin)
admin.site.register(Amenity, AmenityAdmin)
admin.site.register(Wishlist, WishlistAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(Realtor, RealtorAdmin)
admin.site.register(Payment, PaymentAdmin)

