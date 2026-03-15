import secrets
import hashlib
from datetime import datetime
from sqlalchemy.orm import Session
from .company_api_key_model import CompanyAPIKey
import uuid

def generate_api_key():
    """Generates a random API key and its prefix."""
    key = f"pc_{secrets.token_urlsafe(32)}"
    prefix = key[:7]
    return key, prefix

def hash_key(key: str):
    """Hashes the API key for secure storage."""
    return hashlib.sha256(key.encode()).hexdigest()

def create_company_api_key(db: Session, company_id: uuid.UUID, name: str):
    """Creates a new API key for a company."""
    raw_key, prefix = generate_api_key()
    key_hash = hash_key(raw_key)
    
    db_key = CompanyAPIKey(
        company_id=company_id,
        key_hash=key_hash,
        prefix=prefix,
        name=name
    )
    db.add(db_key)
    db.commit()
    db.refresh(db_key)
    
    return db_key, raw_key

def verify_api_key(db: Session, key: str):
    """Verifies an API key and returns the associated company_id if valid."""
    prefix = key[:7]
    key_hash = hash_key(key)
    
    db_key = db.query(CompanyAPIKey).filter(
        CompanyAPIKey.prefix == prefix,
        CompanyAPIKey.key_hash == key_hash,
        CompanyAPIKey.is_active == True
    ).first()
    
    if db_key:
        db_key.last_used_at = datetime.now()
        db.commit()
        return db_key.company_id
    
    return None

def revoke_api_key(db: Session, key_id: uuid.UUID):
    """Revokes an API key."""
    db_key = db.query(CompanyAPIKey).filter(CompanyAPIKey.id == key_id).first()
    if db_key:
        db_key.is_active = False
        db.commit()
        return True
    return False

def list_company_api_keys(db: Session, company_id: uuid.UUID):
    """Lists all API keys for a company."""
    return db.query(CompanyAPIKey).filter(CompanyAPIKey.company_id == company_id).all()
