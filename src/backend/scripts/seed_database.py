"""
Database Seeding Script for TreeBeard Energy Recommendation MVP

This script populates the database with:
- Realistic energy suppliers (Texas-based)
- Diverse energy plans (fixed, variable, renewable options)
- Admin user for management
- Coverage across major Texas ZIP codes

Run: python backend/scripts/seed_database.py
"""

import sys
import os
from datetime import datetime, date
from decimal import Decimal
from uuid import uuid4

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.settings import settings
from models.plan import Supplier, PlanCatalog
from models.user import User
from api.auth.jwt import get_password_hash


# Texas ZIP codes to cover (major cities)
TEXAS_ZIP_CODES = [
    # Austin
    "78701", "78702", "78703", "78704", "78705", "78721", "78722", "78723", "78724", "78725",
    "78726", "78727", "78728", "78729", "78730", "78731", "78732", "78733", "78734", "78735",
    "78736", "78737", "78738", "78739", "78741", "78742", "78744", "78745", "78746", "78747",
    "78748", "78749", "78750", "78751", "78752", "78753", "78754", "78756", "78757", "78758",
    "78759",
    # Houston
    "77001", "77002", "77003", "77004", "77005", "77006", "77007", "77008", "77009", "77010",
    "77019", "77020", "77021", "77025", "77030", "77035", "77036", "77040", "77041", "77042",
    "77043", "77044", "77045", "77046", "77047", "77048", "77049", "77050", "77051", "77054",
    "77055", "77056", "77057", "77058", "77059", "77060", "77061", "77062", "77063", "77064",
    # Dallas
    "75201", "75202", "75203", "75204", "75205", "75206", "75207", "75208", "75209", "75210",
    "75211", "75212", "75214", "75215", "75216", "75217", "75218", "75219", "75220", "75223",
    "75224", "75225", "75226", "75227", "75228", "75229", "75230", "75231", "75232", "75233",
    # San Antonio
    "78201", "78202", "78203", "78204", "78205", "78207", "78208", "78209", "78210", "78211",
    "78212", "78213", "78214", "78215", "78216", "78217", "78218", "78219", "78220", "78221",
]


