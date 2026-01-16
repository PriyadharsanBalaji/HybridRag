"""
Configuration Management for Hybrid RAG System
Optimized for Gemini Free Tier with Rate Limiting - 2026
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from pydantic_settings import BaseSettings
from pydantic import Field, validator
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Application settings with validation"""
    
    # ===== GEMINI API CONFIGURATION =====
    GOOGLE_API_KEY: Optional[str] = Field(None, env="GOOGLE_API_KEY")
    GEMINI_MODEL: str = Field(
        default="gemini-2.5-flash",
        env="GEMINI_MODEL",
        description="Gemini model (2026 free tier: gemini-2.5-flash)"
    )
    
    # ===== RATE LIMITING (GEMINI FREE TIER) =====
    MAX_REQUESTS_PER_MINUTE: int = Field(default=15, env="MAX_REQUESTS_PER_MINUTE")
    MAX_REQUESTS_PER_DAY: int = Field(default=1500, env="MAX_REQUESTS_PER_DAY")
    MAX_TOKENS_PER_MINUTE: int = Field(default=1000000, env="MAX_TOKENS_PER_MINUTE")
    
    # ===== CHROMA DB CONFIGURATION =====
    CHROMA_PERSIST_DIR: str = Field(default="./data/chroma_db", env="CHROMA_PERSIST_DIR")
    CHROMA_COLLECTION_NAME: str = Field(default="rag_documents", env="CHROMA_COLLECTION_NAME")
    
    # ===== EMBEDDING CONFIGURATION =====
    EMBEDDING_MODEL: str = Field(default="all-MiniLM-L6-v2", env="EMBEDDING_MODEL")
    EMBEDDING_DIMENSION: int = 384
    
    # ===== DOCUMENT PROCESSING =====
    MAX_CHUNK_SIZE: int = Field(default=1000, ge=100, le=2000, env="MAX_CHUNK_SIZE")
    CHUNK_OVERLAP: int = Field(default=200, ge=0, le=500, env="CHUNK_OVERLAP")
    TOP_K_VECTOR_RESULTS: int = Field(default=10, ge=1, le=20, env="TOP_K_VECTOR_RESULTS")
    TOP_K_GRAPH_RESULTS: int = Field(default=5, ge=1, le=10, env="TOP_K_GRAPH_RESULTS")
    SIMILARITY_THRESHOLD: float = Field(default=0.15, ge=0.0, le=1.0, env="SIMILARITY_THRESHOLD")
    
    # ===== KNOWLEDGE GRAPH SETTINGS =====
    ENABLE_KNOWLEDGE_GRAPH: bool = Field(default=True, env="ENABLE_KNOWLEDGE_GRAPH")
    ENTITY_CONFIDENCE_THRESHOLD: float = Field(default=0.75, ge=0.0, le=1.0, env="ENTITY_CONFIDENCE_THRESHOLD")
    MAX_GRAPH_DEPTH: int = Field(default=2, ge=1, le=5, env="MAX_GRAPH_DEPTH")
    
    # ===== LLM SETTINGS =====
    TEMPERATURE: float = Field(default=0.7, ge=0.0, le=1.0, env="TEMPERATURE")
    MAX_OUTPUT_TOKENS: int = Field(default=2048, ge=256, le=8192, env="MAX_OUTPUT_TOKENS")
    TOP_P: float = Field(default=0.95, ge=0.0, le=1.0, env="TOP_P")
    TOP_K: int = Field(default=40, ge=1, le=100, env="TOP_K")
    
    # ===== UI CONFIGURATION =====
    PAGE_TITLE: str = Field(default="Hybrid RAG System", env="PAGE_TITLE")
    PAGE_ICON: str = Field(default="🤖", env="PAGE_ICON")
    LAYOUT: str = Field(default="wide", env="LAYOUT")
    THEME: str = Field(default="dark", env="THEME")
    
    # ===== LOGGING =====
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FILE: str = Field(default="./logs/app.log", env="LOG_FILE")
    
    # ===== CACHE SETTINGS =====
    ENABLE_CACHE: bool = Field(default=True, env="ENABLE_CACHE")
    CACHE_TTL: int = Field(default=3600, env="CACHE_TTL")
    
    # ===== DIRECTORY PATHS =====
    BASE_DIR: Path = Path(__file__).parent
    DATA_DIR: Path = BASE_DIR / "data"
    UPLOADS_DIR: Path = DATA_DIR / "uploads"
    PROCESSED_DIR: Path = DATA_DIR / "processed"
    LOGS_DIR: Path = BASE_DIR / "logs"
    
    # ===== SUPPORTED FILE TYPES =====
    SUPPORTED_FILE_TYPES: List[str] = [
        ".pdf", ".docx", ".txt", ".md", ".csv"
    ]
    
    @validator("CHUNK_OVERLAP")
    def validate_overlap(cls, v, values):
        """Ensure overlap is less than chunk size"""
        if "MAX_CHUNK_SIZE" in values and v >= values["MAX_CHUNK_SIZE"]:
            raise ValueError("CHUNK_OVERLAP must be less than MAX_CHUNK_SIZE")
        return v
    
    @validator("GEMINI_MODEL")
    def validate_gemini_model(cls, v):
        """Validate gemini model selection - 2026 FREE models"""
        valid_models = [
            # 2.5 Generation (RECOMMENDED FREE)
            "gemini-2.5-flash",
            "gemini-2.5-pro",
            "gemini-2.5-flash-lite",
            
            # 2.0 Experimental (FREE)
            "gemini-2.0-flash-exp",
            "gemini-2.0-flash-thinking-exp",
            
            # 1.5 Stable (FREE)
            "gemini-1.5-flash",
            "gemini-1.5-flash-8b",
            "gemini-1.5-pro",
            "gemini-1.5-flash-latest",
            "gemini-1.5-pro-latest",
            
            # Preview models
            "gemini-exp-1206",
            "gemini-exp-1121"
        ]
        if v not in valid_models:
            raise ValueError(f"GEMINI_MODEL must be one of {valid_models}. Got: {v}")
        return v
    
    @validator("THEME")
    def validate_theme(cls, v):
        """Validate theme selection"""
        if v not in ["dark", "light"]:
            raise ValueError("THEME must be 'dark' or 'light'")
        return v
    
    def create_directories(self):
        """Create necessary directories if they don't exist"""
        for directory in [
            self.DATA_DIR,
            self.UPLOADS_DIR,
            self.PROCESSED_DIR,
            self.LOGS_DIR,
            Path(self.CHROMA_PERSIST_DIR)
        ]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def validate_api_key(self) -> bool:
        """Check if API key is configured"""
        return self.GOOGLE_API_KEY is not None and len(self.GOOGLE_API_KEY) > 0
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()
settings.create_directories()

