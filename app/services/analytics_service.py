from sqlalchemy.orm import Session
from data import data_repository
from companies import company_repository
from datetime import datetime

def get_growth_percentage(current, previous):
    if previous == 0:
        return 100.0 if current > 0 else 0.0
    return round(((current - previous) / previous) * 100, 2)

def get_global_stats(db: Session):
    # Stats from blockchain consents
    blockchain_stats = data_repository.get_global_stats(db)
    
    # Stats from companies
    total_companies = len(company_repository.list_companies(db))
    
    # Trend Analysis (Month-over-Month Growth)
    now = datetime.utcnow()
    current_month_count = data_repository.get_consents_count_by_month(db, now.year, now.month)
    
    # Calculate previous month
    prev_month = now.month - 1 if now.month > 1 else 12
    prev_year = now.year if now.month > 1 else now.year - 1
    previous_month_count = data_repository.get_consents_count_by_month(db, prev_year, prev_month)
    
    growth = get_growth_percentage(current_month_count, previous_month_count)
    
    return {
        "total_consents": blockchain_stats["total_consents"],
        "active_researchers": blockchain_stats["unique_authorized"], # Unique companies that received access
        "unique_users_with_consent": blockchain_stats["unique_owners"],
        "total_registered_companies": total_companies,
        "growth_percentage": growth,
        "current_month_consents": current_month_count,
        "previous_month_consents": previous_month_count
    }