def seed_suppliers(db):
    """Create realistic Texas energy suppliers."""
    print("Seeding suppliers...")

    # Check if suppliers already exist
    existing_count = db.query(Supplier).count()
    if existing_count > 0:
        print(f"⚠ Found {existing_count} existing suppliers, skipping supplier seeding...")
        suppliers = db.query(Supplier).all()
        return suppliers

    suppliers_data = [
        {
            "supplier_name": "TXU Energy",
            "website": "https://www.txu.com",
            "customer_service_phone": "1-800-242-9113",
            "average_rating": Decimal("4.2"),
            "review_count": 5243,
            "description": "One of Texas' largest retail electricity providers, offering competitive rates and renewable energy options.",
            "service_areas": ["Austin", "Dallas", "Houston", "Fort Worth"],
            "license_number": "TX-10001",
        },
        {
            "supplier_name":"Reliant Energy",
            "website": "https://www.reliant.com",
            "customer_service_phone":"1-866-222-7100",
            "email": "customercare@reliant.com",
            "average_rating":Decimal("4.0"),
            "review_count": 4521,
            "description": "Trusted energy provider with flexible plans and green energy options.",
            "service_areas": ["Houston", "Galveston", "Corpus Christi"],
            "license_number": "TX-10002",
        },
        {
            "supplier_name":"Direct Energy",
            "website": "https://www.directenergy.com",
            "customer_service_phone":"1-866-201-7173",
            "email": "help@directenergy.com",
            "average_rating":Decimal("3.9"),
            "review_count": 3842,
            "description": "Competitive rates with straightforward plans and excellent customer service.",
            "service_areas": ["Dallas", "Austin", "San Antonio"],
            "license_number": "TX-10003",
        },
        {
            "supplier_name":"Green Mountain Energy",
            "website": "https://www.greenmountainenergy.com",
            "customer_service_phone":"1-888-895-2055",
            "email": "service@greenmountainenergy.com",
            "average_rating":Decimal("4.5"),
            "review_count": 2934,
            "description": "100% renewable energy plans for environmentally conscious customers.",
            "service_areas": ["Austin", "Dallas", "Houston"],
            "license_number": "TX-10004",
        },
        {
            "supplier_name":"Champion Energy",
            "website": "https://www.championenergyservices.com",
            "customer_service_phone":"1-866-446-0499",
            "email": "info@championenergy.com",
            "average_rating":Decimal("3.8"),
            "review_count": 2156,
            "description": "Budget-friendly electricity plans with flexible contract options.",
            "service_areas": ["Houston", "Dallas", "Fort Worth"],
            "license_number": "TX-10005",
        },
        {
            "supplier_name":"Gexa Energy",
            "website": "https://www.gexaenergy.com",
            "customer_service_phone":"1-866-961-9399",
            "email": "customersupport@gexaenergy.com",
            "average_rating":Decimal("3.7"),
            "review_count": 1876,
            "description": "Simple, affordable electricity plans with renewable options.",
            "service_areas": ["Dallas", "Houston", "San Antonio"],
            "license_number": "TX-10006",
        },
        {
            "supplier_name":"Frontier Utilities",
            "website": "https://www.frontierutilities.com",
            "customer_service_phone":"1-866-480-2226",
            "email": "support@frontierutilities.com",
            "average_rating":Decimal("4.1"),
            "review_count": 1654,
            "description": "Customer-focused provider with competitive fixed-rate plans.",
            "service_areas": ["Austin", "Dallas", "Waco"],
            "license_number": "TX-10007",
        },
        {
            "supplier_name":"4Change Energy",
            "website": "https://www.4changeenergy.com",
            "customer_service_phone":"1-877-933-5443",
            "email": "info@4changeenergy.com",
            "average_rating":Decimal("4.3"),
            "review_count": 1432,
            "description": "Innovative renewable energy plans with community giving programs.",
            "service_areas": ["Houston", "Austin", "Corpus Christi"],
            "license_number": "TX-10008",
        },
        {
            "supplier_name":"Cirro Energy",
            "website": "https://www.cirroenergy.com",
            "customer_service_phone":"1-844-222-4776",
            "email": "hello@cirroenergy.com",
            "average_rating":Decimal("3.9"),
            "review_count": 1298,
            "description": "Straightforward electricity plans with no surprises.",
            "service_areas": ["Dallas", "Austin", "Houston"],
            "license_number": "TX-10009",
        },
        {
            "supplier_name":"Pulse Power",
            "website": "https://www.pulsepower.com",
            "customer_service_phone":"1-877-785-7373",
            "email": "support@pulsepower.com",
            "average_rating":Decimal("3.6"),
            "review_count": 1187,
            "description": "Prepaid and traditional electricity plans with flexible options.",
            "service_areas": ["Houston", "Dallas", "San Antonio"],
            "license_number": "TX-10010",
        },
        {
            "supplier_name":"Discount Power",
            "website": "https://www.discountpower.com",
            "customer_service_phone":"1-866-657-0247",
            "email": "info@discountpower.com",
            "average_rating":Decimal("3.5"),
            "review_count": 1056,
            "description": "Low-cost electricity with month-to-month and fixed-rate options.",
            "service_areas": ["Dallas", "Fort Worth", "Houston"],
            "license_number": "TX-10011",
        },
        {
            "supplier_name":"Ambit Energy",
            "website": "https://www.ambitenergy.com",
            "customer_service_phone":"1-877-282-6248",
            "email": "customercare@ambitenergy.com",
            "average_rating":Decimal("3.4"),
            "review_count": 967,
            "description": "Competitive rates with customer rewards program.",
            "service_areas": ["Dallas", "Houston", "Austin"],
            "license_number": "TX-10012",
        },
        {
            "supplier_name":"Tara Energy",
            "website": "https://www.taraenergy.com",
            "customer_service_phone":"1-866-368-7802",
            "email": "help@taraenergy.com",
            "average_rating":Decimal("4.0"),
            "review_count": 845,
            "description": "Texas-based provider with renewable energy options and local support.",
            "service_areas": ["Houston", "Austin", "San Antonio"],
            "license_number": "TX-10013",
        },
        {
            "supplier_name":"Just Energy",
            "website": "https://www.justenergy.com",
            "customer_service_phone":"1-866-587-8674",
            "email": "support@justenergy.com",
            "average_rating":Decimal("3.3"),
            "review_count": 723,
            "description": "Energy plans with price protection and green options.",
            "service_areas": ["Dallas", "Houston", "Corpus Christi"],
            "license_number": "TX-10014",
        },
        {
            "supplier_name":"Express Energy",
            "website": "https://www.expressenergy.com",
            "customer_service_phone":"1-888-397-7377",
            "email": "info@expressenergy.com",
            "average_rating":Decimal("3.8"),
            "review_count": 654,
            "description": "Simple electricity plans with transparent pricing.",
            "service_areas": ["Austin", "Dallas", "Houston"],
            "license_number": "TX-10015",
        },
    ]

    suppliers = []
    for data in suppliers_data:
        supplier = Supplier(
            id=uuid4(),
            supplier_name=data["supplier_name"],
            website=data.get("website"),
            customer_service_phone=data.get("customer_service_phone"),
            average_rating=data.get("average_rating"),
            review_count=data.get("review_count", 0),
            is_active=True,
            created_at=datetime.utcnow(),
        )
        db.add(supplier)
        suppliers.append(supplier)

    db.commit()
    print(f"✓ Created {len(suppliers)} suppliers")
    return suppliers


