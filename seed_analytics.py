import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from database import SessionLocal
from companies.company_model import Company
from companies.data_usage_model import DataUsageStat
from datetime import datetime, timedelta
import random

def seed_analytics():
    db = SessionLocal()
    try:
        company = db.query(Company).first()
        if not company:
            print("No companies found. Please create a company first.")
            return
        
        print(f"Seeding analytics for company: {company.name}")
        
        for i in range(30):
            date = datetime.now() - timedelta(days=i)
            # Create some variety
            count = random.randint(5, 50)
            
            stat = DataUsageStat(
                company_id=company.id,
                date=date,
                action_type="consent_approval",
                count=count
            )
            db.add(stat)
        
        db.commit()
        print("Analytics seeded successfully.")
    except Exception as e:
        print(f"Error seeding analytics: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_analytics()
