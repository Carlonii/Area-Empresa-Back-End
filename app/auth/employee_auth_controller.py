from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from employees import employee_service, employee_repository
from companies import company_repository
from security import create_access_token
from . import employee_auth_service
from .employee_auth_service import get_current_employee
from utils.response import success_response

router = APIRouter(prefix="/auth/employees", tags=["Employee Auth"])

class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/login")
def login_employee(payload: LoginRequest, db: Session = Depends(get_db)):
    emp = employee_service.authenticate_employee(db=db, email=payload.email, password=payload.password)
    if not emp:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")

    token_data = {"sub": emp.email, "role": emp.role, "employee_id": str(emp.id), "company_id": str(emp.company_id) if emp.company_id else ""}
    access_token = create_access_token(data=token_data)
    return success_response(data={"access_token": access_token, "token_type": "bearer"}, message="Login realizado com sucesso")


class WalletLoginRequest(BaseModel):
    wallet_address: str

@router.post("/wallet-login")
def wallet_login_employee(payload: WalletLoginRequest, db: Session = Depends(get_db)):
    from employees import employee_repository
    emp = employee_repository.get_employee_by_wallet_address(db, payload.wallet_address)
    
    if not emp:
        # Check if it matches a company wallet instead
        comp = company_repository.get_company_by_wallet(db, payload.wallet_address)
        if comp:
            # It's a company wallet, not an employee wallet. The frontend will handle this redirect.
            return {"status": "company_match", "company_id": str(comp.id)}
            
        return {"status": "not_found"}
        
    token_data = {"sub": emp.email, "role": emp.role, "employee_id": str(emp.id), "company_id": str(emp.company_id) if emp.company_id else ""}
    access_token = create_access_token(data=token_data)
    return success_response(data={
        "access_token": access_token, 
        "token_type": "bearer",
        "has_company": emp.company_id is not None
    }, message="Login via wallet realizado com sucesso")


@router.post("/register")
def register_employee_without_company(payload: employee_service.employee_model.EmployeeCreate, db: Session = Depends(get_db)):
    # Create employee. Company ID can be null.
    emp = employee_service.create_new_employee(db, payload)
    
    # Auto login
    token_data = {"sub": emp.email, "role": emp.role, "employee_id": str(emp.id), "company_id": ""}
    access_token = create_access_token(data=token_data)
    return success_response(data={
        "access_token": access_token, 
        "token_type": "bearer",
        "employee": emp
    }, message="Funcionário registrado com sucesso")


@router.get("/me")
def get_current_user_info(db: Session = Depends(get_db), current_employee = Depends(get_current_employee)):
    """
    Retorna informações do funcionário autenticado e da empresa associada
    """
    # Busca informações da empresa se existir
    company = None
    if current_employee.company_id:
        company = company_repository.get_company(db, current_employee.company_id)
    
    return success_response(data={
        "employee": {
            "id": current_employee.id,
            "email": current_employee.email,
            "role": current_employee.role,
            "company_id": current_employee.company_id
        },
        "company": {
            "id": company.id,
            "name": company.name,
            "wallet_address": company.wallet_address
        } if company else None
    }, message="Informações do usuário carregadas")

class ConnectionRequestPayload(BaseModel):
    company_id: str

@router.post("/request-connection")
def request_connection_to_company(payload: ConnectionRequestPayload, db: Session = Depends(get_db), current_employee = Depends(get_current_employee)):
    if current_employee.company_id:
        raise HTTPException(status_code=400, detail="Employee already linked to a company")
        
    req = employee_service.request_company_connection(db, str(current_employee.id), payload.company_id)
    return success_response(data={"request_id": str(req.id)}, message="Solicitação de vínculo criada com sucesso")
