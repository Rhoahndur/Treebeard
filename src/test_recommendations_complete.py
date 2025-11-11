#!/usr/bin/env python3
"""
Complete end-to-end test of recommendations flow with all fixes applied.
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8888/api/v1"

def test_recommendations_flow():
    """Test the complete recommendations generation flow."""

    print("=" * 80)
    print("TESTING COMPLETE RECOMMENDATIONS FLOW")
    print("=" * 80)

    # Step 1: Login
    print("\n[1/3] Logging in...")
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        data={
            "username": "admin@treebeard.com",
            "password": "admin123"
        }
    )

    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(login_response.text)
        return False

    token = login_response.json()["access_token"]
    print(f"✅ Login successful. Token: {token[:50]}...")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Step 2: Generate recommendations
    print("\n[2/3] Generating recommendations...")

    # Generate 12 months of usage data
    usage_data = []
    base_month = datetime.now().replace(day=1) - timedelta(days=365)
    for i in range(12):
        month = base_month + timedelta(days=30 * i)
        usage_data.append({
            "month": month.strftime("%Y-%m-%d"),
            "kwh": 1000 + (i * 50) % 300  # Vary usage between 1000-1300 kWh
        })

    rec_data = {
        "user_data": {
            "zip_code": "94000",
            "property_type": "residential"
        },
        "usage_data": usage_data,
        "preferences": {
            "cost_priority": 40,
            "flexibility_priority": 30,
            "renewable_priority": 20,
            "rating_priority": 10
        },
        "current_plan": {
            "plan_name": "Old Plan",
            "supplier_name": "Old Supplier",
            "current_rate": 12.5,
            "contract_end_date": (datetime.now() + timedelta(days=90)).strftime("%Y-%m-%d"),
            "early_termination_fee": 150.00,
            "annual_cost": 1500.00,
            "contract_start_date": (datetime.now() - timedelta(days=275)).strftime("%Y-%m-%d")
        },
        "include_risks": True
    }

    print(f"Request data: {json.dumps(rec_data, indent=2)}")

    try:
        rec_response = requests.post(
            f"{BASE_URL}/recommendations/generate",
            json=rec_data,
            headers=headers,
            timeout=60
        )

        print(f"\nResponse status: {rec_response.status_code}")

        if rec_response.status_code != 200:
            print(f"❌ Recommendations generation failed!")
            print(f"Response: {rec_response.text}")
            return False

        result = rec_response.json()
        print(f"✅ Recommendations generated successfully!")

        # Step 3: Validate response structure
        print("\n[3/3] Validating response structure...")

        required_fields = [
            "recommendations",
            "usage_analysis",
            "savings_analysis",
            "market_insights",
            "alerts"
        ]

        missing_fields = [f for f in required_fields if f not in result]
        if missing_fields:
            print(f"❌ Missing fields: {missing_fields}")
            return False

        print("✅ All required fields present")

        # Check recommendations
        if "top_plans" in result["recommendations"]:
            plans = result["recommendations"]["top_plans"]
            print(f"\n📊 Found {len(plans)} recommended plans:")

            for i, plan in enumerate(plans, 1):
                print(f"\n  Plan {i}: {plan.get('plan_name', 'Unknown')}")
                print(f"    Supplier: {plan.get('supplier_name', 'Unknown')}")
                print(f"    Annual Cost: ${plan.get('projected_annual_cost', 0):.2f}")
                print(f"    Renewable: {plan.get('renewable_percentage', 0):.0f}%")
                print(f"    Contract: {plan.get('contract_length_months', 0)} months")

                # Check for the newly added fields
                if 'projected_annual_savings' in plan and plan['projected_annual_savings'] is not None:
                    print(f"    Annual Savings: ${plan['projected_annual_savings']:.2f}")
                else:
                    print(f"    Annual Savings: Not calculated")

                if 'break_even_months' in plan and plan['break_even_months'] is not None:
                    print(f"    Break-even: {plan['break_even_months']} months")

                # Check for explanation
                if 'explanation' in plan:
                    print(f"    Explanation: {plan['explanation'][:100]}...")
                else:
                    print(f"    ⚠️  No explanation generated")

        # Check usage analysis
        if "profile_type" in result["usage_analysis"]:
            print(f"\n🔍 Usage Profile: {result['usage_analysis']['profile_type']}")

        # Check savings analysis
        if "total_annual_savings" in result["savings_analysis"]:
            savings = result["savings_analysis"]["total_annual_savings"]
            print(f"\n💰 Total Annual Savings: ${savings:.2f}")

        # Check market insights
        if "average_market_rate" in result["market_insights"]:
            market_rate = result["market_insights"]["average_market_rate"]
            print(f"\n📈 Average Market Rate: {market_rate:.2f}¢/kWh")

        # Check alerts
        if isinstance(result["alerts"], list):
            print(f"\n⚠️  Alerts: {len(result['alerts'])} alert(s)")
            for alert in result["alerts"][:3]:  # Show first 3
                print(f"    - {alert.get('message', 'No message')[:80]}...")

        print("\n" + "=" * 80)
        print("✅ COMPLETE FLOW TEST PASSED!")
        print("=" * 80)

        return True

    except requests.exceptions.Timeout:
        print("❌ Request timed out after 60 seconds")
        return False
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_recommendations_flow()
    exit(0 if success else 1)
