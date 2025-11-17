from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from . import company_repository, company_model

def create_new_company(db: Session, company: company_model.CompanyCreate):
    # Basic uniqueness check for wallet
    existing = company_repository.get_company_by_wallet(db, wallet=company.wallet_address)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Wallet address already registered")
    return company_repository.create_company(db=db, company=company)

def get_company_by_id(db: Session, company_id: int):
    c = company_repository.get_company(db, company_id)
    if not c:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    return c

def list_all_companies(db: Session):
    return company_repository.list_companies(db)
