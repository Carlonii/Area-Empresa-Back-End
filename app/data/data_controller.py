from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
import os
from web3 import Web3

from database import get_db
from auth.employee_auth_service import get_current_employee
from companies import company_repository
from audit_logs import audit_log_service, audit_log_model
from data import data_model, data_repository
from services import pinata_service, analytics_service
from typing import List

router = APIRouter(prefix="/data", tags=["Data"])


class CheckConsentRequest(BaseModel):
    customer_wallet: str


@router.post("/check-consent")
def check_consent(payload: CheckConsentRequest, db: Session = Depends(get_db), current_employee = Depends(get_current_employee)):
    employee = None
    company = None
    
    try:
        # 1) Identify employee and company
        employee = current_employee
        company = company_repository.get_company(db, employee.company_id)
        if not company:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Employee has no company")
        
        # Verify company has wallet address
        if not company.wallet_address:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Company has no wallet address configured")

        # 2) Connect to web3 provider
        provider_url = os.getenv("WEB3_PROVIDER_URL", "http://127.0.0.1:8545")
        w3 = Web3(Web3.HTTPProvider(provider_url))
        if not w3.is_connected():
            # log denied - incluindo endereços das carteiras para debug
            error_detail = f"CHAIN_UNAVAILABLE - Empresa: {company.wallet_address}, Cliente: {payload.customer_wallet}"
            audit = audit_log_model.AuditLogCreate(
                employee_id=employee.id,
                company_id=company.id,
                customer_wallet=payload.customer_wallet,
                action_type="VERIFICAR_CONSENTIMENTO",
                result=error_detail
            )
            audit_log_service.create_log(db=db, log_in=audit)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
                detail=f"Blockchain provider not available. Company wallet: {company.wallet_address}, Customer wallet: {payload.customer_wallet}"
            )

        # 3) Prepare contract
        abi_path = os.getenv("DATA_CONSENT_ABI_PATH", "app/abi/data_consent_abi.json")
        contract_addr = os.getenv("DATA_CONSENT_ADDRESS")
        if not contract_addr:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="DATA_CONSENT_ADDRESS not configured")

        import json
        with open(abi_path, "r", encoding="utf-8") as f:
            abi_data = json.load(f)
            abi = abi_data.get("abi", abi_data) if isinstance(abi_data, dict) else abi_data
        contract = w3.eth.contract(address=Web3.to_checksum_address(contract_addr), abi=abi)

        # call getRecordByOwner
        # Convert customer wallet to checksum address
        customer_wallet_checksum = Web3.to_checksum_address(payload.customer_wallet)
        record = contract.functions.getRecordByOwner(customer_wallet_checksum).call()
        
        # Return format: (dataHash, owner, authorizedUsers[], timestamp, active)
        cid = None
        authorized = []
        if isinstance(record, (list, tuple)) and len(record) >= 5:
            cid = record[0]  # dataHash
            authorized = record[2]  # authorizedUsers (index 2, not 1)
        else:
            # try dict-like
            cid = record.get("dataHash") if hasattr(record, 'get') else None
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
    except Exception as e:
        import logging
        logging.error("Exception in check_consent: ", exc_info=True)
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/history/{address}", response_model=List[data_model.BlockchainConsentPublic])
def get_consent_history(address: str, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    Returns indexed consent history for a specific wallet address with pagination.
    """
    checksum_address = Web3.to_checksum_address(address)
    return data_repository.get_consents_by_owner(db, checksum_address, skip=skip, limit=limit)

@router.get("/analytics")
def get_global_analytics(db: Session = Depends(get_db)):
    """
    Returns global statistics for the dashboard.
    """
    return analytics_service.get_global_stats(db)

@router.get("/user-analytics/{address}")
def get_user_analytics_endpoint(address: str, db: Session = Depends(get_db)):
    """
    Returns user-specific statistics for the user dashboard.
    """
    checksum_address = Web3.to_checksum_address(address)
    return data_repository.get_user_analytics(db, checksum_address)

class StatusUpdateRequest(BaseModel):
    status: str
    tx_hash: str = None

@router.get("/requests/pending/{address}", response_model=List[data_model.BlockchainConsentPublic])
def get_pending_requests_endpoint(address: str, db: Session = Depends(get_db)):
    """
    Returns a list of pending requests for a user.
    """
    checksum_address = Web3.to_checksum_address(address)
    return data_repository.get_pending_requests(db, checksum_address)

@router.post("/requests/{consent_id}/status", response_model=data_model.BlockchainConsentPublic)
def update_request_status(consent_id: str, payload: StatusUpdateRequest, db: Session = Depends(get_db)):
    """
    Updates the status of a request after handling via blockhain.
    """
    consent = data_repository.update_consent_status(db, consent_id, payload.status, payload.tx_hash)
    if not consent:
        raise HTTPException(status_code=404, detail="Request not found")
    return consent

@router.post("/pin/{cid}")
def pin_ipfs_cid(cid: str, current_employee = Depends(get_current_employee)):
    """
    Manually pins a CID to Pinata.
    """
    try:
        result = pinata_service.pin_cid(cid)
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/profile/{address}", response_model=data_model.BlockchainConsentPublic)
def get_user_profile_cache(address: str, db: Session = Depends(get_db)):
    """
    Returns the latest metadata for a wallet address from cache.
    """
    history = data_repository.get_consents_by_owner(db, address)
    if not history:
        raise HTTPException(status_code=404, detail="Profile not found in cache")
    return history[0]
