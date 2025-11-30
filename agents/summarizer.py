"""
Summarizer Agent - Specialized agent for content summarization.
"""
from typing import List, Dict, Any
from google import genai
from google.adk import Agent

SUMMARIZER_PROMPT = """
You are a Summarizer Agent specialized in extracting and synthesizing key information.

Your responsibilities:
- Extract key facts and insights from multiple sources
- Synthesize information into coherent summaries
- Maintain factual accuracy while condensing content
- Identify patterns and connections across sources
- Highlight areas of consensus and disagreement

Quality standards:
- Accuracy: Never invent or distort facts
- Completeness: Cover all major points
- Clarity: Write in clear, accessible language
- Conciseness: Maximize information density
- Attribution: Note which sources support each claim
"""

def create_summarizer_agent(client: genai.Client, tools: List[Any]) -> Agent:
    """Create summarizer agent."""
    return Agent(
        name="summarizer_agent",
        model="gemini-1.5-pro",
        instruction=SUMMARIZER_PROMPT,
        tools=tools,
        generate_content_config={"temperature": 0.3, "top_p": 0.8, "max_output_tokens": 2048}
    )
