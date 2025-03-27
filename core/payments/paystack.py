# payments/paystack.py

import os
import json
from django.http import JsonResponse
import requests

YOUR_PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY")

def initiate_paystack_payment(email: str, amount):
    url = 'https://api.paystack.co/transaction/initialize'
    headers = {
        'Authorization': f'Bearer {YOUR_PAYSTACK_SECRET_KEY}',
        'Content-Type': 'application/json'
    }
    
    body = {
        'amount': int(amount * 100),  
        'email': email,
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(body))
    if response.status_code == 200:
        data = response.json()
        return JsonResponse({"url": data['data']['authorization_url'], "reference": data['data']['reference']})

    return JsonResponse({"error": response.json().get('message', 'An error occurred')}, status=400)