def seed_plans(db, suppliers):
    """Create diverse energy plans."""
    print("Seeding energy plans...")

    # Check if plans already exist
    existing_count = db.query(PlanCatalog).count()
    if existing_count > 0:
        print(f"⚠ Found {existing_count} existing plans, skipping plan seeding...")
        plans = db.query(PlanCatalog).all()
        return plans

    plans_data = [
        # TXU Energy Plans
        {
            "supplier": suppliers[0],
            "supplier_name":"TXU Energy Secure 12",
            "plan_type": "fixed",
            "contract_length_months": 12,
            "rate_structure": "fixed",
            "base_rate": Decimal("11.9"),
            "renewable_percentage": Decimal("0"),
            "monthly_fee": Decimal("9.95"),
            "early_termination_fee": Decimal("150"),
            "description": "Fixed rate for 12 months with predictable billing.",
            "regions": TEXAS_ZIP_CODES[:100],
        },
        {
            "supplier": suppliers[0],
            "supplier_name":"TXU Energy Secure 24",
            "plan_type": "fixed",
            "contract_length_months": 24,
            "rate_structure": "fixed",
            "base_rate": Decimal("11.2"),
            "renewable_percentage": Decimal("0"),
            "monthly_fee": Decimal("9.95"),
            "early_termination_fee": Decimal("240"),
            "description": "Locked-in rate for 24 months with lowest price.",
            "regions": TEXAS_ZIP_CODES[:100],
        },
        {
            "supplier": suppliers[0],
            "supplier_name":"TXU Energy Solar Choice 12",
            "plan_type": "fixed",
            "contract_length_months": 12,
            "rate_structure": "fixed",
            "base_rate": Decimal("12.8"),
            "renewable_percentage": Decimal("100"),
            "monthly_fee": Decimal("9.95"),
            "early_termination_fee": Decimal("150"),
            "description": "100% renewable solar energy with 12-month contract.",
            "regions": TEXAS_ZIP_CODES[:80],
        },
        # Reliant Energy Plans
        {
            "supplier": suppliers[1],
            "supplier_name":"Reliant Basic Power 12",
            "plan_type": "fixed",
            "contract_length_months": 12,
            "rate_structure": "fixed",
            "base_rate": Decimal("12.1"),
            "renewable_percentage": Decimal("0"),
            "monthly_fee": Decimal("4.95"),
            "early_termination_fee": Decimal("150"),
            "description": "Simple fixed-rate plan with low monthly fee.",
            "regions": TEXAS_ZIP_CODES[:90],
        },
        {
            "supplier": suppliers[1],
            "supplier_name":"Reliant Flex Monthly",
            "plan_type": "variable",
            "contract_length_months": 0,
            "rate_structure": "variable",
            "base_rate": Decimal("13.5"),
            "renewable_percentage": Decimal("0"),
            "monthly_fee": Decimal("0"),
            "early_termination_fee": Decimal("0"),
            "description": "Month-to-month flexibility with no contract commitment.",
            "regions": TEXAS_ZIP_CODES[:90],
        },
        {
            "supplier": suppliers[1],
            "supplier_name":"Reliant Truly Free Weekends 12",
            "plan_type": "fixed",
            "contract_length_months": 12,
            "rate_structure": "tiered",
            "base_rate": Decimal("14.2"),
            "renewable_percentage": Decimal("0"),
            "monthly_fee": Decimal("9.95"),
            "early_termination_fee": Decimal("175"),
            "description": "Free electricity every weekend.",
            "regions": TEXAS_ZIP_CODES[:70],
        },
        # Direct Energy Plans
        {
            "supplier": suppliers[2],
            "supplier_name":"Direct Energy Live Brighter 12",
            "plan_type": "fixed",
            "contract_length_months": 12,
            "rate_structure": "fixed",
            "base_rate": Decimal("11.5"),
            "renewable_percentage": Decimal("0"),
            "monthly_fee": Decimal("4.95"),
            "early_termination_fee": Decimal("150"),
            "description": "Competitive fixed rate with rewards.",
            "regions": TEXAS_ZIP_CODES[:85],
        },
        {
            "supplier": suppliers[2],
            "supplier_name":"Direct Energy All Green 12",
            "plan_type": "fixed",
            "contract_length_months": 12,
            "rate_structure": "fixed",
            "base_rate": Decimal("13.1"),
            "renewable_percentage": Decimal("100"),
            "monthly_fee": Decimal("4.95"),
            "early_termination_fee": Decimal("150"),
            "description": "100% renewable energy from wind and solar.",
            "regions": TEXAS_ZIP_CODES[:75],
        },
        # Green Mountain Energy Plans
        {
            "supplier": suppliers[3],
            "supplier_name":"Pollution Free 12",
            "plan_type": "fixed",
            "contract_length_months": 12,
            "rate_structure": "fixed",
            "base_rate": Decimal("12.9"),
            "renewable_percentage": Decimal("100"),
            "monthly_fee": Decimal("9.95"),
            "early_termination_fee": Decimal("150"),
            "description": "100% renewable energy from Texas wind farms.",
            "regions": TEXAS_ZIP_CODES[:80],
        },
        {
            "supplier": suppliers[3],
            "supplier_name":"Renewable Rewards 24",
            "plan_type": "fixed",
            "contract_length_months": 24,
            "rate_structure": "fixed",
            "base_rate": Decimal("12.1"),
            "renewable_percentage": Decimal("100"),
            "monthly_fee": Decimal("9.95"),
            "early_termination_fee": Decimal("240"),
            "description": "Long-term renewable energy commitment with best rate.",
            "regions": TEXAS_ZIP_CODES[:80],
        },
        {
            "supplier": suppliers[3],
            "supplier_name":"Pollution Free Month-to-Month",
            "plan_type": "variable",
            "contract_length_months": 0,
            "rate_structure": "variable",
            "base_rate": Decimal("14.5"),
            "renewable_percentage": Decimal("100"),
            "monthly_fee": Decimal("9.95"),
            "early_termination_fee": Decimal("0"),
            "description": "Flexible renewable energy with no contract.",
            "regions": TEXAS_ZIP_CODES[:70],
        },
        # Champion Energy Plans
        {
            "supplier": suppliers[4],
            "supplier_name":"Champ Saver 12",
            "plan_type": "fixed",
            "contract_length_months": 12,
            "rate_structure": "fixed",
            "base_rate": Decimal("10.8"),
            "renewable_percentage": Decimal("0"),
            "monthly_fee": Decimal("4.95"),
            "early_termination_fee": Decimal("150"),
            "description": "Budget-friendly fixed rate for cost-conscious customers.",
            "regions": TEXAS_ZIP_CODES[:95],
        },
        {
            "supplier": suppliers[4],
            "supplier_name":"Champ Select 24",
            "plan_type": "fixed",
            "contract_length_months": 24,
            "rate_structure": "fixed",
            "base_rate": Decimal("10.2"),
            "renewable_percentage": Decimal("0"),
            "monthly_fee": Decimal("4.95"),
            "early_termination_fee": Decimal("240"),
            "description": "Lowest rate with 24-month commitment.",
            "regions": TEXAS_ZIP_CODES[:95],
        },
        # Gexa Energy Plans
        {
            "supplier": suppliers[5],
            "supplier_name":"Gexa Saver Supreme 12",
            "plan_type": "fixed",
            "contract_length_months": 12,
            "rate_structure": "fixed",
            "base_rate": Decimal("11.3"),
            "renewable_percentage": Decimal("0"),
            "monthly_fee": Decimal("4.95"),
            "early_termination_fee": Decimal("150"),
            "description": "Simple, affordable electricity with fixed pricing.",
            "regions": TEXAS_ZIP_CODES[:90],
        },
        {
            "supplier": suppliers[5],
            "supplier_name":"Gexa Green 12",
            "plan_type": "fixed",
            "contract_length_months": 12,
            "rate_structure": "fixed",
            "base_rate": Decimal("12.7"),
            "renewable_percentage": Decimal("100"),
            "monthly_fee": Decimal("4.95"),
            "early_termination_fee": Decimal("150"),
            "description": "100% renewable energy at competitive rates.",
            "regions": TEXAS_ZIP_CODES[:75],
        },
        # Frontier Utilities Plans
        {
            "supplier": suppliers[6],
            "supplier_name":"Frontier Secure 12",
            "plan_type": "fixed",
            "contract_length_months": 12,
            "rate_structure": "fixed",
            "base_rate": Decimal("11.6"),
            "renewable_percentage": Decimal("0"),
            "monthly_fee": Decimal("7.95"),
            "early_termination_fee": Decimal("150"),
            "description": "Customer-focused fixed rate with excellent service.",
            "regions": TEXAS_ZIP_CODES[:70],
        },
        {
            "supplier": suppliers[6],
            "supplier_name":"Frontier Green Choice 12",
            "plan_type": "fixed",
            "contract_length_months": 12,
            "rate_structure": "fixed",
            "base_rate": Decimal("13.0"),
            "renewable_percentage": Decimal("100"),
            "monthly_fee": Decimal("7.95"),
            "early_termination_fee": Decimal("150"),
            "description": "100% wind energy with superior customer support.",
            "regions": TEXAS_ZIP_CODES[:65],
        },
        # 4Change Energy Plans
        {
            "supplier": suppliers[7],
            "supplier_name":"Maxx Saver Select 12",
            "plan_type": "fixed",
            "contract_length_months": 12,
            "rate_structure": "fixed",
            "base_rate": Decimal("11.4"),
            "renewable_percentage": Decimal("6"),
            "monthly_fee": Decimal("0"),
            "early_termination_fee": Decimal("150"),
            "description": "Fixed rate with community giving program.",
            "regions": TEXAS_ZIP_CODES[:85],
        },
        {
            "supplier": suppliers[7],
            "supplier_name":"Maxx Saver Select 24",
            "plan_type": "fixed",
            "contract_length_months": 24,
            "rate_structure": "fixed",
            "base_rate": Decimal("10.7"),
            "renewable_percentage": Decimal("6"),
            "monthly_fee": Decimal("0"),
            "early_termination_fee": Decimal("240"),
            "description": "Long-term savings with charitable donations.",
            "regions": TEXAS_ZIP_CODES[:85],
        },
        {
            "supplier": suppliers[7],
            "supplier_name":"Freedom Solar 12",
            "plan_type": "fixed",
            "contract_length_months": 12,
            "rate_structure": "fixed",
            "base_rate": Decimal("12.5"),
            "renewable_percentage": Decimal("100"),
            "monthly_fee": Decimal("0"),
            "early_termination_fee": Decimal("150"),
            "description": "100% solar energy with community impact.",
            "regions": TEXAS_ZIP_CODES[:75],
        },
        # Cirro Energy Plans
        {
            "supplier": suppliers[8],
            "supplier_name":"Simple Rate 12",
            "plan_type": "fixed",
            "contract_length_months": 12,
            "rate_structure": "fixed",
            "base_rate": Decimal("11.8"),
            "renewable_percentage": Decimal("0"),
            "monthly_fee": Decimal("9.95"),
            "early_termination_fee": Decimal("150"),
            "description": "Straightforward fixed rate with no surprises.",
            "regions": TEXAS_ZIP_CODES[:80],
        },
        {
            "supplier": suppliers[8],
            "supplier_name":"Simple Month-to-Month",
            "plan_type": "variable",
            "contract_length_months": 0,
            "rate_structure": "variable",
            "base_rate": Decimal("13.8"),
            "renewable_percentage": Decimal("0"),
            "monthly_fee": Decimal("9.95"),
            "early_termination_fee": Decimal("0"),
            "description": "No commitment, cancel anytime.",
            "regions": TEXAS_ZIP_CODES[:80],
        },
        # Pulse Power Plans
        {
            "supplier": suppliers[9],
            "supplier_name":"Pulse Plus 12",
            "plan_type": "fixed",
            "contract_length_months": 12,
            "rate_structure": "fixed",
            "base_rate": Decimal("12.3"),
            "renewable_percentage": Decimal("0"),
            "monthly_fee": Decimal("9.95"),
            "early_termination_fee": Decimal("150"),
            "description": "Fixed rate with mobile app control.",
            "regions": TEXAS_ZIP_CODES[:85],
        },
        {
            "supplier": suppliers[9],
            "supplier_name":"Pulse Prepaid",
            "plan_type": "prepaid",
            "contract_length_months": 0,
            "rate_structure": "fixed",
            "base_rate": Decimal("13.9"),
            "renewable_percentage": Decimal("0"),
            "monthly_fee": Decimal("0"),
            "early_termination_fee": Decimal("0"),
            "description": "Pay-as-you-go with no deposit or credit check.",
            "regions": TEXAS_ZIP_CODES[:85],
        },
        # Discount Power Plans
        {
            "supplier": suppliers[10],
            "supplier_name":"Budget Saver 12",
            "plan_type": "fixed",
            "contract_length_months": 12,
            "rate_structure": "fixed",
            "base_rate": Decimal("10.5"),
            "renewable_percentage": Decimal("0"),
            "monthly_fee": Decimal("4.95"),
            "early_termination_fee": Decimal("125"),
            "description": "Ultra-low fixed rate for budget shoppers.",
            "regions": TEXAS_ZIP_CODES[:90],
        },
        {
            "supplier": suppliers[10],
            "supplier_name":"Discount Green 12",
            "plan_type": "fixed",
            "contract_length_months": 12,
            "rate_structure": "fixed",
            "base_rate": Decimal("12.4"),
            "renewable_percentage": Decimal("100"),
            "monthly_fee": Decimal("4.95"),
            "early_termination_fee": Decimal("125"),
            "description": "Affordable renewable energy option.",
            "regions": TEXAS_ZIP_CODES[:75],
        },
        # Ambit Energy Plans
        {
            "supplier": suppliers[11],
            "supplier_name":"Ambit Secure 12",
            "plan_type": "fixed",
            "contract_length_months": 12,
            "rate_structure": "fixed",
            "base_rate": Decimal("11.7"),
            "renewable_percentage": Decimal("0"),
            "monthly_fee": Decimal("9.95"),
            "early_termination_fee": Decimal("150"),
            "description": "Fixed rate with customer rewards.",
            "regions": TEXAS_ZIP_CODES[:80],
        },
        {
            "supplier": suppliers[11],
            "supplier_name":"Ambit Eco Rewards 12",
            "plan_type": "fixed",
            "contract_length_months": 12,
            "rate_structure": "fixed",
            "base_rate": Decimal("13.2"),
            "renewable_percentage": Decimal("100"),
            "monthly_fee": Decimal("9.95"),
            "early_termination_fee": Decimal("150"),
            "description": "100% renewable with referral benefits.",
            "regions": TEXAS_ZIP_CODES[:70],
        },
        # Tara Energy Plans
        {
            "supplier": suppliers[12],
            "supplier_name":"Tara Breeze 12",
            "plan_type": "fixed",
            "contract_length_months": 12,
            "rate_structure": "fixed",
            "base_rate": Decimal("11.9"),
            "renewable_percentage": Decimal("0"),
            "monthly_fee": Decimal("4.95"),
            "early_termination_fee": Decimal("150"),
            "description": "Local Texas provider with competitive rates.",
            "regions": TEXAS_ZIP_CODES[:85],
        },
        {
            "supplier": suppliers[12],
            "supplier_name":"Tara Wind Power 12",
            "plan_type": "fixed",
            "contract_length_months": 12,
            "rate_structure": "fixed",
            "base_rate": Decimal("12.6"),
            "renewable_percentage": Decimal("100"),
            "monthly_fee": Decimal("4.95"),
            "early_termination_fee": Decimal("150"),
            "description": "100% Texas wind energy with local support.",
            "regions": TEXAS_ZIP_CODES[:75],
        },
        # Just Energy Plans
        {
            "supplier": suppliers[13],
            "supplier_name":"Just Fixed 12",
            "plan_type": "fixed",
            "contract_length_months": 12,
            "rate_structure": "fixed",
            "base_rate": Decimal("12.4"),
            "renewable_percentage": Decimal("0"),
            "monthly_fee": Decimal("9.95"),
            "early_termination_fee": Decimal("175"),
            "description": "Price protection with fixed rate guarantee.",
            "regions": TEXAS_ZIP_CODES[:75],
        },
        {
            "supplier": suppliers[13],
            "supplier_name":"Just Green 12",
            "plan_type": "fixed",
            "contract_length_months": 12,
            "rate_structure": "fixed",
            "base_rate": Decimal("13.3"),
            "renewable_percentage": Decimal("100"),
            "monthly_fee": Decimal("9.95"),
            "early_termination_fee": Decimal("175"),
            "description": "Green energy with price protection.",
            "regions": TEXAS_ZIP_CODES[:65],
        },
        # Express Energy Plans
        {
            "supplier": suppliers[14],
            "supplier_name":"Express Value 12",
            "plan_type": "fixed",
            "contract_length_months": 12,
            "rate_structure": "fixed",
            "base_rate": Decimal("11.1"),
            "renewable_percentage": Decimal("0"),
            "monthly_fee": Decimal("4.95"),
            "early_termination_fee": Decimal("150"),
            "description": "Great value with transparent pricing.",
            "regions": TEXAS_ZIP_CODES[:85],
        },
        {
            "supplier": suppliers[14],
            "supplier_name":"Express Eco 12",
            "plan_type": "fixed",
            "contract_length_months": 12,
            "rate_structure": "fixed",
            "base_rate": Decimal("12.3"),
            "renewable_percentage": Decimal("100"),
            "monthly_fee": Decimal("4.95"),
            "early_termination_fee": Decimal("150"),
            "description": "Eco-friendly power with simple terms.",
            "regions": TEXAS_ZIP_CODES[:75],
        },
    ]

    plans = []
    for data in plans_data:
        # Create rate_structure JSON based on plan type
        if data["rate_structure"] == "tiered":
            rate_structure = {
                "type": "tiered",
                "tiers": [
                    {"min_kwh": 0, "max_kwh": 500, "rate": float(data["base_rate"]) - 1.0},
                    {"min_kwh": 501, "max_kwh": 1000, "rate": float(data["base_rate"])},
                    {"min_kwh": 1001, "max_kwh": None, "rate": float(data["base_rate"]) + 1.0},
                ]
            }
        elif data["rate_structure"] == "fixed":
            rate_structure = {
                "type": "fixed",
                "rate": float(data["base_rate"])
            }
        elif data["rate_structure"] == "variable":
            rate_structure = {
                "type": "variable",
                "base_rate": float(data["base_rate"]),
                "adjustment_factor": 0.1
            }
        else:
            # Default to fixed
            rate_structure = {
                "type": data["rate_structure"],
                "rate": float(data["base_rate"])
            }

        plan = PlanCatalog(
            id=uuid4(),
            supplier_id=data["supplier"].id,
            plan_name=data["supplier_name"],  # Note: using "supplier_name" key due to global replace
            plan_type=data["plan_type"],
            contract_length_months=data["contract_length_months"],
            rate_structure=rate_structure,
            renewable_percentage=data["renewable_percentage"],
            monthly_fee=data["monthly_fee"],
            early_termination_fee=data["early_termination_fee"],
            connection_fee=Decimal("0"),
            plan_description=data["description"],
            available_regions=data["regions"],
            is_active=True,
            created_at=datetime.utcnow(),
        )
        db.add(plan)
        plans.append(plan)

    db.commit()
    print(f"✓ Created {len(plans)} energy plans")
    return plans


