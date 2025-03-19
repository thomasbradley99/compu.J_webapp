from transformers import pipeline
from typing import List, Dict
import torch
from app.core.config import settings

class DocumentClassifier:
    def __init__(self):
        self.model = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli",
            device=0 if torch.cuda.is_available() else -1
        )
        self.categories = settings.CLASSIFICATION_CATEGORIES

    def classify_document(self, text: str) -> Dict:
        """
        Classify the document text into predefined categories.
        
        Args:
            text: The text content of the document
            
        Returns:
            Dict containing:
                - predicted_category: The most likely category
                - confidence_score: Confidence score for the prediction
                - confidence_level: Confidence level for the prediction
                - category_scores: Dict of scores for all categories
        """
        # Truncate text if too long
        max_length = 512
        if len(text) > max_length:
            text = text[:max_length] + "..."

        # Perform classification
        result = self.model(
            text,
            candidate_labels=self.categories,
            multi_label=False
        )

        # Determine confidence level
        confidence = result["scores"][0]
        if confidence >= settings.CONFIDENCE_THRESHOLDS["high"]:
            confidence_level = "high"
        elif confidence >= settings.CONFIDENCE_THRESHOLDS["medium"]:
            confidence_level = "medium"
        else:
            confidence_level = "low"

        # Format results
        return {
            "predicted_category": result["labels"][0],
            "confidence_score": confidence,
            "confidence_level": confidence_level,
            "category_scores": dict(zip(result["labels"], result["scores"]))
        }

    def batch_classify(self, texts: List[str]) -> List[Dict]:
        """
        Classify multiple documents in batch.
        
        Args:
            texts: List of document texts
            
        Returns:
            List of classification results
        """
        return [self.classify_document(text) for text in texts] 