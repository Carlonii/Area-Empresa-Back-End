from sqlalchemy.orm import Session
from . import audit_log_model

def create_audit_log(db: Session, log: audit_log_model.AuditLogCreate):
    db_log = audit_log_model.AuditLog(
        employee_id=log.employee_id,
        company_id=log.company_id,
        customer_wallet=log.customer_wallet,
        action_type=log.action_type,
        result=log.result
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

def list_audit_logs_by_company(db: Session, company_id: int):
    return db.query(audit_log_model.AuditLog).filter(audit_log_model.AuditLog.company_id == company_id).all()
def list_audit_logs_by_wallet(db: Session, customer_wallet: str):
    return db.query(audit_log_model.AuditLog).filter(audit_log_model.AuditLog.customer_wallet == customer_wallet).order_by(audit_log_model.AuditLog.timestamp.desc()).all()
