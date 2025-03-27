import json
from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from rest_framework.views import APIView 
from django.contrib.auth.decorators import login_required
from django_filters.rest_framework import  DjangoFilterBackend
from django.db.models import Count, Avg
import requests
import stripe
from userauths.models import User
from core.models import Property, Booking, PropertyReview, Wishlist, Address, Payment
from core.forms import PropertyReviewForm
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
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
from .serializers import (
    PropertyCategorySerializer,
    RealtorSerializer,
    PropertySerializer,
    BookingSerializer,
    PropertyReviewSerializer,
    WishlistSerializer,
    AddressSerializer,
    AmenitySerializer,
    PropertyImagesSerializer,
    PaymentSerializer,
)
from django.template.loader import get_template, TemplateDoesNotExist
from .serializers import PaymentSerializer
from .payments.paypal import initiate_paypal_payment
from .payments.paystack import initiate_paystack_payment
from .payments.credit_card import initiate_stripe_payment
from paystackapi.transaction import Transaction 
from django.middleware.csrf import get_token
import hmac
import hashlib


def property_list_view(request):
    try:
        template = get_template('core/property-list.html')  
        return render(request, 'core/property-list.html')  
    except TemplateDoesNotExist:
        return HttpResponse("Template does not exist.")


def index(request):
    properties = Property.objects.filter(available=True, featured=True).order_by("-date_added")
    context = {
        "properties": properties
    }
    return render(request, 'core/index.html', context)


def property_list_view(request):
    properties = Property.objects.filter(available=True).order_by("-date_added")
    context = {
        "properties": properties,
    }
    return render(request, 'core/property-list.html', context)


def property_detail_view(request, pid):
    property = get_object_or_404(Property, pid=pid)
    reviews = PropertyReview.objects.filter(property=property).order_by("-date")
    average_rating = PropertyReview.objects.filter(property=property).aggregate(rating=Avg('rating'))

    review_form = PropertyReviewForm()

    make_review = True
    if request.user.is_authenticated:
        user_review_count = PropertyReview.objects.filter(user=request.user, property=property).count()
        if user_review_count > 0:
            make_review = False

    context = {
        "property": property,
        "make_review": make_review,
        "review_form": review_form,
        "average_rating": average_rating,
        "reviews": reviews,
    }
    return render(request, "core/property-detail.html", context)


@login_required
def book_property(request, pid):
    if request.method == "POST":
        property = get_object_or_404(Property, pid=pid)
        check_in_date = request.POST.get("check_in")
        check_out_date = request.POST.get("check_out")
        guests = request.POST.get("guests")

        booking = Booking.objects.create(
            user=request.user,
            property=property,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            guests=guests,
        )

        messages.success(request, "Booking successful!")
        return redirect('core:booking_detail', booking.id)
    return render(request, "core/book_property.html", {"property_id": pid})


