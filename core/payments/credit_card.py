# payments/credit_card.py

# Using an example of Stripe for credit card processing
import os
import stripe
from django.http import JsonResponse

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

def initiate_stripe_payment(request, amount):
    try:
        # Assume token is being sent from the frontend
        token = request.POST.get("stripeToken")
        
        charge = stripe.Charge.create(
            amount=int(amount * 100),  # amount in cents
            currency='usd',  # Change currency as needed
            description='Payment for booking',
            source=token
        )
        
        return JsonResponse({"success": True, "charge": charge})

    except stripe.error.CardError as e:
        return JsonResponse({"error": str(e)}, status=400)