"""
Document Processing and Chunking
Supports: PDF, DOCX, TXT, MD, CSV, XLSX, PPTX, HTML
"""

import re
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass

# Document loaders
from langchain_community.document_loaders import (
    PyPDFLoader, Docx2txtLoader, TextLoader,
    UnstructuredMarkdownLoader, CSVLoader,
    UnstructuredExcelLoader, UnstructuredPowerPointLoader,
    UnstructuredHTMLLoader
)
# FIXED IMPORT - Updated path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from loguru import logger
from config import settings
from utils.helpers import calculate_file_hash, clean_text


@dataclass
class DocumentChunk:
    """Represents a processed document chunk"""
    content: str
    metadata: Dict[str, Any]
    chunk_id: str
    embedding: List[float] = None


class DocumentProcessor:
    """Process and chunk documents"""
    
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.MAX_CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        logger.info("DocumentProcessor initialized")
    
    def load_document(self, file_path: Path) -> List[Dict[str, Any]]:
        """Load document based on file type"""
        file_ext = file_path.suffix.lower()
        
        loaders = {
            '.pdf': PyPDFLoader,
            '.docx': Docx2txtLoader,
            '.txt': TextLoader,
            '.md': UnstructuredMarkdownLoader,
            '.csv': CSVLoader,
            '.xlsx': UnstructuredExcelLoader,
            '.pptx': UnstructuredPowerPointLoader,
            '.html': UnstructuredHTMLLoader
        }
        
        loader_class = loaders.get(file_ext)
        if not loader_class:
            raise ValueError(f"Unsupported file type: {file_ext}")
        
        try:
            loader = loader_class(str(file_path))
            documents = loader.load()
            logger.info(f"Loaded {len(documents)} pages from {file_path.name}")
            return documents
        except Exception as e:
            logger.error(f"Error loading document {file_path.name}: {e}")
            raise
    
    def process_document(self, file_path: Path) -> List[DocumentChunk]:
        """Load, chunk, and process document"""
        try:
            # Load document
            documents = self.load_document(file_path)
            
            # Calculate file hash
            file_hash = calculate_file_hash(file_path)
            
            # Split into chunks
            chunks = []
            for doc_idx, doc in enumerate(documents):
                # Clean text
                cleaned_text = clean_text(doc.page_content)
                
                # Split into chunks
                text_chunks = self.text_splitter.split_text(cleaned_text)
                
                for chunk_idx, chunk_text in enumerate(text_chunks):
                    chunk_id = f"{file_hash}_{doc_idx}_{chunk_idx}"
                    
                    metadata = {
                        "source": file_path.name,
                        "file_path": str(file_path),
                        "file_hash": file_hash,
                        "page": doc_idx + 1,
                        "chunk_index": chunk_idx,
                        "chunk_id": chunk_id,
                        **doc.metadata
                    }
                    
                    chunks.append(DocumentChunk(
                        content=chunk_text,
                        metadata=metadata,
                        chunk_id=chunk_id
                    ))
            
            logger.info(f"Processed {len(chunks)} chunks from {file_path.name}")
            return chunks
            
        except Exception as e:
            logger.error(f"Error processing document: {e}")
            raise


# Global document processor instance
document_processor = DocumentProcessor()
