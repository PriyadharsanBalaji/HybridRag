"""Input Validation Utilities"""

from pathlib import Path
from typing import Optional
from config import settings
from loguru import logger


class FileValidator:
    """Validate uploaded files"""
    
    @staticmethod
    def validate_file_type(filename: str) -> bool:
        """Check if file type is supported"""
        file_ext = Path(filename).suffix.lower()
        return file_ext in settings.SUPPORTED_FILE_TYPES
    
    @staticmethod
    def validate_file_size(file_size: int, max_size_mb: int = 50) -> bool:
        """Check if file size is within limits"""
        max_size_bytes = max_size_mb * 1024 * 1024
        return file_size <= max_size_bytes
    
    @staticmethod
    def validate_file(filename: str, file_size: int) -> tuple[bool, Optional[str]]:
        """Validate file type and size"""
        if not FileValidator.validate_file_type(filename):
            return False, f"Unsupported file type. Supported: {', '.join(settings.SUPPORTED_FILE_TYPES)}"
        
        if not FileValidator.validate_file_size(file_size):
            return False, "File size exceeds 50MB limit"
        
        return True, None


class QueryValidator:
    """Validate user queries"""
    
    @staticmethod
    def validate_query(query: str, min_length: int = 3, max_length: int = 1000) -> tuple[bool, Optional[str]]:
        """Validate query string"""
        if not query or not query.strip():
            return False, "Query cannot be empty"
        
        query_length = len(query.strip())
        
        if query_length < min_length:
            return False, f"Query too short (minimum {min_length} characters)"
        
        if query_length > max_length:
            return False, f"Query too long (maximum {max_length} characters)"
        
        return True, None
