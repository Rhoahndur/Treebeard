"""
Script to add logo URLs to suppliers in the database.
Run from backend directory: python add_supplier_logos.py
"""
from database.session import SessionLocal
from models.plan import Supplier

# Logo URLs for common Texas energy suppliers
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
    db = SessionLocal()
    try:
        suppliers = db.query(Supplier).all()
        print(f"Found {len(suppliers)} suppliers in database")

        updated_count = 0
        for supplier in suppliers:
            if supplier.supplier_name in LOGO_URLS:
                supplier.logo_url = LOGO_URLS[supplier.supplier_name]
                updated_count += 1
                print(f"✓ Updated logo for: {supplier.supplier_name}")
            else:
                print(f"  No logo mapping for: {supplier.supplier_name}")

        db.commit()
        print(f"\n✅ Successfully updated {updated_count} supplier logos")

    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
