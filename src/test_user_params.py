#!/usr/bin/env python3
"""Test with exact user parameters."""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8888/api/v1"

# Step 1: Login
print("Logging in...")
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    data={
        "username": "admin@treebeard.com",
        "password": "admin123"
    }
)
token = login_response.json()["access_token"]
print(f"✅ Got token: {token[:30]}...")

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Step 2: Generate recommendations with USER'S EXACT PARAMETERS
print("\n📊 Testing with user's exact parameters:")
print("  ZIP: 78701")
print("  Current Provider: TXU Energy")
print("  Average Rate: 20 c/kWh")
print("  Early Cancellation: $200")
print("  Monthly Base Fee: $100")

# Generate 12 months of usage data (user said they added monthly usage for 12 months)
usage_data = []
base_month = datetime.now().replace(day=1) - timedelta(days=365)
for i in range(12):
    month = base_month + timedelta(days=30 * i)
    usage_data.append({
        "month": month.strftime("%Y-%m-%d"),
        "kwh": 1000  # Default usage
    })

rec_data = {
    "user_data": {
        "zip_code": "78701",  # USER'S ZIP
        "property_type": "residential"
    },
    "usage_data": usage_data,
    "preferences": {
        "cost_priority": 34,  # Default from frontend
        "flexibility_priority": 33,
        "renewable_priority": 33,
        "rating_priority": 0
    },
    "current_plan": {
        "plan_name": "Current Plan",
        "supplier_name": "TXU Energy",  # USER'S CURRENT SUPPLIER
        "current_rate": 20.0,  # USER'S RATE (20 c/kWh)
        "contract_end_date": (datetime.now() + timedelta(days=90)).strftime("%Y-%m-%d"),
        "early_termination_fee": 200.00,  # USER'S ETF
        "annual_cost": 2400.00,  # 1000 kWh * 12 months * $0.20/kWh
        "contract_start_date": (datetime.now() - timedelta(days=275)).strftime("%Y-%m-%d")
    },
    "include_risks": True
}

print(f"\n📤 Sending request...")
rec_response = requests.post(
    f"{BASE_URL}/recommendations/generate",
    json=rec_data,
    headers=headers,
    timeout=60
)

print(f"\n📥 Response status: {rec_response.status_code}")

if rec_response.status_code == 200:
    result = rec_response.json()
    print("\n✅ SUCCESS! Response structure:")
    print(json.dumps(list(result.keys()), indent=2))

    # Check if there are plans
    if "recommendations" in result and "top_plans" in result["recommendations"]:
        plans = result["recommendations"]["top_plans"]
        print(f"\n🎉 Found {len(plans)} recommended plans!")

        for i, plan in enumerate(plans, 1):
            print(f"\n  Plan {i}: {plan.get('plan_name', 'Unknown')}")
            print(f"    Supplier: {plan.get('supplier_name', 'Unknown')}")
            print(f"    Annual Cost: ${plan.get('projected_annual_cost', 0):.2f}")
    else:
        print("\n⚠️  No plans in response")
        print(json.dumps(result, indent=2))
else:
    print(f"\n❌ Error: {rec_response.status_code}")
    print(rec_response.text)
