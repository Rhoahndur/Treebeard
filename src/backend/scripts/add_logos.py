"""
Simple script to add logo URLs to suppliers.
Run from backend directory: python scripts/add_logos.py
"""
import os
from sqlalchemy import create_engine, text

# Get database URL from environment or use default
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://treebeard:dev_password_123@localhost:5432/treebeard_dev"
)

# Logo URLs for Texas energy suppliers
LOGO_URLS = {
    "TXU Energy": "https://logo.clearbit.com/txu.com",
    "Reliant Energy": "https://logo.clearbit.com/reliant.com",
    "Direct Energy": "https://logo.clearbit.com/directenergy.com",
    "Gexa Energy": "https://logo.clearbit.com/gexaenergy.com",
    "Green Mountain Energy": "https://logo.clearbit.com/greenmountainenergy.com",
    "Pulse Power": "https://logo.clearbit.com/pulsepower.com",
    "Champion Energy": "https://logo.clearbit.com/championenergyservices.com",
    "Discount Power": "https://logo.clearbit.com/discountpower.com",
    "First Choice Power": "https://logo.clearbit.com/firstchoicepower.com",
    "Frontier Utilities": "https://logo.clearbit.com/frontierutilities.com",
}

def main():
    engine = create_engine(DATABASE_URL)

    with engine.connect() as conn:
        # Get all suppliers
        result = conn.execute(text("SELECT supplier_name FROM suppliers"))
        suppliers = [row[0] for row in result]
        print(f"Found {len(suppliers)} suppliers in database:")
        for s in suppliers:
            print(f"  - {s}")

        print("\nUpdating logo URLs...")
        updated_count = 0

        for supplier_name, logo_url in LOGO_URLS.items():
            result = conn.execute(
                text("UPDATE suppliers SET logo_url = :logo_url WHERE supplier_name = :name"),
                {"logo_url": logo_url, "name": supplier_name}
            )
            if result.rowcount > 0:
                updated_count += 1
                print(f"✓ Updated logo for: {supplier_name}")
            else:
                print(f"  No match for: {supplier_name}")

        conn.commit()
        print(f"\n✅ Successfully updated {updated_count} supplier logos")

if __name__ == "__main__":
    main()
