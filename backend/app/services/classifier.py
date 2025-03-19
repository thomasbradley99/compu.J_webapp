from transformers import pipeline, AutoTokenizer
from typing import List, Dict
import torch
from app.core.config import settings
import numpy as np
import re
from collections import defaultdict

class DocumentClassifier:
    def __init__(self):
        self.model_name = "facebook/bart-large-mnli"
        self.model = pipeline(
            "zero-shot-classification",
            model=self.model_name,
            device=0 if torch.cuda.is_available() else -1
        )
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.categories = settings.CLASSIFICATION_CATEGORIES

    def count_tokens(self, text: str) -> int:
        """Count the number of tokens in a text."""
        return len(self.tokenizer.encode(text))

    def chunk_text(self, text: str, max_length: int = 512) -> List[str]:
        """Split text into chunks, trying to maintain sentence boundaries"""
        sentences = re.split('(?<=[.!?])\s+', text)
        chunks = []
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            sentence_tokens = self.count_tokens(sentence)
            if current_length + sentence_tokens <= max_length:
                current_chunk.append(sentence)
                current_length += sentence_tokens
            else:
                if current_chunk:
                    chunks.append(' '.join(current_chunk))
                current_chunk = [sentence]
                current_length = sentence_tokens
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks

    def extract_document_features(self, text: str, filename: str) -> Dict:
        """Extract key features from document content and metadata"""
        # Filename analysis
        filename_lower = filename.lower()
        
        # Document structure features
        lines = text.split('\n')
        paragraphs = [p for p in text.split('\n\n') if p.strip()]
        
        return {
            # Content-based features
            "avg_paragraph_length": sum(len(p.split()) for p in paragraphs) / len(paragraphs) if paragraphs else 0,
            "code_indicators": len([l for l in lines if l.strip().startswith(('def ', 'class ', 'import ', '# '))]),
            "legal_indicators": len([p for p in paragraphs if any(term in p.lower() for term in ['hereby', 'shall', 'pursuant', 'agreement'])]),
            "academic_indicators": len([p for p in paragraphs if any(term in p.lower() for term in ['abstract', 'methodology', 'conclusion', 'references'])]),
            
            # Metadata features
            "has_technical_filename": any(term in filename_lower for term in ['doc', 'manual', 'guide', 'api', '.py', '.js']),
            "has_legal_filename": any(term in filename_lower for term in ['agreement', 'contract', 'terms', 'policy']),
            "has_academic_filename": any(term in filename_lower for term in ['paper', 'research', 'study', 'thesis']),
            
            # Structure features
            "has_sections": bool(re.findall(r'^[A-Z][^a-z]+:', text, re.MULTILINE)),
            "has_bullet_points": bool(re.findall(r'^\s*[-•*]\s', text, re.MULTILINE))
        }

    def classify_with_features(self, text: str, filename: str) -> Dict:
        """Enhanced classification using both content and document features"""
        features = self.extract_document_features(text, filename)
        
        # Initial classification using BART
        result = self.model(
            text[:512],  # Use first chunk for initial classification
            candidate_labels=self.categories,
            hypothesis_template="This document is a {}.",
            multi_label=True
        )
        
        scores = dict(zip(result["labels"], result["scores"]))
        
        # Adjust scores based on features
        if features["code_indicators"] > 5:
            scores["Technical Documentation"] = max(scores["Technical Documentation"], 0.8)
        
        if features["legal_indicators"] > 3:
            scores["Legal Document"] = max(scores["Legal Document"], 0.75)
            
        if features["academic_indicators"] > 3:
            scores["Academic Paper"] = max(scores["Academic Paper"], 0.75)
            
        if features["has_technical_filename"]:
            scores["Technical Documentation"] *= 1.2
            
        if features["has_legal_filename"]:
            scores["Legal Document"] *= 1.2
            
        if features["has_academic_filename"]:
            scores["Academic Paper"] *= 1.2

        # Normalize scores
        total = sum(scores.values())
        scores = {k: v/total for k, v in scores.items()}

        # Get final prediction
        predicted_category = max(scores.items(), key=lambda x: x[1])[0]
        confidence_score = scores[predicted_category]

        return {
            "predicted_category": predicted_category,
            "confidence_score": confidence_score,
            "category_scores": scores,
            "features": features
        }

    def classify_document(self, text: str, filename: str) -> Dict:
        """Classify a document with proper chunking and score aggregation"""
        total_tokens = self.count_tokens(text)
        
        hypothesis_template = "This text is a {}."
        
        if total_tokens <= 512:
            # Single chunk classification
            result = self.model(
                text,
                candidate_labels=self.categories,
                hypothesis_template=hypothesis_template,
                multi_label=False
            )
            
            return {
                "predicted_category": result["labels"][0],
                "confidence_score": float(result["scores"][0]),
                "category_scores": dict(zip(result["labels"], result["scores"])),
                "token_count": total_tokens,
                "num_chunks": 1
            }
        else:
            # Multi-chunk processing
            chunks = self.chunk_text(text)
            chunk_results = []
            
            for chunk in chunks:
                result = self.model(
                    chunk,
                    candidate_labels=self.categories,
                    hypothesis_template=hypothesis_template,
                    multi_label=False
                )
                chunk_results.append(dict(zip(result["labels"], result["scores"])))
            
            # Aggregate scores across chunks
            aggregated_scores = defaultdict(float)
            for chunk_result in chunk_results:
                for category, score in chunk_result.items():
                    aggregated_scores[category] += score
            
            # Average the scores
            final_scores = {k: v/len(chunks) for k, v in aggregated_scores.items()}
            
            # Get final prediction
            predicted_category = max(final_scores.items(), key=lambda x: x[1])[0]
            
            return {
                "predicted_category": predicted_category,
                "confidence_score": final_scores[predicted_category],
                "category_scores": final_scores,
                "token_count": total_tokens,
                "num_chunks": len(chunks)
            }

    def batch_classify(self, texts: List[str], filenames: List[str]) -> List[Dict]:
        """
        Classify multiple documents in batch.
        
        Args:
            texts: List of document texts
            filenames: List of original filenames
            
        Returns:
            List of classification results
        """
        return [self.classify_document(text, filename) for text, filename in zip(texts, filenames)]

    def get_confidence_level(self, score: float) -> Dict:
        """Enhanced confidence level assessment with recommendations"""
        if score >= settings.CONFIDENCE_THRESHOLDS["high"]:
            return {
                "level": "high",
                "action_needed": False,
                "recommendation": None
            }
        elif score >= settings.CONFIDENCE_THRESHOLDS["medium"]:
            return {
                "level": "medium",
                "action_needed": True,
                "recommendation": "Consider manual review for accuracy"
            }
        else:
            return {
                "level": "low",
                "action_needed": True,
                "recommendation": "Document may need restructuring or manual categorization"
            }

    def handle_low_confidence(self, scores: Dict[str, float], text: str) -> Dict:
        """Enhanced low confidence handling with recommendations"""
        if max(scores.values()) < 0.5:
            return {
                "warning": "Low confidence classification",
                "recommendations": [
                    "Consider manual review",
                    "Document may need restructuring",
                    "Check if document fits any predefined categories"
                ],
                "alternative_categories": sorted(
                    scores.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:2]
            }
        return None 