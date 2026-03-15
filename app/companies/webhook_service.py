import hmac
import hashlib
import json
import httpx
import logging
import secrets
from typing import Any
from sqlalchemy.orm import Session
from .company_webhook_model import CompanyWebhook
import uuid

logger = logging.getLogger(__name__)

async def deliver_webhook(webhook: CompanyWebhook, event_type: str, payload: dict[str, Any]):
    """Delivers a webhook payload to the configured URL."""
    if event_type not in webhook.events:
        return
    
    data = json.dumps({
        "event": event_type,
        "timestamp": str(uuid.uuid4()), # Placeholder for unique ID
        "data": payload
    })
    
    signature = hmac.new(
        webhook.secret.encode(),
        data.encode(),
        hashlib.sha256
    ).hexdigest()
    
    headers = {
        "Content-Type": "application/json",
        "X-Hub-Signature": f"sha256={signature}",
        "User-Agent": "Projeto-V2-Webhook-Deliverer"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(webhook.url, content=data, headers=headers, timeout=5.0)
            response.raise_for_status()
            logger.info(f"Webhook delivered to {webhook.url} for event {event_type}")
        except Exception as e:
            logger.error(f"Failed to deliver webhook to {webhook.url}: {str(e)}")

async def trigger_webhooks(db: Session, company_id: uuid.UUID, event_type: str, payload: dict[str, Any]):
    """Triggers all active webhooks for a company and an event type."""
    webhooks = db.query(CompanyWebhook).filter(
        CompanyWebhook.company_id == company_id,
        CompanyWebhook.is_active == True
    ).all()
    
    import asyncio
    tasks = [deliver_webhook(wh, event_type, payload) for wh in webhooks]
    await asyncio.gather(*tasks)

def create_webhook(db: Session, company_id: uuid.UUID, url: str, events: list[str]):
    """Creates a new webhook configuration."""
    secret = secrets.token_urlsafe(32) # Need to import secrets
    db_webhook = CompanyWebhook(
        company_id=company_id,
        url=url,
        secret=secret,
        events=events
    )
    db.add(db_webhook)
    db.commit()
    db.refresh(db_webhook)
    return db_webhook

# Note: Added secrets import in thought but forgot in code, will fix in next step if needed or just use secrets.token_urlsafe(32)