def seed_admin_user(db):
    """Create default admin user."""
    print("Creating admin user...")

    # Check if admin already exists
    existing_admin = db.query(User).filter(User.email == "admin@treebeard.com").first()
    if existing_admin:
        print("⚠ Admin user already exists, skipping...")
        return existing_admin

    admin = User(
        id=uuid4(),
        email="admin@treebeard.com",
        name="Admin User",
        hashed_password=get_password_hash("admin123"),  # CHANGE IN PRODUCTION!
        zip_code="78701",
        property_type="residential",
        consent_given=True,
        is_admin=True,
        is_active=True,
        created_at=datetime.utcnow(),
    )
    db.add(admin)
    db.commit()

    print(f"✓ Created admin user: admin@treebeard.com / admin123")
    print("⚠ IMPORTANT: Change admin password in production!")
    return admin


def seed_demo_user(db):
    """Create demo user for testing."""
    print("Creating demo user...")

    # Check if demo user already exists
    existing_user = db.query(User).filter(User.email == "user@treebeard.com").first()
    if existing_user:
        print("⚠ Demo user already exists, skipping...")
        return existing_user

    user = User(
        id=uuid4(),
        email="user@treebeard.com",
        name="Demo User",
        hashed_password=get_password_hash("user123"),
        zip_code="78701",
        property_type="residential",
        consent_given=True,
        is_admin=False,
        is_active=True,
        created_at=datetime.utcnow(),
    )
    db.add(user)
    db.commit()

    print(f"✓ Created demo user: user@treebeard.com / user123")
    return user


def main():
    """Main seeding function."""
    print("\n" + "="*60)
    print("TreeBeard Database Seeding")
    print("="*60 + "\n")

    # Create database engine - use explicit connection string
    db_url = "postgresql://treebeard:dev_password_123@localhost:5432/treebeard_dev"
    print(f"Connecting to: {db_url}")
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        # Seed in order
        suppliers = seed_suppliers(db)
        plans = seed_plans(db, suppliers)
        admin = seed_admin_user(db)
        demo_user = seed_demo_user(db)

        print("\n" + "="*60)
        print("✓ SEEDING COMPLETE!")
        print("="*60)
        print(f"\nSummary:")
        print(f"  • Suppliers: {len(suppliers)}")
        print(f"  • Plans: {len(plans)}")
        print(f"  • Admin user: admin@treebeard.com")
        print(f"  • Demo user: user@treebeard.com")
        print(f"  • ZIP codes covered: {len(TEXAS_ZIP_CODES)}")
        print(f"\n⚠ Remember to change admin password in production!\n")

    except Exception as e:
        print(f"\n✗ ERROR during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
