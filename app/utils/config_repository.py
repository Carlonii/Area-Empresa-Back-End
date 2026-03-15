# utils/config_repository.py
from sqlalchemy.orm import Session
from . import config_model

def get_config(db: Session, key: str):
    return db.query(config_model.SystemConfig).filter(config_model.SystemConfig.key == key).first()

def set_config(db: Session, key: str, value: str):
    config = get_config(db, key)
    if config:
        config.value = value
    else:
        config = config_model.SystemConfig(key=key, value=value)
        db.add(config)
    db.commit()
    db.refresh(config)
    return config
