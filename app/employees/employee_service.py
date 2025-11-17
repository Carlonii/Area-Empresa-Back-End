from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from . import employee_repository, employee_model
from security import get_password_hash, verify_password

def create_new_employee(db: Session, emp: employee_model.EmployeeCreate):
    # Check existing email
    existing = employee_repository.get_employee_by_email(db, email=emp.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    hashed = get_password_hash(emp.password)
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
