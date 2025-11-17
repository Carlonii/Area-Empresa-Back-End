from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
import os
from web3 import Web3

from database import get_db
from auth.employee_auth_service import get_current_employee
from companies import company_repository
from audit_logs import audit_log_service, audit_log_model

router = APIRouter(prefix="/data", tags=["Data"])


class CheckConsentRequest(BaseModel):
    customer_wallet: str


@router.post("/check-consent")
def check_consent(payload: CheckConsentRequest, db: Session = Depends(get_db), current_employee = Depends(get_current_employee)):
    # 1) Identify employee and company
    employee = current_employee
    company = company_repository.get_company(db, employee.company_id)
    if not company:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Employee has no company")

    # 2) Connect to web3 provider
    provider_url = os.getenv("WEB3_PROVIDER_URL", "http://127.0.0.1:8545")
    w3 = Web3(Web3.HTTPProvider(provider_url))
    if not w3.is_connected():
        # log denied
        audit = audit_log_model.AuditLogCreate(
            employee_id=employee.id,
            company_id=company.id,
            customer_wallet=payload.customer_wallet,
            action_type="VERIFICAR_CONSENTIMENTO",
            result="ERROR:CHAIN_UNAVAILABLE"
        )
        audit_log_service.create_log(db=db, log_in=audit)
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Blockchain provider not available")

    # 3) Prepare contract
    abi_path = os.getenv("DATA_CONSENT_ABI_PATH", "app/abi/data_consent_abi.json")
    contract_addr = os.getenv("DATA_CONSENT_ADDRESS")
    if not contract_addr:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="DATA_CONSENT_ADDRESS not configured")

    try:
        import json
        with open(abi_path, "r", encoding="utf-8") as f:
            abi = json.load(f)
        contract = w3.eth.contract(address=Web3.to_checksum_address(contract_addr), abi=abi)

        # call getRecordByOwner
        record = contract.functions.getRecordByOwner(payload.customer_wallet).call()
        # Expectation: record might be a tuple: (cid, authorizedUsers[])
        cid = None
        authorized = []
        if isinstance(record, (list, tuple)) and len(record) >= 2:
            cid = record[0]
            authorized = record[1]
        else:
            # try dict-like
            cid = record.get("cid") if hasattr(record, 'get') else None
            authorized = record.get("authorizedUsers") if hasattr(record, 'get') else []

        # Normalize addresses
        authorized = [Web3.to_checksum_address(a) for a in authorized] if authorized else []
        company_wallet = Web3.to_checksum_address(company.wallet_address)
        status_str = "DENIED"
        if company_wallet in authorized:
            status_str = "AUTHORIZED"

        # Create audit log
        audit = audit_log_model.AuditLogCreate(
            employee_id=employee.id,
            company_id=company.id,
            customer_wallet=payload.customer_wallet,
            action_type="VERIFICAR_CONSENTIMENTO",
            result=status_str
        )
        audit_log_service.create_log(db=db, log_in=audit)

        if status_str == "AUTHORIZED":
            return {"status": "AUTHORIZED", "cid": cid}
        return {"status": "DENIED"}

    except FileNotFoundError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="ABI file not found")
    except Exception as e:
        # log error
        audit = audit_log_model.AuditLogCreate(
            employee_id=employee.id,
            company_id=company.id,
            customer_wallet=payload.customer_wallet,
            action_type="VERIFICAR_CONSENTIMENTO",
            result=f"ERROR:{str(e)}"
        )
        audit_log_service.create_log(db=db, log_in=audit)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
