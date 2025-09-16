#!/usr/bin/env python3

import requests
import json

def test_api():
    """Test the medical chatbot API endpoints"""
    base_url = "http://localhost:5000"
    
    print("Testing AI Medical Chatbot API...")
    print("=" * 50)
    
    # Test 1: Root endpoint
    try:
        response = requests.get(f"{base_url}/")
        print(f"✅ Root endpoint: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"❌ Root endpoint failed: {e}")
    
    print("\n" + "-" * 30)
    
    # Test 2: Chat endpoint
    try:
        chat_data = {
            "message": "I have fever and headache",
            "language": "en"
        }
        response = requests.post(f"{base_url}/chat", json=chat_data)
        print(f"✅ Chat endpoint: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"❌ Chat endpoint failed: {e}")
    
    print("\n" + "-" * 30)
    
    # Test 3: Diseases endpoint
    try:
        response = requests.get(f"{base_url}/diseases")
        print(f"✅ Diseases endpoint: {response.status_code}")
        data = response.json()
        print(f"Found {data.get('total', 0)} diseases")
    except Exception as e:
        print(f"❌ Diseases endpoint failed: {e}")
    
    print("\n" + "-" * 30)
    
    # Test 4: Emergency endpoint
    try:
        response = requests.get(f"{base_url}/emergency")
        print(f"✅ Emergency endpoint: {response.status_code}")
        data = response.json()
        print(f"Emergency contacts: {list(data.get('emergency_contacts', {}).keys())}")
    except Exception as e:
        print(f"❌ Emergency endpoint failed: {e}")

if __name__ == "__main__":
    test_api()