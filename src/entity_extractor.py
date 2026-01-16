"""
Entity Extraction using Transformers (NO COMPILATION NEEDED)
Free NER for Knowledge Graph construction
"""

from typing import List, Dict, Tuple
from transformers import pipeline
from loguru import logger
from config import settings


class EntityExtractor:
    """Extract entities and relationships using Transformers"""
    
    def __init__(self):
        self.model_name = "dslim/bert-base-NER"
        logger.info(f"Loading NER model: {self.model_name}")
        
        try:
            # Use transformers NER pipeline (pre-trained, no compilation)
            self.ner_pipeline = pipeline(
                "ner",
                model=self.model_name,
                aggregation_strategy="simple"
            )
            logger.info("NER model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load NER model: {e}")
            self.ner_pipeline = None
    
    def extract_entities(self, text: str) -> List[Dict[str, any]]:
        """Extract named entities from text"""
        if not self.ner_pipeline:
            return []
        
        try:
            # Limit text length to avoid memory issues
            text = text[:5000]
            
            # Run NER
            results = self.ner_pipeline(text)
            
            entities = []
            for ent in results:
                # Map entity types
                entity_type = self._map_entity_type(ent['entity_group'])
                
                entities.append({
                    "text": ent['word'],
                    "label": entity_type,
                    "start": ent['start'],
                    "end": ent['end'],
                    "score": ent['score']
                })
            
            return entities
            
        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
            return []
    
    def _map_entity_type(self, hf_type: str) -> str:
        """Map HuggingFace entity types to standard types"""
        mapping = {
            'PER': 'PERSON',
            'ORG': 'ORG',
            'LOC': 'LOC',
            'MISC': 'MISC'
        }
        return mapping.get(hf_type, 'UNKNOWN')
    
    def extract_relationships(self, text: str) -> List[Tuple[str, str, str]]:
        """Extract simple relationships (basic implementation)"""
        # Simple keyword-based relationship extraction
        relationships = []
        
        # Extract entities first
        entities = self.extract_entities(text)
        
        if len(entities) < 2:
            return relationships
        
        # Simple rule: if two entities appear close together, they're related
        for i in range(len(entities) - 1):
            entity1 = entities[i]['text']
            entity2 = entities[i + 1]['text']
            
            # Check if they're within 50 characters
            if abs(entities[i]['start'] - entities[i + 1]['start']) < 50:
                relationships.append((entity1, "related_to", entity2))
        
        return relationships[:10]  # Limit to 10 relationships


# Global entity extractor instance
entity_extractor = EntityExtractor()
