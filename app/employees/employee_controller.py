from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from companies import company_service
from auth.employee_auth_service import get_current_employee, require_role
from . import employee_service, employee_model

router = APIRouter(prefix="/companies/{company_id}/employees", tags=["Employees"])


@router.post("/", response_model=employee_model.EmployeePublic, status_code=status.HTTP_201_CREATED)
def create_employee(company_id: str, emp: employee_model.EmployeeCreate, db: Session = Depends(get_db)):
    # Ensure company exists
    company_service.get_company_by_id(db, company_id)
    # Ensure request company_id matches path
    if emp.company_id != company_id:
        emp.company_id = company_id
    return employee_service.create_new_employee(db=db, emp=emp)


@router.get("/", response_model=List[employee_model.EmployeePublic])
def list_employees(company_id: str, db: Session = Depends(get_db), current_employee = Depends(require_role("admin"))):
    # Only admin can list employees for their company
    if current_employee.company_id != company_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return employee_service.employee_repository.list_employees_by_company(db=db, company_id=company_id)


@router.get("/{employee_id}", response_model=employee_model.EmployeePublic)
def get_employee(company_id: str, employee_id: str, db: Session = Depends(get_db), current_employee = Depends(get_current_employee)):
    # Ensure same company
    emp = employee_service.get_employee_by_id(db, employee_id)
    if str(emp.company_id) != str(company_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return emp


@router.put("/{employee_id}", response_model=employee_model.EmployeePublic)
def update_employee(company_id: str, employee_id: str, payload: dict, db: Session = Depends(get_db), current_employee = Depends(get_current_employee)):
    emp = employee_service.get_employee_by_id(db, employee_id)
    if str(emp.company_id) != str(company_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    # Only admin or the employee itself can update
    if not (current_employee.id == emp.id or current_employee.role == 'admin'):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    # If password present, hash it
    if 'password' in payload:
        from security import get_password_hash
        payload['password'] = get_password_hash(payload['password'])
        # repository expects password hashed in 'password' key mapping to password_hash in update
    return employee_service.update_existing_employee(db=db, employee_id=employee_id, employee_in=payload)


@router.delete("/{employee_id}")
def delete_employee(company_id: str, employee_id: str, db: Session = Depends(get_db), current_employee = Depends(require_role('admin'))):
    # Only admin can delete
    if str(current_employee.company_id) != str(company_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return employee_service.delete_employee_by_id(db=db, employee_id=employee_id)

# --- Connection Requests ---

@router.get("/requests/pending")
def list_connection_requests(company_id: str, db: Session = Depends(get_db), current_employee = Depends(require_role('admin'))):
    if str(current_employee.company_id) != str(company_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return employee_service.get_company_connection_requests(db, company_id)

@router.post("/requests/{request_id}/approve")
def approve_request(company_id: str, request_id: str, db: Session = Depends(get_db), current_employee = Depends(require_role('admin'))):
    if str(current_employee.company_id) != str(company_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    req = employee_service.approve_connection_request(db, request_id)
    return {"status": "success", "request": req}

@router.post("/requests/{request_id}/reject")
def reject_request(company_id: str, request_id: str, db: Session = Depends(get_db), current_employee = Depends(require_role('admin'))):
    if str(current_employee.company_id) != str(company_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    req = employee_service.reject_connection_request(db, request_id)
    return {"status": "success", "request": req}
