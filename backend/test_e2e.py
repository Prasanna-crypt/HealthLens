import requests
import json
import uuid
import sys

BASE_URL = "http://127.0.0.1:8000/api"
session = requests.Session()

def print_result(name, res):
    if res.status_code < 400:
        print(f"[PASS] {name}")
    else:
        print(f"[FAIL] {name} - {res.status_code}: {res.text}")

try:
    # 1. Auth Registration & Login
    unique_id = str(uuid.uuid4())[:8]
    email = f"test_{unique_id}@example.com"
    password = "password123"

    res = session.post(f"{BASE_URL}/auth/register", json={
        "email": email,
        "password": password,
        "full_name": "Test User"
    })
    print_result("Register", res)

    res = session.post(f"{BASE_URL}/auth/login", data={
        "username": email,
        "password": password
    })
    print_result("Login", res)
    token = res.json().get("access_token")
    session.headers.update({"Authorization": f"Bearer {token}"})

    # 2. Test Profile
    res = session.get(f"{BASE_URL}/profile")
    print_result("Get Profile", res)

    res = session.put(f"{BASE_URL}/profile", json={
        "full_name": "Updated Test User",
        "height": 180.5,
        "weight": 75.0,
        "blood_group": "O+"
    })
    print_result("Update Profile", res)

    # 3. Test Core Endpoints
    res = session.get(f"{BASE_URL}/reports/")
    print_result("Get Reports List", res)

    res = session.get(f"{BASE_URL}/results/patterns")
    print_result("Get Patterns", res)

    res = session.get(f"{BASE_URL}/results/changes")
    print_result("Get Changes", res)

    res = session.get(f"{BASE_URL}/results/user/unique-tests")
    print_result("Get Unique Tests", res)

    # 4. Test AI Assistant
    res = session.post(f"{BASE_URL}/ai/assistant", json={
        "question": "Hello, what is my blood group?"
    })
    print_result("AI Assistant", res)
except Exception as e:
    print(f"[ERROR] {e}")
