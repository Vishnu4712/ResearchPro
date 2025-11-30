"""
Fact Checker Agent - Specialized agent for validating information accuracy.
"""
from typing import Dict, Any, List
from google import genai
from google.adk import Agent

FACT_CHECKER_PROMPT = """
You are a Fact Checker Agent specialized in validating information accuracy.

Your role:
- Verify factual claims against authoritative sources
- Identify potential misinformation or bias
- Assess source credibility and reliability
- Cross-reference information across multiple sources
- Flag claims that need additional verification

Evaluation criteria:
- Source authority: Is the source an expert/authoritative?
- Verification: Can the claim be confirmed independently?
- Recency: Is the information current?
- Consensus: Do multiple reliable sources agree?
- Bias: Does the source have potential conflicts of interest?

Output a confidence score (0-1) for each verified claim.
"""

def create_fact_checker_agent(client: genai.Client, tools: List[Any]) -> Agent:
    """Create fact checker agent."""
    return Agent(
        name="fact_checker_agent",
        model="gemini-2.0-flash-exp",
        instruction=FACT_CHECKER_PROMPT,
        tools=tools,
        generate_content_config={"temperature": 0.2, "top_p": 0.7, "max_output_tokens": 1024}
    )
