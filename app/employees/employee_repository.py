from sqlalchemy.orm import Session
from . import employee_model
from typing import Optional

def create_employee(db: Session, emp: employee_model.EmployeeCreate, password_hash: str):
    db_emp = employee_model.Employee(
        company_id=emp.company_id,
        name=emp.name,
        email=emp.email,
        password_hash=password_hash,
        role=emp.role
    )
    db.add(db_emp)
    db.commit()
    db.refresh(db_emp)
    return db_emp

def get_employee(db: Session, employee_id: int):
    return db.query(employee_model.Employee).filter(employee_model.Employee.id == employee_id).first()

def get_employee_by_email(db: Session, email: str) -> Optional[employee_model.Employee]:
    return db.query(employee_model.Employee).filter(employee_model.Employee.email == email).first()

def list_employees_by_company(db: Session, company_id: int):
    return db.query(employee_model.Employee).filter(employee_model.Employee.company_id == company_id).all()

def update_employee(db: Session, db_emp: employee_model.Employee, emp_in: dict):
    for key, value in emp_in.items():
        if key == "password":
            # password should be hashed before calling this
            setattr(db_emp, "password_hash", value)
        else:
            setattr(db_emp, key, value)
    db.add(db_emp)
    db.commit()
    db.refresh(db_emp)
    return db_emp

def delete_employee(db: Session, db_emp: employee_model.Employee):
    db.delete(db_emp)
    db.commit()
    return db_emp
