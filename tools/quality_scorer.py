"""
Quality Scorer - Custom tool for ResearchPro.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import re

class QualityScorerTool:
    """
    Tool for evaluating content quality.
    
    Assesses:
    - Completeness
    - Accuracy indicators
    - Source diversity
    - Clarity and coherence
    - Proper citations
    """
    
    def __init__(self):
        self.name = "evaluate_quality"
        self.description = "Evaluate research content quality"
    
    def score(
        self,
        content: str,
        sources: List[Dict[str, Any]] = None,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Score content quality.
        
        Args:
            content: Text content to evaluate
            sources: List of sources used
            context: Additional context for evaluation
            
        Returns:
            Quality metrics and overall score
        """
        scores = {}
        
        # Completeness (based on length and structure)
        scores["completeness"] = self._score_completeness(content)
        
        # Clarity (based on readability)
        scores["clarity"] = self._score_clarity(content)
        
        # Source diversity (if sources provided)
        if sources:
            scores["source_diversity"] = self._score_source_diversity(sources)
            scores["source_credibility"] = self._score_source_credibility(sources)
        
        # Citation quality
        scores["citations"] = self._score_citations(content)
        
        # Overall score (weighted average)
        weights = {
            "completeness": 0.25,
            "clarity": 0.25,
            "source_diversity": 0.15,
            "source_credibility": 0.20,
            "citations": 0.15
        }
        
        overall = sum(
            scores.get(key, 0.5) * weight
            for key, weight in weights.items()
        )
        
        return {
            "overall_score": round(overall, 2),
            "breakdown": scores,
            "recommendations": self._generate_recommendations(scores)
        }
    
    def _score_completeness(self, content: str) -> float:
        """Score content completeness."""
        word_count = len(content.split())
        
        # Simple heuristic: expect at least 200 words for complete summary
        if word_count >= 200:
            return 1.0
        elif word_count >= 100:
            return 0.7
        elif word_count >= 50:
            return 0.5
        else:
            return 0.3
    
    def _score_clarity(self, content: str) -> float:
        """Score content clarity."""
        # Check for good structure (paragraphs, headers)
        has_paragraphs = "\n\n" in content
        has_headers = "#" in content or "##" in content
        
        # Check sentence length (avoid overly complex sentences)
        sentences = re.split(r'[.!?]+', content)
        avg_sentence_length = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
        
        score = 0.5  # Base score
        
        if has_paragraphs:
            score += 0.2
        if has_headers:
            score += 0.1
        if avg_sentence_length < 25:  # Not too complex
            score += 0.2
        
        return min(score, 1.0)
    
    def _score_source_diversity(self, sources: List[Dict[str, Any]]) -> float:
        """Score source diversity."""
        if not sources:
            return 0.0
        
        # Check for different types of sources
        source_types = set(s.get("database", "unknown") for s in sources)
        
        # More diverse = better
        diversity_score = min(len(source_types) / 3.0, 1.0)
        
        return diversity_score
    
    def _score_source_credibility(self, sources: List[Dict[str, Any]]) -> float:
        """Score average source credibility."""
        if not sources:
            return 0.0
        
        credibility_scores = [
            s.get("credibility_score", 0.5) for s in sources
        ]
        
        return sum(credibility_scores) / len(credibility_scores)
    
    def _score_citations(self, content: str) -> float:
        """Score citation quality."""
        # Look for citation markers
        has_citations = bool(re.search(r'\[\d+\]|\(\d{4}\)|https?://', content))
        
        return 1.0 if has_citations else 0.3
    
    def _generate_recommendations(self, scores: Dict[str, float]) -> List[str]:
        """Generate improvement recommendations."""
        recommendations = []
        
        if scores.get("completeness", 1.0) < 0.7:
            recommendations.append("Add more detail and expand key points")
        
        if scores.get("clarity", 1.0) < 0.7:
            recommendations.append("Improve structure with headers and paragraphs")
        
        if scores.get("source_diversity", 1.0) < 0.6:
            recommendations.append("Include more diverse source types")
        
        if scores.get("citations", 1.0) < 0.7:
            recommendations.append("Add proper citations for claims")
        
        return recommendations if recommendations else ["Quality is good"]