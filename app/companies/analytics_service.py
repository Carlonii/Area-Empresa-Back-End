from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from .data_usage_model import DataUsageStat
from audit_logs.audit_log_model import AuditLog
import uuid

def aggregate_daily_stats(db: Session, company_id: uuid.UUID):
    """Aggregates audit logs into daily stats for a company."""
    # This is a simplified version. In a real system, this would be a background task.
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    
    # Example: Count access approvals
    count = db.query(AuditLog).filter(
        AuditLog.company_id == company_id,
        AuditLog.action_type == "approve_request",
        func.date(AuditLog.timestamp) == yesterday
    ).count()
    
    if count > 0:
        stat = db.query(DataUsageStat).filter(
            DataUsageStat.company_id == company_id,
            DataUsageStat.date == datetime.combine(yesterday, datetime.min.time()),
            DataUsageStat.action_type == "consent_approval"
        ).first()
        
        if not stat:
            stat = DataUsageStat(
                company_id=company_id,
                date=datetime.combine(yesterday, datetime.min.time()),
                action_type="consent_approval",
                count=count
            )
            db.add(stat)
        else:
            stat.count = count
        db.commit()

def get_dashboard_stats(db: Session, company_id: uuid.UUID):
    """Returns aggregated stats for the company dashboard."""
    # Active users (users who granted access)
    # This would involve querying the smart contract or a cached version.
    # For now, let's return counts from AuditLogs as a proxy.
    
    total_requests = db.query(AuditLog).filter(
        AuditLog.company_id == company_id,
        AuditLog.action_type == "request_access"
    ).count()
    
    total_approvals = db.query(AuditLog).filter(
        AuditLog.company_id == company_id,
        AuditLog.action_type == "approve_request"
    ).count()
    
    # Time series data for the last 7 days
    seven_days_ago = datetime.now() - timedelta(days=7)
    time_series = db.query(
        func.date(DataUsageStat.date).label('day'),
        func.sum(DataUsageStat.count).label('total')
    ).filter(
        DataUsageStat.company_id == company_id,
        DataUsageStat.date >= seven_days_ago
    ).group_by('day').order_by('day').all()
    
    return {
        "total_requests": total_requests,
        "total_approvals": total_approvals,
        "approval_rate": (total_approvals / total_requests * 100) if total_requests > 0 else 0,
        "usage_history": [{"date": str(row.day), "count": int(row.total)} for row in time_series]
    }
