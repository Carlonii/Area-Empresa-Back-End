import sys
import os

# Ensure app package is in path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from database import SessionLocal
from companies.company_model import Company
from employees.employee_model import Employee, EmployeeCreate
from employees import employee_service
import secrets

def migrate():
    db = SessionLocal()
    companies = db.query(Company).all()
    
    for c in companies:
        if not c.wallet_address:
            print(f"Skipping {c.name} - no wallet address")
            continue
            
        # Check if admin employee already exists
        existing_emp = db.query(Employee).filter(Employee.company_id == c.id, Employee.role == 'admin').first()
        if existing_emp:
            print(f"Skipping {c.name} - admin already exists")
            continue
            
        admin_data = EmployeeCreate(
            company_id=c.id,
            wallet_address=c.wallet_address,
            name=f"Admin {c.name}",
            email=f"admin@{c.domain if c.domain else 'company.com'}",
            password=secrets.token_urlsafe(16),
            role="admin"
        )
        
        try:
            employee_service.create_new_employee(db=db, emp=admin_data)
            print(f"Created admin for {c.name} with wallet {c.wallet_address}")
        except Exception as e:
            print(f"Error for {c.name}: {e}")
            
    db.close()

if __name__ == "__main__":
    migrate()