@login_required
def booking_detail(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    return render(request, "core/booking_detail.html", {"booking": booking})


@login_required
def add_property_review(request, pid):
    if request.method == "POST":
        property = get_object_or_404(Property, pid=pid)
        review_form = PropertyReviewForm(request.POST)
        if review_form.is_valid():
            PropertyReview.objects.create(
                user=request.user,
                property=property,
                review=review_form.cleaned_data['review'],
                rating=review_form.cleaned_data['rating'],
            )
            messages.success(request, "Review added successfully!")
        else:
            messages.error(request, "There was an error adding your review.")
        return redirect("core:property_detail", pid=pid)


@login_required
def wishlist_view(request):
    wishlist = Wishlist.objects.filter(user=request.user)
    context = {
        "wishlist": wishlist,
    }
    return render(request, "core/wishlist.html", context)

@login_required
def add_to_wishlist(request):
    pid = request.GET['id']
    property = get_object_or_404(Property, pid=pid)
    Wishlist.objects.get_or_create(user=request.user, property=property)
    return JsonResponse({"success": True})

@login_required
def remove_from_wishlist(request):
    pid = request.GET['id']
    wishlist_item = Wishlist.objects.filter(user=request.user, property__pid=pid).first()
    if wishlist_item:
        wishlist_item.delete()
    return JsonResponse({"success": True})


@login_required
def user_dashboard(request):
    bookings = Booking.objects.filter(user=request.user).order_by("-check_in_date")
    context = {
        "bookings": bookings,
    }
    return render(request, 'core/dashboard.html', context)


@login_required
def make_address_default(request):
    id = request.GET['id']
    Address.objects.update(status=False)
    Address.objects.filter(id=id).update(status=True)
    return JsonResponse({"boolean": True})


def search_view(request):
    query = request.GET.get("q", "")
    properties = Property.objects.filter(title__icontains=query, available=True).order_by("-date_added")
    context = {
        "properties": properties,
        "query": query,
    }
    return render(request, "core/search.html", context)



# My Other Pages
def contact(request):
    return render(request, "core/contact.html")


def about_us(request):
    return render(request, "core/about_us.html")


def privacy_policy(request):
    return render(request, "core/privacy_policy.html")


def terms_of_service(request):
    return render(request, "core/terms_of_service.html")


#==========My ViesSet for Serializers==================


class PropertyCategoryViewSet(viewsets.ModelViewSet):
    queryset = PropertyCategory.objects.all()
    serializer_class = PropertyCategorySerializer
    #permission_classes = [IsAuthenticated] 
    permission_classes = []


    def get_serializer_context(self):
        return {'request': self.request}

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.properties.exists():
            return Response({'error': 'Cannot delete this category because it is associated with properties.'}, status=status.HTTP_400_BAD_REQUEST)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RealtorViewSet(viewsets.ModelViewSet):
    queryset = Realtor.objects.all()
    serializer_class = RealtorSerializer
    permission_classes = [IsAuthenticated]  

    def get_serializer_context(self):
        return {'request': self.request}

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.properties.exists():
            return Response({'error': 'Cannot delete this realtor because they are associated with properties.'}, status=status.HTTP_400_BAD_REQUEST)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    #permission_classes = [AllowAny]  
    #permission_classes = [IsAuthenticated]  


    def get_queryset(self):
        queryset = Property.objects.all()
        location = self.request.query_params.get("location")
        min_price = self.request.query_params.get("minPrice")
        max_price = self.request.query_params.get("maxPrice")
        bedrooms = self.request.query_params.get("bedrooms")
        amenities = self.request.query_params.get("amenities")

        if location:
            queryset = queryset.filter(location__icontains=location)
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        if bedrooms:
            queryset = queryset.filter(bedrooms=bedrooms)
        if amenities:
            queryset = queryset.filter(amenities__name__in=amenities.split(","))

        return queryset


    
class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]  

    def get_serializer_context(self):
        return {'request': self.request}

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PropertyReviewViewSet(viewsets.ModelViewSet):
    queryset = PropertyReview.objects.all()
    serializer_class = PropertyReviewSerializer
    permission_classes = [IsAuthenticated] 

    def get_serializer_context(self):
        return {'request': self.request}


class WishlistViewSet(viewsets.ModelViewSet):
    queryset = Wishlist.objects.all()
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated] 

    def get_serializer_context(self):
        return {'request': self.request}


class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated] 

    def get_serializer_context(self):
        return {'request': self.request}

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AmenityViewSet(viewsets.ModelViewSet):
    queryset = Amenity.objects.all()
    serializer_class = AmenitySerializer
    permission_classes = [IsAuthenticated] 

    def get_serializer_context(self):
        return {'request': self.request}


class PropertyImageViewSet(viewsets.ModelViewSet):
    queryset = PropertyImages.objects.all()
    serializer_class = PropertyImagesSerializer
    #permission_classes = [IsAuthenticated] 

    # def get_serializer_context(self):
    #     return {'request': self.request}

    # def destroy(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     instance.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)
    
    def get_queryset(self):
        property_id = self.request.query_params.get("property")
        if property_id:
            return PropertyImages.objects.filter(property_id=property_id)
        return PropertyImages.objects.all()
    
    #===============Payment Method Initiate==============
class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['booking']
    permission_classes = [AllowAny]
    
def get_csrf_token(request):
    return JsonResponse({"csrfToken": get_token(request)})

