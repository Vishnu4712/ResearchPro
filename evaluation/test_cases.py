"""
Test Cases - Evaluation test suite.
"""
from typing import Dict, Any, List

class TestCase:
    """Represents a single evaluation test case."""
    def __init__(self, test_id: str, query: str, expected: Dict[str, Any]):
        self.test_id = test_id
        self.query = query
        self.expected_output = expected

TEST_CASES = [
    TestCase("TC001", "What are recent AI breakthroughs?", {"min_sources": 5, "min_quality": 0.8}),
    TestCase("TC002", "Compare solar vs wind energy", {"min_sources": 8, "min_quality": 0.85}),
    TestCase("TC003", "Summarize quantum computing research", {"min_sources": 10, "min_quality": 0.9}),
]
