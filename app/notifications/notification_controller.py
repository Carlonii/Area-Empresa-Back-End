from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from auth.employee_auth_service import get_current_employee
from . import notification_model
from typing import List

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("/", response_model=List[notification_model.NotificationPublic])
def list_notifications(db: Session = Depends(get_db), current_employee = Depends(get_current_employee)):
    return db.query(notification_model.Notification).filter(
        notification_model.Notification.company_id == current_employee.company_id
    ).order_by(notification_model.Notification.created_at.desc()).all()

@router.put("/{notification_id}/read")
def mark_as_read(notification_id: str, db: Session = Depends(get_db), current_employee = Depends(get_current_employee)):
    notification = db.query(notification_model.Notification).filter(
        notification_model.Notification.id == notification_id,
        notification_model.Notification.company_id == current_employee.company_id
    ).first()
    if notification:
        notification.is_read = True
        db.commit()
    return {"status": "success"}
