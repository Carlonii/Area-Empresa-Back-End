import logging
import sys
from typing import Any, Optional

def get_logger(name: str) -> logging.Logger:
    """Configures and returns a logger instance."""
    logger = logging.getLogger(name)
    
    # Previne multiplas configuracoes se ja existir handlers
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # Formatter: Timestamp - Nivel - Nome - Mensagem
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # Handler para console (stdout)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # Handler para arquivo de erro (se for um log de exception/erro)
        # file_handler = logging.FileHandler('error.log', encoding='utf-8')
        # file_handler.setFormatter(formatter)
        # file_handler.setLevel(logging.ERROR)
        # logger.addHandler(file_handler)
        
    return logger

def success_response(data: Any = None, message: str = "Operação realizada com sucesso") -> dict:
    """Formata uma resposta padrao de sucesso."""
    response = {
        "status": "success",
        "message": message
    }
    if data is not None:
        response["data"] = data
    return response

def error_response(message: str, data: Optional[Any] = None) -> dict:
    """Formata uma resposta padrao de erro."""
    response = {
        "status": "error",
        "message": message
    }
    if data is not None:
        response["data"] = data
    return response
