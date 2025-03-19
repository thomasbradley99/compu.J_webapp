from transformers import pipeline, AutoTokenizer
from typing import List, Dict
import torch
from app.core.config import settings
import numpy as np

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
        """
        Split text into chunks based on token count.
        Try to split on sentence boundaries when possible.
        """
        # First try to split by paragraphs
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = []
        current_length = 0

        for para in paragraphs:
            para_tokens = self.count_tokens(para)
            
            if para_tokens > max_length:
                # If paragraph is too long, split by sentences
                sentences = para.split('. ')
                for sentence in sentences:
                    sentence_tokens = self.count_tokens(sentence)
                    if current_length + sentence_tokens <= max_length:
                        current_chunk.append(sentence)
                        current_length += sentence_tokens
                    else:
                        # Save current chunk and start new one
                        if current_chunk:
                            chunks.append('. '.join(current_chunk) + '.')
                        current_chunk = [sentence]
                        current_length = sentence_tokens
            else:
                if current_length + para_tokens <= max_length:
                    current_chunk.append(para)
                    current_length += para_tokens
                else:
                    # Save current chunk and start new one
                    chunks.append('\n\n'.join(current_chunk))
                    current_chunk = [para]
                    current_length = para_tokens

        # Don't forget the last chunk
        if current_chunk:
            chunks.append('\n\n'.join(current_chunk))

        return chunks

    def aggregate_results(self, chunk_results: List[Dict]) -> Dict:
        """
        Aggregate classification results from multiple chunks.
        Uses weighted average based on confidence scores.
        """
        # Initialize aggregated scores
        total_scores = {category: 0.0 for category in self.categories}
        total_weight = 0.0

        # Weight each chunk's contribution by its confidence
        for result in chunk_results:
            confidence = result["confidence_score"]
            for category, score in result["category_scores"].items():
                total_scores[category] += score * confidence
            total_weight += confidence

        # Normalize scores
        if total_weight > 0:
            for category in total_scores:
                total_scores[category] /= total_weight

        # Get the highest scoring category
        predicted_category = max(total_scores.items(), key=lambda x: x[1])[0]
        confidence_score = total_scores[predicted_category]

        # Determine confidence level
        if confidence_score >= settings.CONFIDENCE_THRESHOLDS["high"]:
            confidence_level = "high"
        elif confidence_score >= settings.CONFIDENCE_THRESHOLDS["medium"]:
            confidence_level = "medium"
        else:
            confidence_level = "low"

        return {
            "predicted_category": predicted_category,
            "confidence_score": confidence_score,
            "confidence_level": confidence_level,
            "category_scores": total_scores,
            "num_chunks": len(chunk_results),
            "token_count": sum(result.get("token_count", 0) for result in chunk_results)
        }

    def classify_document(self, text: str) -> Dict:
        """
        Classify document text, handling long documents by chunking.
        """
        # Count total tokens
        total_tokens = self.count_tokens(text)
        
        if total_tokens <= 512:
            # For short documents, classify directly
            result = self.model(
                text,
                candidate_labels=self.categories,
                multi_label=False
            )
            
            return {
                "predicted_category": result["labels"][0],
                "confidence_score": result["scores"][0],
                "confidence_level": "high" if result["scores"][0] >= settings.CONFIDENCE_THRESHOLDS["high"]
                                   else "medium" if result["scores"][0] >= settings.CONFIDENCE_THRESHOLDS["medium"]
                                   else "low",
                "category_scores": dict(zip(result["labels"], result["scores"])),
                "token_count": total_tokens,
                "num_chunks": 1
            }
        else:
            # For long documents, chunk and aggregate
            chunks = self.chunk_text(text)
            chunk_results = []
            
            for chunk in chunks:
                result = self.model(
                    chunk,
                    candidate_labels=self.categories,
                    multi_label=False
                )
                chunk_results.append({
                    "predicted_category": result["labels"][0],
                    "confidence_score": result["scores"][0],
                    "category_scores": dict(zip(result["labels"], result["scores"])),
                    "token_count": self.count_tokens(chunk)
                })
            
            return self.aggregate_results(chunk_results)

    def batch_classify(self, texts: List[str]) -> List[Dict]:
        """
        Classify multiple documents in batch.
        
        Args:
            texts: List of document texts
            
        Returns:
            List of classification results
        """
        return [self.classify_document(text) for text in texts] 