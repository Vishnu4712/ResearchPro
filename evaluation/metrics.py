"""
Evaluation Metrics - Quality assessment metrics.
"""
from typing import Dict, Any, List

class EvaluationMetrics:
    """Metrics for evaluating agent performance."""
    
    @staticmethod
    def factual_accuracy(generated: str, truth: str) -> float:
        """Evaluate factual accuracy against ground truth."""
        gen_terms = set(generated.lower().split())
        truth_terms = set(truth.lower().split())
        overlap = len(gen_terms & truth_terms)
        return overlap / len(truth_terms) if truth_terms else 0
    
    @staticmethod
    def citation_completeness(content: str, sources: List[Dict[str, Any]]) -> float:
        """Evaluate citation completeness."""
        import re
        citations = len(re.findall(r'\[\d+\]', content))
        return min(citations / len(sources), 1.0) if sources else 0
