"""
Search Agent - Specialized agent for information retrieval.

This agent performs intelligent searches across multiple sources:
- Web search via Google Search
- Academic search via custom MCP tool
- Query optimization and reformulation
- Result ranking and deduplication
"""

from typing import List, Dict, Any
from google import genai
from google.adk import Agent


SEARCH_AGENT_PROMPT = """
You are a Search Agent specialized in finding high-quality information sources.

Your expertise includes:

## Search Strategy:
- Formulate effective search queries from natural language questions
- Use advanced search operators when appropriate
- Identify the most relevant sources quickly
- Diversify sources (academic, news, expert analysis, etc.)

## Quality Assessment:
- Prioritize credible sources (peer-reviewed, authoritative)
- Check publication dates for currency
- Identify potential bias or conflicts of interest
- Verify author credentials when possible

## Tools Available:
- **Google Search**: General web search for recent information
- **Academic Search**: Specialized search for scholarly articles (arXiv, PubMed, etc.)

## Output Format:
For each source you find, provide:
1. URL and title
2. Brief summary of relevant content
3. Source credibility assessment (1-5 stars)
4. Publication date
5. Why this source is relevant to the query

Focus on quality over quantity. Better to have 5 excellent sources than 20 mediocre ones.
"""


def create_search_agent(
    client: genai.Client,
    tools: List[Any]
) -> Agent:
    """
    Create a specialized search agent.
    
    Args:
        client: Gemini client
        tools: List of search tools (Google Search, Academic Search, etc.)
        
    Returns:
        Configured search agent
    """
    search_agent = Agent(
        name="search_agent",
        model="gemini-2.0-flash-exp",
        instruction=SEARCH_AGENT_PROMPT,
        tools=tools,
        generate_content_config={
            "temperature": 0.4,  # Moderate creativity for query reformulation
            "top_p": 0.9,
            "top_k": 40,
            "max_output_tokens": 1024,
        }
    )
    
    return search_agent


# Utility functions for search optimization
def optimize_search_query(query: str, search_type: str = "general") -> str:
    """
    Optimize search query based on type.
    
    Args:
        query: Original query
        search_type: Type of search (general, academic, news)
        
    Returns:
        Optimized query string
    """
    if search_type == "academic":
        # Add academic-focused terms
        return f"{query} research study peer-reviewed"
    elif search_type == "news":
        # Add recency indicators
        return f"{query} latest recent 2024"
    else:
        return query


def rank_search_results(
    results: List[Dict[str, Any]],
    quality_weights: Dict[str, float] = None
) -> List[Dict[str, Any]]:
    """
    Rank search results by quality indicators.
    
    Args:
        results: List of search results
        quality_weights: Weights for different quality factors
        
    Returns:
        Ranked list of results
    """
    if quality_weights is None:
        quality_weights = {
            "credibility": 0.4,
            "relevance": 0.3,
            "recency": 0.2,
            "depth": 0.1
        }
    
    # Score each result
    for result in results:
        score = 0.0
        
        # Add scoring logic based on metadata
        if "credibility" in result:
            score += result["credibility"] * quality_weights["credibility"]
        if "relevance" in result:
            score += result["relevance"] * quality_weights["relevance"]
        if "recency" in result:
            score += result["recency"] * quality_weights["recency"]
        if "depth" in result:
            score += result["depth"] * quality_weights["depth"]
        
        result["quality_score"] = score
    
    # Sort by quality score
    return sorted(results, key=lambda x: x.get("quality_score", 0), reverse=True)
