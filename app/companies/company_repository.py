from sqlalchemy.orm import Session
from . import company_model

def create_company(db: Session, company: company_model.CompanyCreate):
    db_company = company_model.Company(
        name=company.name,
        cnpj=company.cnpj,
        domain=company.domain,
        wallet_address=company.wallet_address
    )
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company

def get_company(db: Session, company_id: str):
    return db.query(company_model.Company).filter(company_model.Company.id == company_id).first()

def get_company_by_wallet(db: Session, wallet: str):
    return db.query(company_model.Company).filter(company_model.Company.wallet_address == wallet).first()

def get_company_by_domain(db: Session, domain: str):
    return db.query(company_model.Company).filter(company_model.Company.domain == domain).first()

def list_companies(db: Session):
    return db.query(company_model.Company).all()

def delete_company(db: Session, db_company: company_model.Company):
    db.delete(db_company)
    db.commit()
    return db_company
