from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from employees import employee_service
from security import create_access_token

router = APIRouter()


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/login")
def login_employee(payload: LoginRequest, db: Session = Depends(get_db)):
    emp = employee_service.authenticate_employee(db=db, email=payload.email, password=payload.password)
    if not emp:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")

    token_data = {"sub": emp.email, "role": emp.role, "employee_id": str(emp.id), "company_id": str(emp.company_id)}
    access_token = create_access_token(data=token_data)
    return {"access_token": access_token, "token_type": "bearer"}
