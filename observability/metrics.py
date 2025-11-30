"""
Metrics Collection - Custom metrics for monitoring.
"""
from collections import defaultdict
from typing import Dict, Any

class MetricsCollector:
    """Collect and track metrics for monitoring."""
    def __init__(self):
        self.counters = defaultdict(int)
        self.histograms = defaultdict(list)
    
    def increment_counter(self, name: str, value: int = 1):
        """Increment a counter metric."""
        self.counters[name] += value
    
    def record_histogram(self, name: str, value: float):
        """Record a value in a histogram."""
        self.histograms[name].append(value)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get all current metrics."""
        return {
            "counters": dict(self.counters),
            "histograms": {
                k: {"avg": sum(v)/len(v) if v else 0, "count": len(v)}
                for k, v in self.histograms.items()
            }
        }
