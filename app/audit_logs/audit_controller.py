from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from auth.employee_auth_service import get_current_employee
from . import audit_log_service, audit_log_model

router = APIRouter(prefix="/audit", tags=["Audit"])

@router.get("/logs", response_model=list[audit_log_model.AuditLogPublic])
def get_audit_logs(db: Session = Depends(get_db), current_employee = Depends(get_current_employee)):
    # Permite que a empresa autenticada veja os logs da sua própria empresa
    if not current_employee.company_id:
        return []
    return audit_log_service.list_logs_for_company(db=db, company_id=current_employee.company_id)

@router.get("/logs/{customer_wallet}", response_model=list[audit_log_model.AuditLogPublic])
def get_user_logs(customer_wallet: str, db: Session = Depends(get_db)):
    # Convert parameters to checksum to match database entries
    from web3 import Web3
    try:
        checksum_address = Web3.to_checksum_address(customer_wallet)
    except Exception:
        checksum_address = customer_wallet
    return audit_log_service.list_logs_by_wallet(db=db, customer_wallet=checksum_address)
