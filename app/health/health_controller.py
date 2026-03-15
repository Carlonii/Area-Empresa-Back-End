from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from database import get_db, engine
from config import settings
from web3 import Web3
import sqlalchemy

router = APIRouter(prefix="/health", tags=["Infrastructure"])

@router.get("/")
def get_health(db: Session = Depends(get_db)):
    """
    Infrastructure health check.
    """
    health_status = {
        "status": "healthy",
        "database": "unreachable",
        "blockchain": "unreachable",
        "version": settings.APP_VERSION
    }
    
    # Check Database
    try:
        db.execute(sqlalchemy.text("SELECT 1"))
        health_status["database"] = "reachable"
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["database"] = f"error: {str(e)}"
        
    # Check Blockchain
    try:
        w3 = Web3(Web3.HTTPProvider(settings.WEB3_PROVIDER_URL))
        if w3.is_connected():
            health_status["blockchain"] = "connected"
        else:
            health_status["status"] = "unhealthy"
            health_status["blockchain"] = "disconnected"
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["blockchain"] = f"error: {str(e)}"
        
    return health_status
