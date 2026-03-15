import pytest
from unittest.mock import MagicMock, patch
from services import pinata_service, analytics_service
from data import data_repository
from datetime import datetime
import uuid

def test_get_global_stats_advanced():
    # Mock database
    db = MagicMock()
    
    with patch("data.data_repository.get_global_stats") as mock_blockchain_stats:
        mock_blockchain_stats.return_value = {
            "total_consents": 100,
            "unique_owners": 50,
            "unique_authorized": 15
        }
        
        with patch("companies.company_repository.list_companies") as mock_list_companies:
            mock_list_companies.return_value = [MagicMock()] * 20
            
            with patch("data.data_repository.get_consents_count_by_month") as mock_month_count:
                # current_month = 10, previous_month = 5 => 100% growth
                mock_month_count.side_effect = [10, 5] 
                
                stats = analytics_service.get_global_stats(db)
                
                assert stats["total_consents"] == 100
                assert stats["active_researchers"] == 15
                assert stats["unique_users_with_consent"] == 50
                assert stats["growth_percentage"] == 100.0

def test_growth_percentage_logic():
    from services.analytics_service import get_growth_percentage
    
    assert get_growth_percentage(20, 10) == 100.0
    assert get_growth_percentage(10, 20) == -50.0
    assert get_growth_percentage(10, 0) == 100.0
    assert get_growth_percentage(0, 0) == 0.0

@patch("requests.get")
def test_get_ipfs_data(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"name": "Test User", "email": "test@example.com"}
    mock_get.return_value = mock_response
    
    data = pinata_service.get_ipfs_data("QmTest")
    assert data["name"] == "Test User"
    assert data["email"] == "test@example.com"
