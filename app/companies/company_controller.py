from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from . import company_service, company_model, api_key_service, webhook_service, analytics_service, company_api_key_model, company_webhook_model
from fastapi import HTTPException
from auth.employee_auth_service import get_current_employee

router = APIRouter(prefix="/companies", tags=["Companies"])


from utils.response import success_response

@router.post("/", response_model=None, status_code=status.HTTP_201_CREATED)
def create_company(company: company_model.CompanyCreate, db: Session = Depends(get_db)):
    comp = company_service.create_new_company(db=db, company=company)
    return success_response(data=company_model.CompanyPublic.model_validate(comp).model_dump(), message="Empresa criada com sucesso")


@router.get("/", response_model=None)
def list_companies(db: Session = Depends(get_db)):
    comps = company_service.list_all_companies(db)
    return success_response(data=[company_model.CompanyPublic.model_validate(c).model_dump() for c in comps])

@router.get("/detect", response_model=None)
def detect_company_by_domain(domain: str, db: Session = Depends(get_db)):
    comp = company_service.get_company_by_domain(db, domain)
    if comp:
        return success_response(data=company_model.CompanyPublic.model_validate(comp).model_dump())
    return success_response(data=None, message="Empresa não encontrada para este domínio")


@router.delete("/{company_id}", response_model=None)
def delete_company(company_id: str, db: Session = Depends(get_db)):
    # Load company to return its public representation after deletion
    comp = company_service.get_company_by_id(db, company_id)
    comp_data = company_model.CompanyPublic.model_validate(comp)
    # perform deletion
    company_service.delete_company_by_id(db=db, company_id=company_id)
    return success_response(data=comp_data.model_dump(), message="Empresa removida com sucesso")


@router.get("/dashboard/stats")
def get_company_stats(db: Session = Depends(get_db), current_employee = Depends(get_current_employee)):
    return analytics_service.get_dashboard_stats(db, current_employee.company_id)


@router.get("/api-keys", response_model=List[company_api_key_model.APIKeyPublic])
def list_api_keys(db: Session = Depends(get_db), current_employee = Depends(get_current_employee)):
    return api_key_service.list_company_api_keys(db, current_employee.company_id)


@router.post("/api-keys")
def create_api_key(key_data: company_api_key_model.APIKeyCreate, db: Session = Depends(get_db), current_employee = Depends(get_current_employee)):
    if key_data.company_id != current_employee.company_id:
        raise HTTPException(status_code=403, detail="Not authorized to create keys for this company")
    db_key, raw_key = api_key_service.create_company_api_key(db, key_data.company_id, key_data.name)
    return {"key": raw_key, "prefix": db_key.prefix, "id": db_key.id}


@router.delete("/api-keys/{key_id}", response_model=None)
def revoke_api_key(key_id: str, db: Session = Depends(get_db), current_employee = Depends(get_current_employee)):
    success = api_key_service.revoke_api_key(db, key_id)
    if not success:
        raise HTTPException(status_code=404, detail="API Key not found")
    return success_response(message="API Key revogada com sucesso")


@router.get("/webhooks", response_model=List[company_webhook_model.WebhookPublic])
def list_webhooks(db: Session = Depends(get_db), current_employee = Depends(get_current_employee)):
    return db.query(company_webhook_model.CompanyWebhook).filter(
        company_webhook_model.CompanyWebhook.company_id == current_employee.company_id
    ).all()


@router.post("/webhooks", response_model=company_webhook_model.WebhookPublic)
def create_webhook(webhook_data: company_webhook_model.WebhookCreate, db: Session = Depends(get_db), current_employee = Depends(get_current_employee)):
    if webhook_data.company_id != current_employee.company_id:
        raise HTTPException(status_code=403, detail="Not authorized to create webhooks for this company")
    return webhook_service.create_webhook(db, webhook_data.company_id, str(webhook_data.url), webhook_data.events)
