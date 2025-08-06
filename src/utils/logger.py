# ============================================================================
# FILE: src/utils/logger.py
# Logging configuration
# ============================================================================

import logging
import sys
from datetime import datetime
import os

def setup_logging(log_level: str = "INFO"):
    """Setup application logging"""
    
    # Create logs directory
    os.makedirs("logs", exist_ok=True)
    
    # Configure logging format
    log_format = "%(asctime)s | %(levelname)8s | %(name)s | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        datefmt=date_format,
        handlers=[
            # Console handler
            logging.StreamHandler(sys.stdout),
            # File handler
            logging.FileHandler(
                f"logs/mindfulmate_{datetime.now().strftime('%Y%m%d')}.log"
            )
        ]
    )
    
    # Set specific logger levels
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    
    # Create application logger
    logger = logging.getLogger("mindfulmate")
    logger.info("[READY] Logging initialized")
    
    return logger