@login_required
def initiate_payment(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    payment_method = request.POST.get("payment_method")
    amount = booking.property.price
    
    if payment_method == "paypal":
        return initiate_paypal_payment(request, booking, amount)
    elif payment_method == "paystack":
        return initiate_paystack_payment(request.user.email, amount)
    elif payment_method == "credit_card":
        return initiate_stripe_payment(request, amount)
    else:
        return JsonResponse({"error": "Invalid payment method selected."}, status=400)  
    

class PaystackPayment(View):
    def post(self, request):
        amount = request.POST.get("amount")  
        email = request.POST.get("email")
        response = Transaction.initialize(data={
            'amount': amount,
            'email': email,
        })
        return JsonResponse(response)
    
@csrf_exempt
def paystack_webhook(request):
    if request.method == "POST":
        secret_key = settings.PAYSTACK_SECRET_KEY.encode('utf-8')
        signature = request.headers.get("x-paystack-signature")

        payload = request.body
        computed_signature = hmac.new(secret_key, payload, hashlib.sha512).hexdigest()

        if signature == computed_signature:  # Verify the request is from Paystack
            event = json.loads(payload)
            if event['event'] == "charge.success":
                # Extract necessary data
                data = event['data']
                reference = data['reference']
                status = data['status']
                amount = data['amount'] / 100  # Convert kobo to Naira

                # Update transaction in database
                from yourapp.models import Payment  # Import your Payment model
                try:
                    payment = Payment.objects.get(reference=reference)
                    payment.status = "paid" if status == "success" else "failed"
                    payment.save()
                except Payment.DoesNotExist:
                    return JsonResponse({"error": "Payment not found"}, status=400)

                return JsonResponse({"message": "Payment verified successfully"}, status=200)

        return JsonResponse({"error": "Invalid signature"}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)

#==============================================
# class PaystackWebhook(APIView):
#     def post(self, request):
#         raw_body = request.body
#         computed_hash = hmac.new(bytes(PAYSTACK_SECRET_KEY 'utf-8'), raw_body, hashlib.sha512).hexdigest()
#         paystack_signature = request.headers.get('x-paystack-signature')
#         if paystack_signature == computed_hash:
#             event = json.load(raw_body.decode('utf-8'))
#             print('Recieved paystack payload', event)
#             return 200
#         else:
#             print("Invalid paystack signature")
    
#==========================================
# class PaymentViewSet(viewsets.ModelViewSet):
#     queryset = Payment.objects.all()
#     serializer_class = PaymentSerializer
#     #permission_classes = [AllowAny]
#     permission_classes = [IsAuthenticated] 
    
# @login_required   
# def initiate_payment(request, booking_id):
#     booking = get_object_or_404(Booking, id=booking_id, user=request.user)
#     payment_method = request.POST.get("payment_method")
#     amount = booking.property.price
#     if payment_method == "paypal":
#                 return initiate_paypal_payment(request, booking, amount)
#     elif payment_method == "paystack":
#                 return initiate_paystack_payment(request, booking, amount)
#     elif payment_method == "credit_card":
#                 return initiate_stripe_payment(request, booking, amount)
#     else:
#                 return JsonResponse({"error": "Invalid payment method selected."}, status=400)


#     def initiate_paypal_payment(request, booking, amount):
#         PAYPAL_URL = "https://api-m.sandbox.paypal.com/v2/checkout/orders"
#         headers = {
#             "Content-Type": "application/json",
#             "Authorization": f"Bearer {settings.PAYPAL_ACCESS_TOKEN}",
#         }
#         data = {
#             "intent": "CAPTURE",
#             "purchase_units": [{"amount": {"currency_code": "USD", "value": str(amount)}}],
#         }
#         response = requests.post(PAYPAL_URL, json=data, headers=headers)
#         return JsonResponse(response.json())

#     def initiate_paystack_payment(request, booking, amount):
#         PAYSTACK_URL = "https://api.paystack.co/transaction/initialize"
#         headers = {
#             "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
#             "Content-Type": "application/json",
#         }
#         data = {
#             "email": request.user.email,
#             "amount": int(amount * 100),
#             "callback_url": request.build_absolute_uri(reverse("core:verify_paystack_payment")),
#         }
#         response = requests.post(PAYSTACK_URL, json=data, headers=headers)
#         return JsonResponse(response.json())

# def initiate_stripe_payment(request, booking, amount):
#     stripe.api_key = settings.STRIPE_SECRET_KEY
#     try:
#         payment_intent = stripe.PaymentIntent.create(
#             amount=int(amount * 100),
#             currency="usd",
#             payment_method_types=["card"],
#         )
#         return JsonResponse({"client_secret": payment_intent["client_secret"]})
#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=400)

#     def verify_paystack_payment(request):
#         transaction_id = request.GET.get("reference")
#         VERIFY_URL = f"https://api.paystack.co/transaction/verify/{transaction_id}"
#         headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
#         response = requests.get(VERIFY_URL, headers=headers).json()
#         if response["status"]:
#             booking = Booking.objects.get(id=response["data"]["metadata"]["booking_id"])
#             Payment.objects.create(
#                 user=booking.user,
#                 booking=booking,
#                 amount=booking.property.price,
#                 payment_method="paystack",
#                 status="completed",
#                 transaction_id=transaction_id,
#             )
#             messages.success(request, "Payment successful!")
#             return redirect("core:booking_detail", booking.id)
#         messages.error(request, "Payment verification failed.")
#         return redirect("core:user_dashboard")



# @login_required
# def process_payment(request, booking_id):

#     booking = get_object_or_404(Booking, id=booking_id, user=request.user)

#     if request.method == "POST":
#         payment_method = request.POST.get("payment_method")  
#         amount = booking.property.price * booking.get_total_days()

#         payment = Payment.objects.create(
#             user=request.user,
#             booking=booking,
#             amount=amount,
#             status="Pending",
#             payment_method=payment_method
#         )

#         payment.status = "Completed"
#         payment.save()

#         messages.success(request, "Payment successful!")
#         return redirect("core:booking_detail", booking.id)

#     return render(request, "core/payment.html", {"booking": booking})


#==========================================

# class PaymentViewSet(viewsets.ModelViewSet):
#     queryset = Payment.objects.all()
#     serializer_class = PaymentSerializer
#     permission_classes = [IsAuthenticated]

#     @action(detail=True, methods=["post"])
#     def initiate_payment(self, request, pk=None):
#         booking = get_object_or_404(Booking, id=pk, user=request.user)
#         payment_method = request.data.get("payment_method")
#         amount = booking.property.price * booking.get_total_days()

#         if payment_method == "paypal":
#             return self.initiate_paypal_payment(request, booking, amount)
#         elif payment_method == "paystack":
#             return self.initiate_paystack_payment(request, booking, amount)
#         elif payment_method == "credit_card":
#             return self.initiate_stripe_payment(request, booking, amount)
#         else:
#             return Response({"error": "Invalid payment method selected."}, status=status.HTTP_400_BAD_REQUEST)

#     def initiate_paypal_payment(self, request, booking, amount):
#         """Initiates a PayPal payment request."""
#         PAYPAL_URL = "https://api-m.sandbox.paypal.com/v2/checkout/orders"
#         headers = {
#             "Content-Type": "application/json",
#             "Authorization": f"Bearer {settings.PAYPAL_ACCESS_TOKEN}",
#         }
#         data = {
#             "intent": "CAPTURE",
#             "purchase_units": [{"amount": {"currency_code": "USD", "value": str(amount)}}],
#         }
#         response = requests.post(PAYPAL_URL, json=data, headers=headers)
        
#         if response.status_code == 201:
#             return Response(response.json(), status=status.HTTP_201_CREATED)
#         return Response({"error": "PayPal payment initiation failed"}, status=status.HTTP_400_BAD_REQUEST)

#     def initiate_paystack_payment(self, request, booking, amount):
#         """Initiates a Paystack payment request."""
#         PAYSTACK_URL = "https://api.paystack.co/transaction/initialize"
#         headers = {
#             "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
#             "Content-Type": "application/json",
#         }
#         data = {
#             "email": request.user.email,
#             "amount": int(amount * 100),
#             "callback_url": request.build_absolute_uri("/api/payments/verify-paystack/"),
#             "metadata": {"booking_id": booking.id}
#         }
#         response = requests.post(PAYSTACK_URL, json=data, headers=headers)
        
#         if response.status_code == 200:
#             return Response(response.json(), status=status.HTTP_200_OK)
#         return Response({"error": "Paystack payment initiation failed"}, status=status.HTTP_400_BAD_REQUEST)

#     def initiate_stripe_payment(self, request, booking, amount):
#         """Initiates a Stripe credit card payment request."""
#         stripe.api_key = settings.STRIPE_SECRET_KEY
#         try:
#             payment_intent = stripe.PaymentIntent.create(
#                 amount=int(amount * 100),
#                 currency="usd",
#                 payment_method_types=["card"],
#             )
#             return Response({"client_secret": payment_intent["client_secret"]}, status=status.HTTP_201_CREATED)
#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

#     @action(detail=False, methods=["get"])
#     def verify_paystack_payment(self, request):
#         """Verifies Paystack payment via transaction reference."""
#         transaction_id = request.GET.get("reference")
#         VERIFY_URL = f"https://api.paystack.co/transaction/verify/{transaction_id}"
#         headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
#         response = requests.get(VERIFY_URL, headers=headers).json()

#         if response["status"]:
#             booking_id = response["data"]["metadata"]["booking_id"]
#             booking = get_object_or_404(Booking, id=booking_id)
#             Payment.objects.create(
#                 user=booking.user,
#                 booking=booking,
#                 amount=booking.property.price,
#                 payment_method="paystack",
#                 status="completed",
#                 transaction_id=transaction_id,
#             )
#             return Response({"message": "Payment successful!"}, status=status.HTTP_200_OK)

#         return Response({"error": "Payment verification failed."}, status=status.HTTP_400_BAD_REQUEST)