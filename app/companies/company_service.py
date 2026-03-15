from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from . import company_repository, company_model

def create_new_company(db: Session, company: company_model.CompanyCreate):
    # Basic uniqueness check for wallet
    existing = company_repository.get_company_by_wallet(db, wallet=company.wallet_address)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Wallet address already registered")
    new_company = company_repository.create_company(db=db, company=company)
    
    # Auto-create the Admin employee for this company
    from employees import employee_service, employee_model
    from security import get_password_hash
    import uuid
    import secrets
    
    admin_emp_data = employee_model.EmployeeCreate(
        company_id=new_company.id,
        wallet_address=new_company.wallet_address,
        name=f"Admin {new_company.name}",
        email=f"admin@{new_company.domain if new_company.domain else 'company.com'}",
        password=secrets.token_urlsafe(16),
        role="admin"
    )
    
    try:
        employee_service.create_new_employee(db=db, emp=admin_emp_data)
    except Exception as e:
        print(f"Error creating admin employee: {e}")
        # Not throwing exception to avoid failing company creation
        
    return new_company

def get_company_by_id(db: Session, company_id: str):
    c = company_repository.get_company(db, company_id)
    if not c:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    return c

def get_company_by_domain(db: Session, domain: str):
    c = company_repository.get_company_by_domain(db, domain)
    if not c:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    return c

def list_all_companies(db: Session):
    return company_repository.list_companies(db)

def delete_company_by_id(db: Session, company_id):
    db_company = company_repository.get_company(db, company_id)
    if not db_company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    return company_repository.delete_company(db=db, db_company=db_company)
