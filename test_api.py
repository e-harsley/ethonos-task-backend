#!/usr/bin/env python
"""
Simple script to test the Wallet API endpoints
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

def print_response(response):
    """Pretty print API response"""
    print(f"Status Code: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)
    print("-" * 80)

def test_registration():
    """Test user registration"""
    print("\n=== Testing User Registration ===")
    url = f"{BASE_URL}/auth/register"
    data = {
        "email": "test@example.com",
        "password": "password123",
        "first_name": "Test",
        "last_name": "User",
        "phone_number": "+234 800 000 0000"
    }
    response = requests.post(url, json=data)
    print_response(response)

    if response.status_code == 201:
        tokens = response.json()
        return tokens['access'], tokens['refresh']
    return None, None

def test_login():
    """Test user login"""
    print("\n=== Testing User Login ===")
    url = f"{BASE_URL}/auth/login"
    data = {
        "email": "deji@example.com",
        "password": "password123"
    }
    response = requests.post(url, json=data)
    print_response(response)

    if response.status_code == 200:
        tokens = response.json()
        return tokens['access'], tokens['refresh']
    return None, None

def test_get_user(access_token):
    """Test get current user"""
    print("\n=== Testing Get Current User ===")
    url = f"{BASE_URL}/auth/me"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    print_response(response)

def test_get_wallet(access_token):
    """Test get wallet"""
    print("\n=== Testing Get Wallet ===")
    url = f"{BASE_URL}/wallet/wallet"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    print_response(response)

def test_add_card(access_token):
    """Test add card"""
    print("\n=== Testing Add Card ===")
    url = f"{BASE_URL}/wallet/cards"
    headers = {"Authorization": f"Bearer {access_token}"}
    data = {
        "card_number": "4111111111111111",
        "card_type": "credit",
        "card_holder_name": "Deji Designer",
        "expiry_date": "12/25",
        "bank_name": "First Bank",
        "is_primary": True
    }
    response = requests.post(url, json=data, headers=headers)
    print_response(response)

def test_create_transaction(access_token):
    """Test create transaction"""
    print("\n=== Testing Create Transaction ===")
    url = f"{BASE_URL}/wallet/transactions"
    headers = {"Authorization": f"Bearer {access_token}"}
    data = {
        "transaction_type": "income",
        "amount": 2500000.00,
        "description": "Monthly Salary",
        "category": "Salary"
    }
    response = requests.post(url, json=data, headers=headers)
    print_response(response)

def test_generate_qr_code(access_token):
    """Test generate QR code"""
    print("\n=== Testing Generate QR Code ===")
    url = f"{BASE_URL}/wallet/qr-codes/generate"
    headers = {"Authorization": f"Bearer {access_token}"}
    data = {
        "amount": 5000.00,
        "description": "Payment Request",
        "expires_in_hours": 24
    }
    response = requests.post(url, json=data, headers=headers)
    print_response(response)

def test_get_stats(access_token):
    """Test get statistics"""
    print("\n=== Testing Get Statistics ===")
    url = f"{BASE_URL}/wallet/stats?months=6"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    print_response(response)

def main():
    print("=" * 80)
    print("Deji's Wallet API - Test Suite")
    print("=" * 80)

    # Test login
    access_token, refresh_token = test_login()

    if not access_token:
        print("\n❌ Login failed. Make sure the user is registered first.")
        return

    print(f"\n✅ Access Token: {access_token[:50]}...")

    # Run protected endpoints tests
    test_get_user(access_token)
    test_get_wallet(access_token)
    test_add_card(access_token)
    test_create_transaction(access_token)
    test_generate_qr_code(access_token)
    test_get_stats(access_token)

    print("\n" + "=" * 80)
    print("✅ API Test Suite Completed!")
    print("=" * 80)

if __name__ == "__main__":
    main()
