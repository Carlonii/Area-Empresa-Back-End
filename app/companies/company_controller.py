from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from . import company_service, company_model

router = APIRouter(prefix="/companies", tags=["Companies"])


@router.post("/", response_model=company_model.CompanyPublic, status_code=status.HTTP_201_CREATED)
def create_company(company: company_model.CompanyCreate, db: Session = Depends(get_db)):
    return company_service.create_new_company(db=db, company=company)


@router.get("/", response_model=List[company_model.CompanyPublic])
def list_companies(db: Session = Depends(get_db)):
    return company_service.list_all_companies(db)
