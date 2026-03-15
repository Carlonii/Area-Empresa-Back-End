import time
import json
import logging
from web3 import Web3
from sqlalchemy.orm import Session
from database import SessionLocal
from data import data_repository, data_model
from services import pinata_service
from datetime import datetime
from config import settings
from utils import config_repository

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuração da chave para persistência do bloco
LAST_BLOCK_KEY = "indexer_last_synced_block"

def get_contract():
    w3 = Web3(Web3.HTTPProvider(settings.WEB3_PROVIDER_URL))
    if not w3.is_connected():
        logger.error("Falha ao conectar ao provedor Web3")
        return None, None
    
    if not settings.DATA_CONSENT_ADDRESS:
        logger.error("DATA_CONSENT_ADDRESS não configurado")
        return None, None

    try:
        with open(settings.DATA_CONSENT_ABI_PATH, "r", encoding="utf-8") as f:
            abi_data = json.load(f)
            abi = abi_data.get("abi", abi_data) if isinstance(abi_data, dict) else abi_data
        contract = w3.eth.contract(address=Web3.to_checksum_address(settings.DATA_CONSENT_ADDRESS), abi=abi)
        return w3, contract
    except Exception as e:
        logger.error(f"Erro ao carregar contrato: {str(e)}")
        return None, None

def fetch_metadata_with_retry(cid: str, owner: str, retries=3, delay=2):
    for i in range(retries):
        try:
            return pinata_service.get_ipfs_data(cid)
        except Exception as e:
            logger.warning(f"Tentativa {i+1} falhou para CID {cid}: {str(e)}")
            if i < retries - 1:
                time.sleep(delay * (i + 1))
    return None

def process_event(db: Session, event_name: str, event_data: dict):
    tx_hash = event_data['transactionHash'].hex()
    # Check if tx already indexed for this interaction_type
    # (Using tx_hash as unique might block multiple events in same tx if they arise, 
    # but here each event is a separate tx largely. However, let's keep it robust.)
    existing = db.query(data_model.BlockchainConsent).filter_by(tx_hash=tx_hash).first()
    if existing:
        return

    args = event_data['args']
    owner = args.get('owner')
    
    # Map Event to Interaction Type
    interaction_map = {
        "ConsentRegistered": "REGISTERED",
        "AccessGranted": "GRANTED",
        "AccessRevoked": "REVOKED",
        "AccessRequested": "REQUESTED",
        "RequestApproved": "APPROVED"
    }
    
    interaction_type = interaction_map.get(event_name, "UNKNOWN")
    authorized_address = args.get('authorizedUser') or args.get('company') or args.get('revokedUser')
    cid = args.get('dataHash')
    timestamp_raw = args.get('timestamp') or int(time.time()) # Some events might not have timestamp in args depending on ABI

    # For Registration, fetch metadata
    name = None
    email = None
    if event_name == "ConsentRegistered" and cid:
        metadata = fetch_metadata_with_retry(cid, owner)
        if metadata:
            name = metadata.get("name") or metadata.get("full_name")
            email = metadata.get("email")
            # Pin on registration
            try:
                pinata_service.pin_cid(cid, name=f"Consent_{owner}")
            except: pass
    elif event_name != "ConsentRegistered":
        # For non-registration events, we might want to link to the user's latest metadata
        # or just store the interaction. Requirement says "Entity Name (extracted from IPFS metadata)"
        # This implies for history we want the name even for REVOKED events.
        latest_reg = db.query(data_model.BlockchainConsent).filter_by(
            owner_address=owner, interaction_type="REGISTERED"
        ).order_by(data_model.BlockchainConsent.timestamp.desc()).first()
        if latest_reg:
            name = latest_reg.full_name
            email = latest_reg.email
            cid = latest_reg.cid

    consent_in = data_model.BlockchainConsentCreate(
        owner_address=owner,
        cid=cid,
        full_name=name,
        email=email,
        interaction_type=interaction_type,
        authorized_address=authorized_address,
        timestamp=datetime.fromtimestamp(timestamp_raw),
        tx_hash=tx_hash
    )
    
    data_repository.create_consent(db, consent_in)
    logger.info(f"Evento {event_name} indexado: {tx_hash} para {owner}")

def index_events():
    w3, contract = get_contract()
    if not w3 or not contract:
        return

    logger.info("Iniciando indexação de eventos multievento...")
    
    db = SessionLocal()
    try:
        config = config_repository.get_config(db, LAST_BLOCK_KEY)
        last_block = int(config.value) if config else 0
        current_block = w3.eth.block_number
        
        if last_block == 0:
            from_block = max(0, current_block - 1000)
        else:
            from_block = last_block + 1

        if from_block > current_block:
            logger.info("Nenhum bloco novo.")
            return

        to_block = min(current_block, from_block + 5000)
        logger.info(f"Processando blocos {from_block} -> {to_block}")

        # List of events to watch
        event_names = ["ConsentRegistered", "AccessGranted", "AccessRevoked", "AccessRequested", "RequestApproved"]
        
        for event_name in event_names:
            event_instance = getattr(contract.events, event_name)
            events = event_instance.get_logs(fromBlock=from_block, toBlock=to_block)
            for event in events:
                process_event(db, event_name, event)

        config_repository.set_config(db, LAST_BLOCK_KEY, str(to_block))
        logger.info(f"Sincronizado até o bloco {to_block}")

    except Exception as e:
        logger.error(f"Erro na indexação: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    while True:
        index_events()
        time.sleep(settings.INDEXER_POLL_INTERVAL)
