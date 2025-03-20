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
        
        # Adjust hypothesis templates to be more specific
        self.hypothesis_templates = {
            "Technical Documentation": "This text is {} that explains how to use or implement technical systems",
            "Business Proposal": "This text is {} that promotes or proposes a product, service, or business opportunity",
            "Legal Document": "This text is {} that establishes legal terms or requirements",
            "Academic Paper": "This text is {} that presents formal research findings or academic analysis",
            "General Article": "This text is {} that shares experiences, opinions, or general information",
            "Other": "This text is {}"
        }
        
        # Expand indicators for better classification
        self.category_indicators = {
            "Technical Documentation": ["guide", "documentation", "manual", "reference", "tutorial", "function", "class", "api", "code"],
            "Business Proposal": ["proposal", "executive summary", "business plan", "pitch", "investment", "market"],
            "Legal Document": ["agreement", "terms", "contract", "policy", "hereby", "pursuant", "parties"],
            "General Article": ["how i", "why is", "opinion", "blog", "story", "experience", "thoughts"],
            "Academic Paper": ["abstract", "methodology", "conclusion", "research", "study", "analysis"],
            "Business Proposal": [
                "revolutionize", "transform", "innovative", "solution", 
                "product", "service", "opportunity", "benefits",
                "!",  # Exclamation marks often indicate promotional content
                "are you tired of", "introducing", "discover"
            ]
        }

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
        
        # Get first non-empty line as title
        title = next((line.strip() for line in lines if line.strip()), '')
        title_lower = title.lower()
        
        features = {
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
            "has_bullet_points": bool(re.findall(r'^\s*[-•*]\s', text, re.MULTILINE)),
            
            # Title-based features
            "has_technical_title": any(term in title_lower for term in self.category_indicators["Technical Documentation"]),
            "has_business_title": any(term in title_lower for term in self.category_indicators["Business Proposal"]),
            "has_legal_title": any(term in title_lower for term in self.category_indicators["Legal Document"]),
            "has_article_title": any(term in title_lower for term in self.category_indicators["General Article"]),
            "is_first_person": any(term in title_lower for term in ["i ", "my ", "how i", "why i"]),
            "has_question": "?" in title or title.lower().startswith(("how", "why", "what", "when")),
        }

        return features

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
        features = self.extract_document_features(text, filename)
        token_count = self.count_tokens(text)
        chunks = self.chunk_text(text) if token_count > 512 else [text]
        num_chunks = len(chunks)
        
        # Initial classification
        results = []
        for category in self.categories:
            result = self.model(
                text[:512],
                candidate_labels=[category],
                hypothesis_template=self.hypothesis_templates[category],
                multi_label=False
            )
            results.append((category, result["scores"][0]))
        
        scores = dict(results)
        
        # Adjust scores based on features
        if features["has_technical_title"] or features["code_indicators"] > 2:
            scores["Technical Documentation"] *= 1.8
            scores["Legal Document"] *= 0.7  # Reduce legal bias for technical content
        
        if features["is_first_person"] or features["has_question"]:
            scores["General Article"] *= 2.0
            scores["Legal Document"] *= 0.5  # Significantly reduce legal bias for article-like content
        
        if features["legal_indicators"] > 2:
            scores["Legal Document"] *= 1.5  # Only boost legal if strong indicators
        
        if features["academic_indicators"] > 2:
            scores["Academic Paper"] *= 1.8
            scores["Legal Document"] *= 0.7
        
        # Check for article indicators in title
        title_words = filename.lower().split()
        if any(word in ["how", "why", "what", "when", "blog", "opinion"] for word in title_words):
            scores["General Article"] *= 2.0
            scores["Legal Document"] *= 0.4
        
        # Add specific adjustments for marketing content
        first_paragraph = text.split('\n\n')[0].lower()
        if any(indicator in first_paragraph.lower() for indicator in [
            "revolutionize", "transform", "are you", "introducing", "discover"
        ]):
            scores["Business Proposal"] *= 2.0
            scores["Academic Paper"] *= 0.5

        # Stronger boost for first-person articles
        if "how i" in filename.lower() or "why i" in filename.lower():
            scores["General Article"] *= 2.5
            scores["Academic Paper"] *= 0.3
            scores["Technical Documentation"] *= 0.7

        # Handle mixed-content documents
        content_indicators = {
            "technical": ["implementation", "system", "algorithm"],
            "business": ["proposal", "opportunity", "market"],
            "academic": ["research", "study", "analysis"],
            "legal": ["compliance", "regulation", "policy"]
        }
        
        indicator_counts = {k: sum(1 for ind in v if ind in text.lower()) 
                          for k, v in content_indicators.items()}
        
        if sum(count > 2 for count in indicator_counts.values()) >= 3:
            # If document has significant indicators from 3+ categories
            scores["Other"] *= 1.5

        # Normalize scores
        total = sum(scores.values())
        normalized_scores = {k: v/total for k, v in scores.items()}
        
        predicted_category = max(normalized_scores.items(), key=lambda x: x[1])[0]
        confidence = normalized_scores[predicted_category]
        
        return {
            "predicted_category": predicted_category,
            "confidence_score": confidence,
            "category_scores": normalized_scores,
            "token_count": token_count,
            "num_chunks": num_chunks
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