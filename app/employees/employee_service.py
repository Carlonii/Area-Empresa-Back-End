from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from . import employee_repository, employee_model
from security import get_password_hash, verify_password

def create_new_employee(db: Session, emp: employee_model.EmployeeCreate):
    # Check existing email
    existing = employee_repository.get_employee_by_email(db, email=emp.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    if emp.wallet_address:
        existing_wallet = employee_repository.get_employee_by_wallet_address(db, wallet=emp.wallet_address)
        if existing_wallet:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Wallet already registered")

    hashed = get_password_hash(emp.password) if emp.password else ""
    return employee_repository.create_employee(db=db, emp=emp, password_hash=hashed)

def get_employee_by_id(db: Session, employee_id: int):
    e = employee_repository.get_employee(db, employee_id)
    if not e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    return e

def authenticate_employee(db: Session, email: str, password: str):
    emp = employee_repository.get_employee_by_email(db, email=email)
    if not emp:
        return None
    if not verify_password(password, emp.password_hash):
        return None
    return emp

def update_existing_employee(db: Session, employee_id, employee_in: dict):
    db_emp = employee_repository.get_employee(db, employee_id)
    if not db_emp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    return employee_repository.update_employee(db=db, db_emp=db_emp, emp_in=employee_in)

def delete_employee_by_id(db: Session, employee_id):
    db_emp = employee_repository.get_employee(db, employee_id)
    if not db_emp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    return employee_repository.delete_employee(db=db, db_emp=db_emp)

# --- Connection Requests ---

def request_company_connection(db: Session, employee_id: str, company_id: str):
    # Check if comp exists
    from companies import company_repository
    comp = company_repository.get_company(db, company_id)
    if not comp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    
    # Check if already requested and pending/approved
    requests = employee_repository.get_connection_requests_by_company(db, company_id)
    for r in requests:
        if str(r.employee_id) == str(employee_id) and r.status in ["pending", "approved"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Request already exists or approved")
            
    return employee_repository.create_connection_request(db, employee_id, company_id)

def get_company_connection_requests(db: Session, company_id: str):
    return employee_repository.get_connection_requests_by_company(db, company_id)

def approve_connection_request(db: Session, request_id: str):
    req = employee_repository.get_connection_request(db, request_id)
    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")
    
    req = employee_repository.update_connection_request_status(db, req, "approved")
    # Update employee company
    emp = employee_repository.get_employee(db, req.employee_id)
    if emp:
        employee_repository.update_employee(db, emp, {"company_id": req.company_id})
    return req

def reject_connection_request(db: Session, request_id: str):
    req = employee_repository.get_connection_request(db, request_id)
    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")
    
    return employee_repository.update_connection_request_status(db, req, "rejected")
