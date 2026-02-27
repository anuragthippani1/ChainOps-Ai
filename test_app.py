#!/usr/bin/env python3
"""
Simple test script to verify SentriX backend functionality
"""

import requests
import json
import time

def test_backend():
    """Test the SentriX backend API"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing SentriX Backend API")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1. Testing health check...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Backend is running")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend. Make sure it's running on port 8000")
        return False
    
    # Test 2: Dashboard data
    print("\n2. Testing dashboard data...")
    try:
        response = requests.get(f"{base_url}/api/dashboard")
        if response.status_code == 200:
            data = response.json()
            print("✅ Dashboard data loaded successfully")
            print(f"   Countries monitored: {len(data.get('world_risk_data', {}))}")
            print(f"   Political risks: {len(data.get('political_risks', []))}")
            print(f"   Schedule risks: {len(data.get('schedule_risks', []))}")
        else:
            print(f"❌ Dashboard data failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Dashboard data error: {e}")
    
    # Test 3: Chat query
    print("\n3. Testing chat query...")
    try:
        query_data = {"query": "What are the political risks?"}
        response = requests.post(f"{base_url}/api/query", json=query_data)
        if response.status_code == 200:
            data = response.json()
            print("✅ Chat query processed successfully")
            print(f"   Response type: {data.get('type', 'unknown')}")
            if 'response' in data:
                print(f"   Message: {data['response'].get('message', 'No message')[:100]}...")
        else:
            print(f"❌ Chat query failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Chat query error: {e}")
    
    # Test 4: Reports
    print("\n4. Testing reports...")
    try:
        response = requests.get(f"{base_url}/api/reports")
        if response.status_code == 200:
            data = response.json()
            print("✅ Reports endpoint working")
            print(f"   Total reports: {len(data.get('reports', []))}")
        else:
            print(f"❌ Reports failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Reports error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Backend testing completed!")
    return True

if __name__ == "__main__":
    test_backend()
