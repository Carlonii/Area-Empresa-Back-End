from sqlalchemy.orm import Session
from . import audit_log_repository, audit_log_model

def create_log(db: Session, log_in: audit_log_model.AuditLogCreate):
    return audit_log_repository.create_audit_log(db=db, log=log_in)

def list_logs_for_company(db: Session, company_id: int):
    return audit_log_repository.list_audit_logs_by_company(db=db, company_id=company_id)

def list_logs_by_wallet(db: Session, customer_wallet: str):
    return audit_log_repository.list_audit_logs_by_wallet(db=db, customer_wallet=customer_wallet)