# Warn if API key is missing
if not settings.validate_api_key():
    import warnings
    warnings.warn(
        "\n⚠️  WARNING: GOOGLE_API_KEY not found in .env file!\n"
        "Please:\n"
        "1. Get your FREE API key from: https://makersuite.google.com/app/apikey\n"
        "2. Add it to .env file: GOOGLE_API_KEY=your_key_here\n"
        "3. Restart the application\n",
        UserWarning
    )


# ===== EMBEDDING MODEL CONFIGURATIONS =====
EMBEDDING_MODELS = {
    "all-MiniLM-L6-v2": {
        "dimension": 384,
        "max_seq_length": 256,
        "description": "Fast and efficient, good for most tasks"
    },
    "all-mpnet-base-v2": {
        "dimension": 768,
        "max_seq_length": 384,
        "description": "High quality, slower but more accurate"
    },
    "multi-qa-MiniLM-L6-cos-v1": {
        "dimension": 384,
        "max_seq_length": 512,
        "description": "Optimized for question-answering"
    }
}


# ===== GEMINI MODEL CONFIGURATIONS =====
GEMINI_MODELS = {
    "gemini-2.5-flash": {
        "context_window": 1000000,
        "description": "Latest, fastest, FREE - RECOMMENDED",
        "tier": "free"
    },
    "gemini-2.5-pro": {
        "context_window": 2000000,
        "description": "Most capable 2.5 model, FREE with limits",
        "tier": "free"
    },
    "gemini-1.5-flash": {
        "context_window": 1000000,
        "description": "Stable and reliable, FREE",
        "tier": "free"
    },
    "gemini-1.5-pro": {
        "context_window": 2000000,
        "description": "High capability, FREE with limits",
        "tier": "free"
    }
}
