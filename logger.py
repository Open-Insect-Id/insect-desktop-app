"""
Gestionnaire de logs pour l'application Insect Identifier
"""

import logging
from pathlib import Path
from datetime import datetime

class LogManager:
    def __init__(self, log_dir="logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Créer un logger
        self.logger = logging.getLogger("InsectIdentifier")
        self.logger.setLevel(logging.DEBUG)
        
        # Format
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # File handler
        log_file = self.log_dir / f"insect_identifier_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
    
    def get_logger(self):
        return self.logger

# Instance globale
log_manager = LogManager()
logger = log_manager.get_logger()
