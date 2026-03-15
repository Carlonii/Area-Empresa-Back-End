import requests
from config import settings
import logging

logger = logging.getLogger(__name__)

BASE_URL = "https://api.pinata.cloud"

def get_auth_headers():
    headers = {"Content-Type": "application/json"}
    if settings.PINATA_JWT:
        headers["Authorization"] = f"Bearer {settings.PINATA_JWT}"
    else:
        headers["pinata_api_key"] = settings.PINATA_API_KEY
        headers["pinata_secret_api_key"] = settings.PINATA_SECRET_API_KEY
    return headers

def pin_json_to_ipfs(data: dict):
    """
    Pins JSON data to IPFS using Pinata.
    """
    url = f"{BASE_URL}/pinning/pinJSONToIPFS"
    headers = get_auth_headers()
    
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        return response.json()["IpfsHash"]
    else:
        logger.error(f"Pinata error: {response.text}")
        raise Exception(f"Pinata error: {response.status_code}")

def pin_cid(cid: str, name: str = "ConsentData"):
    """
    Pins an existing CID to Pinata.
    """
    url = f"{BASE_URL}/pinning/pinByHash"
    headers = get_auth_headers()
    
    payload = {
        "hashToPin": cid,
        "pinataMetadata": {"name": name}
    }

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        logger.error(f"Pinata error: {response.text}")
        raise Exception(f"Pinata error: {response.status_code}")

def get_ipfs_data(cid: str):
    """
    Fetches JSON data from IPFS gateway.
    """
    gateway_url = settings.IPFS_GATEWAY
    url = f"{gateway_url}{cid}"
    
    response = requests.get(url, timeout=10)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"IPFS Gateway error: {response.status_code}")
