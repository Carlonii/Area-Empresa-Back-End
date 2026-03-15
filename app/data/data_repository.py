from sqlalchemy.orm import Session
from . import data_model
from typing import Optional

def create_consent(db: Session, consent: data_model.BlockchainConsentCreate):
    db_consent = data_model.BlockchainConsent(
        owner_address=consent.owner_address,
        cid=consent.cid,
        full_name=consent.full_name,
        email=consent.email,
        interaction_type=consent.interaction_type,
        authorized_address=consent.authorized_address,
        timestamp=consent.timestamp,
        tx_hash=consent.tx_hash
    )
    db.add(db_consent)
    db.commit()
    db.refresh(db_consent)
    return db_consent

def get_consents_by_owner(db: Session, owner_address: str, skip: int = 0, limit: int = 10):
    return db.query(data_model.BlockchainConsent).filter(
        data_model.BlockchainConsent.owner_address == owner_address
    ).order_by(data_model.BlockchainConsent.timestamp.desc()).offset(skip).limit(limit).all()

def get_global_stats(db: Session):
    total_consents = db.query(data_model.BlockchainConsent).filter(
        data_model.BlockchainConsent.interaction_type == "REGISTERED"
    ).count()
    
    unique_owners = db.query(data_model.BlockchainConsent.owner_address).filter(
        data_model.BlockchainConsent.interaction_type == "REGISTERED"
    ).distinct().count()
    
    unique_authorized = db.query(data_model.BlockchainConsent.authorized_address).filter(
        data_model.BlockchainConsent.authorized_address.is_not(None)
    ).distinct().count()
    
    return {
        "total_consents": total_consents,
        "unique_owners": unique_owners,
        "unique_authorized": unique_authorized
    }

def get_consents_count_by_month(db: Session, year: int, month: int):
    from sqlalchemy import extract
    return db.query(data_model.BlockchainConsent).filter(
        data_model.BlockchainConsent.interaction_type == "REGISTERED",
        extract('year', data_model.BlockchainConsent.timestamp) == year,
        extract('month', data_model.BlockchainConsent.timestamp) == month
    ).count()

def get_user_analytics(db: Session, owner_address: str):
    from sqlalchemy import extract
    from datetime import datetime
    
    # Total consents
    total_consents = db.query(data_model.BlockchainConsent).filter(
        data_model.BlockchainConsent.owner_address == owner_address,
        data_model.BlockchainConsent.interaction_type.in_(["REGISTERED", "GRANTED"])
    ).count()

    # Trend Analysis (Month-over-Month Growth)
    now = datetime.utcnow()
    current_month_count = db.query(data_model.BlockchainConsent).filter(
        data_model.BlockchainConsent.owner_address == owner_address,
        data_model.BlockchainConsent.interaction_type.in_(["REGISTERED", "GRANTED"]),
        extract('year', data_model.BlockchainConsent.timestamp) == now.year,
        extract('month', data_model.BlockchainConsent.timestamp) == now.month
    ).count()
    
    # Calculate previous month
    prev_month = now.month - 1 if now.month > 1 else 12
    prev_year = now.year if now.month > 1 else now.year - 1
    previous_month_count = db.query(data_model.BlockchainConsent).filter(
        data_model.BlockchainConsent.owner_address == owner_address,
        data_model.BlockchainConsent.interaction_type.in_(["REGISTERED", "GRANTED"]),
        extract('year', data_model.BlockchainConsent.timestamp) == prev_year,
        extract('month', data_model.BlockchainConsent.timestamp) == prev_month
    ).count()
    
    def get_growth_percentage(current, previous):
        if previous == 0:
            return 100.0 if current > 0 else 0.0
        return round(((current - previous) / previous) * 100, 2)
        
    growth = get_growth_percentage(current_month_count, previous_month_count)

    return {
        "totalConsents": total_consents,
        "monthlyGrowth": growth,
        "harmonyScore": 98, # Mock logical value for now, could be dynamic based on synced nodes
        "securityScore": 94 # Mock logical value for now
    }

def get_pending_requests(db: Session, owner_address: str):
    return db.query(data_model.BlockchainConsent).filter(
        data_model.BlockchainConsent.owner_address == owner_address,
        data_model.BlockchainConsent.interaction_type == "REQUESTED"
    ).all()

def update_consent_status(db: Session, consent_id: str, new_status: str, tx_hash: str = None):
    consent = db.query(data_model.BlockchainConsent).filter(
        data_model.BlockchainConsent.id == consent_id
    ).first()
    if consent:
        consent.interaction_type = new_status
        if tx_hash:
            consent.tx_hash = tx_hash
        db.commit()
        db.refresh(consent)
    return consent
