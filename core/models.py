from django.db import models
from django.contrib.auth.models import AbstractUser
from shortuuid.django_fields import ShortUUIDField
from django.utils.html import mark_safe
from taggit.managers import TaggableManager
from django.conf import settings
from django.utils import timezone
from tinymce.models import HTMLField


# Payment method choices
PAYMENT_METHOD_CHOICES = [
    ("paypal", "PayPal"),
    ("credit_card", "Credit Card"),
    ("paystack", "Paystack"),
]

# Payment status choices
PAYMENT_STATUS_CHOICES = [
    ("pending", "Pending"),
    ("completed", "Completed"),
    ("failed", "Failed"),
]


class PropertyCategory(models.Model):
    cid = ShortUUIDField(unique=True, length=10, max_length=20, prefix="cat", alphabet="abcdefgh12345")
    title = models.CharField(max_length=100, default="Apartment")
    image = models.ImageField(upload_to="property_categories", default="category.jpg")

    class Meta:
        verbose_name_plural = "Property Categories"

    def category_image(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))

    def __str__(self):
        return self.title


class Realtor(models.Model):
    rid = ShortUUIDField(unique=True, length=10, max_length=20, prefix="rel", alphabet="abcdefgh12345")
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Realtors"

    def __str__(self):
        return self.user.username


class Property(models.Model):
    pid = ShortUUIDField(unique=True, length=10, max_length=20, prefix="prop", alphabet="abcdefgh12345")
    realtor = models.ForeignKey(Realtor, on_delete=models.SET_NULL, null=True, related_name="properties")
    category = models.ForeignKey(PropertyCategory, on_delete=models.SET_NULL, null=True, related_name="properties")

    title = models.CharField(max_length=100, default="Cozy Home")
    image = models.ImageField(upload_to="properties", default="property.jpg")
    description = HTMLField()

    price_per_night = models.DecimalField(max_digits=12, decimal_places=2, default="0.00")
    max_guests = models.IntegerField(default=1)
    num_bedrooms = models.IntegerField(default=1)
    num_bathrooms = models.IntegerField(default=1)
    location = models.CharField(max_length=255, default="123 Main St")

    available = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    tags = TaggableManager(blank=True)

    date_added = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "Properties"

    def __str__(self):
        return self.title


class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    check_in_date = models.DateTimeField()
    check_out_date = models.DateTimeField()
    guests = models.IntegerField(default=1)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default="0.00")

    date_created = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[("pending", "Pending"), ("confirmed", "Confirmed"), ("canceled", "Canceled")],
        default="pending",
    )

    class Meta:
        verbose_name_plural = "Bookings"

    def __str__(self):
        return f"Booking {self.id} for {self.property.title}"


class Payment(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name="payment")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default="paypal")
    transaction_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default="pending")
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Payments"

    def __str__(self):
        return f"Payment {self.transaction_id} - {self.get_status_display()}"


class PropertyReview(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    property = models.ForeignKey(Property, on_delete=models.SET_NULL, null=True, related_name="reviews")
    comment = models.TextField()
    rating = models.IntegerField(choices=[(i, f"{i} star") for i in range(1, 6)], default=None)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Property Reviews"

    def __str__(self):
        return f"{self.user.username} - {self.property.title}"


class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    property = models.ForeignKey(Property, on_delete=models.SET_NULL, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Wishlists"

    def __str__(self):
        return f"{self.user.username}'s Wishlist - {self.property.title}"


class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    address_line = models.CharField(max_length=300, null=True)
    city = models.CharField(max_length=100, null=True)
    state = models.CharField(max_length=100, null=True)
    country = models.CharField(max_length=100, null=True)
    zip_code = models.CharField(max_length=20, null=True)

    class Meta:
        verbose_name_plural = "Addresses"

    def __str__(self):
        return f"{self.user.username}'s Address"


class Amenity(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class PropertyImages(models.Model):
    images = models.ImageField(upload_to="property-images", default="product.jpg")
    property = models.ForeignKey("Property", related_name="property_images", on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Property Images"

    def __str__(self):
        return f"Image for {self.property}"
