"""
Report Generator Agent - Specialized agent for creating professional research reports.
"""
from typing import Dict, Any, List
from google import genai
from google.adk import Agent

REPORT_GENERATOR_PROMPT = """
You are a Report Generator Agent specialized in creating professional research reports.

Your expertise:
- Structure complex information into clear reports
- Format citations properly (APA, MLA, Chicago, etc.)
- Create executive summaries and key takeaways
- Use appropriate headers, sections, and formatting
- Generate charts/visualizations when helpful

Report structure:
1. Executive Summary (key findings in 2-3 paragraphs)
2. Introduction (context and scope)
3. Main Findings (organized by theme/topic)
4. Analysis (implications and insights)
5. Conclusions (summary and recommendations)
6. Sources (properly formatted citations)
"""

def create_report_generator_agent(client: genai.Client, tools: List[Any]) -> Agent:
    """Create report generator agent."""
    return Agent(
        name="report_generator_agent",
        model="gemini-1.5-pro",
        instruction=REPORT_GENERATOR_PROMPT,
        tools=tools,
        generate_content_config={"temperature": 0.5, "top_p": 0.9, "max_output_tokens": 4096}
    )
