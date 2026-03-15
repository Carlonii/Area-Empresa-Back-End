import os
from typing import List

class Settings:
    def __init__(self):
        # App Settings
        self.APP_NAME = os.getenv("APP_NAME", "Data Consent Proxy API")
        self.APP_VERSION = "0.2.0"
        self.APP_PROFILE = os.getenv("APP_PROFILE", "DEV")
        
        # Database Settings
        self.DATABASE_URL = os.getenv(
            "DATABASE_URL", 
            "postgresql://postgres:1234@localhost/programacaoiii_db"
        )
        
        # Blockchain Settings
        self.WEB3_PROVIDER_URL = os.getenv(
            "WEB3_PROVIDER_URL", 
            "http://127.0.0.1:8545"
        )
        self.DATA_CONSENT_ADDRESS = os.getenv("DATA_CONSENT_ADDRESS", "")
        self.DATA_CONSENT_ABI_PATH = os.getenv(
            "DATA_CONSENT_ABI_PATH", 
            "app/abi/data_consent_abi.json"
        )
        self.INDEXER_POLL_INTERVAL = int(os.getenv("INDEXER_POLL_INTERVAL", "10"))
        
        # IPFS Settings
        self.PINATA_API_KEY = os.getenv("PINATA_API_KEY", "")
        self.PINATA_SECRET_API_KEY = os.getenv("PINATA_SECRET_API_KEY", "")
        self.PINATA_JWT = os.getenv("PINATA_JWT", "")
        self.IPFS_GATEWAY = os.getenv(
            "IPFS_GATEWAY", 
            "https://gateway.pinata.cloud/ipfs/"
        )
        
        # Security Settings
        self.SECRET_KEY = os.getenv("SECRET_KEY", "S3CR3T_K3Y_CH4NG3_M3")
        self.ALGORITHM = "HS256"
        self.ACCESS_TOKEN_EXPIRE_MINUTES = 30
        
        # CORS Settings
        self.ALLOWED_ORIGINS = [
            "http://localhost:5173",
            "http://localhost:5174",
            "https://programacaoiii-front-1.onrender.com",
        ]

settings = Settings()
