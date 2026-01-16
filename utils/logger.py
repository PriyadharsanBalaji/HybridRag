"""Advanced Logging Configuration"""

import sys
from pathlib import Path
from loguru import logger
from config import settings


class LoggerSetup:
    """Configure application-wide logging"""
    
    @staticmethod
    def setup():
        """Initialize logger"""
        logger.remove()
        
        # Console handler
        logger.add(
            sys.stdout,
            format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
            level=settings.LOG_LEVEL,
            colorize=True
        )
        
        # File handler
        logger.add(
            settings.LOG_FILE,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level=settings.LOG_LEVEL,
            rotation="10 MB",
            retention="30 days",
            compression="zip"
        )
        
        logger.info("Logger initialized")


LoggerSetup.setup()
