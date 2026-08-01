"""
Bharat Vanguard News (BVN) — Entity Extractor
Uses spaCy (en_core_web_sm) to extract named entities (People, Organizations, Locations) from text.
"""
import logging
import spacy
from typing import List, Dict

logger = logging.getLogger("nlp.entities")

class EntityExtractor:
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("Loaded spaCy en_core_web_sm model")
        except OSError:
            logger.warning("spaCy en_core_web_sm model not found. Downloading...")
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("Successfully downloaded and loaded spaCy model")
            
        # Mapping spaCy labels to our internal types
        self.LABEL_MAP = {
            "PERSON": "person",
            "ORG": "organization",
            "GPE": "country",          # Map GPE (Geopolitical Entity) to country
            "LOC": "other",            # Map LOC to other
            "NORP": "organization",    # Map NORP (Nationalities/Religious/Political groups) to organization
            "EVENT": "event_type",     # Map EVENT to event_type
            "PRODUCT": "product"
        }

    def extract_entities(self, text: str) -> List[Dict]:
        """
        Extract entities from text and return a deduplicated list of dicts.
        Each dict has 'name', 'type', and 'count' (occurrences).
        """
        if not text or not text.strip():
            return []

        # Increase max_length for long articles if needed, default is 1,000,000 characters
        doc = self.nlp(text)
        
        entities_dict = {}
        for ent in doc.ents:
            mapped_type = self.LABEL_MAP.get(ent.label_)
            if not mapped_type:
                continue
                
            # Clean up entity text (e.g. remove leading/trailing punctuation)
            name = ent.text.strip(" \n\r\t.,;:\"'()[]{}!?-")
            
            # Simple length filters to avoid noise
            if len(name) < 2 or len(name) > 100:
                continue
                
            # Deduplicate by lowercased name + type
            key = f"{name.lower()}::{mapped_type}"
            if key in entities_dict:
                entities_dict[key]["count"] += 1
            else:
                entities_dict[key] = {
                    "name": name,
                    "type": mapped_type,
                    "count": 1
                }
                
        # Return as a list sorted by count descending
        sorted_entities = sorted(entities_dict.values(), key=lambda x: x["count"], reverse=True)
        return sorted_entities

# Singleton instance
_extractor = None

def get_entity_extractor() -> EntityExtractor:
    global _extractor
    if _extractor is None:
        _extractor = EntityExtractor()
    return _extractor
