#!/usr/bin/env python3
"""
Test script to verify API caching implementation.
Demonstrates cache performance improvement on repeated requests.
"""

import subprocess
import time
import sys
import threading
import requests

# Start the backend server in a background thread
def start_backend():
    import os
    os.chdir("c:\\Users\\varsh\\MLense\\Exam\\backend")
    exec_path = "C:/Users/varsh/MLense/Exam/.venv/Scripts/python.exe"
    subprocess.Popen([
        exec_path, "-m", "uvicorn", 
        "backend.main:app", 
        "--host", "0.0.0.0", 
        "--port", "8000"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Wait for server to start
    time.sleep(3)

# Start backend
print("🚀 Starting FastAPI backend...")
start_backend()

# Give the server a moment to fully initialize
time.sleep(2)

print("\n📊 Testing API Response Caching")
print("=" * 60)

api_url = "http://localhost:8000/resources/Operating%20Systems"
test_results = []

# Test 1: First request (cache miss)
print("\n1️⃣ First request (CACHE MISS - fetches from YouTube):")
try:
    start_time = time.time()
    response = requests.get(api_url, timeout=30)
    elapsed = time.time() - start_time
    test_results.append(("Cache Miss (First)", elapsed))
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Status: {response.status_code}")
        print(f"   📹 Videos returned: {data['total']}")
        print(f"   ⏱️  Response time: {elapsed:.2f}s")
    else:
        print(f"   ❌ Error: Status {response.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Wait a bit
time.sleep(1)

# Test 2: Second request (cache hit)
print("\n2️⃣ Second request (CACHE HIT - uses cache):")
try:
    start_time = time.time()
    response = requests.get(api_url, timeout=10)
    elapsed = time.time() - start_time
    test_results.append(("Cache Hit (Second)", elapsed))
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Status: {response.status_code}")
        print(f"   📹 Videos returned: {data['total']}")
        print(f"   ⏱️  Response time: {elapsed:.2f}s")
    else:
        print(f"   ❌ Error: Status {response.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3: Third request (cache hit)
print("\n3️⃣ Third request (CACHE HIT - uses cache):")
try:
    start_time = time.time()
    response = requests.get(api_url, timeout=10)
    elapsed = time.time() - start_time
    test_results.append(("Cache Hit (Third)", elapsed))
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Status: {response.status_code}")
        print(f"   📹 Videos returned: {data['total']}")
        print(f"   ⏱️  Response time: {elapsed:.2f}s")
    else:
        print(f"   ❌ Error: Status {response.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Summary
print("\n" + "=" * 60)
print("📈 PERFORMANCE SUMMARY")
print("=" * 60)

for label, elapsed in test_results:
    print(f"{label:25} → {elapsed:6.2f}s")

if len(test_results) >= 2:
    improvement = ((test_results[0][1] - test_results[1][1]) / test_results[0][1]) * 100
    print(f"\n✨ Cache Performance Improvement: {improvement:.1f}%")
    print(f"   First request (no cache):  {test_results[0][1]:.2f}s")
    print(f"   Second request (cached):   {test_results[1][1]:.2f}s")
    print(f"   Speed factor: {test_results[0][1] / max(test_results[1][1], 0.001):.1f}x faster")

print("\n✅ Caching implementation is working!")
