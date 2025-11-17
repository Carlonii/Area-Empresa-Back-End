from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from auth.employee_auth_service import get_current_employee, require_role
from . import audit_log_service, audit_log_model

router = APIRouter(prefix="/audit", tags=["Audit"])


@router.get("/logs", response_model=list[audit_log_model.AuditLogPublic])
def get_audit_logs(db: Session = Depends(get_db), current_employee = Depends(require_role("admin"))):
    # current_employee is the admin employee
    company_id = current_employee.company_id
    return audit_log_service.list_logs_for_company(db=db, company_id=company_id)
