# payments/paypal.py

import requests
import json
import os

YOUR_PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID")
YOUR_PAYPAL_SECRET = os.getenv("PAYPAL_SECRET")

def initiate_paypal_payment(request, booking, amount):
    # Use PayPal's API to create payment
    # For simplicity, this uses the REST API; ensure you have the right permissions configured
    
    url = "https://api.sandbox.paypal.com/v1/payments/payment"  # Use sandbox for testing
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Basic {YOUR_PAYPAL_CLIENT_ID}:{YOUR_PAYPAL_SECRET}'
    }
    
    body = {
        "intent": "sale",
        "redirect_urls": {
            "return_url": "http://localhost:8000/payment/success/",
            "cancel_url": "http://localhost:8000/payment/cancel/"
        },
        "payer": {
            "payment_method": "paypal"
        },
        "transactions": [{
            "amount": {
                "total": str(amount),
                "currency": "USD"  # Change this to your desired currency
            },
            "description": f"Booking payment for {booking.property.name}"
        }]
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(body))
    if response.status_code == 201:
        data = response.json()
        return JsonResponse({"approval_url": data['links'][1]['href']})
    
    return JsonResponse({"error": "PayPal payment initiation failed"}, status=400)