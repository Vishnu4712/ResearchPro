"""
Orchestrator Agent - Main coordination agent for ResearchPro.

This agent coordinates the multi-agent research workflow:
- Routes requests to appropriate specialized agents
- Manages sequential and parallel execution
- Aggregates results from multiple agents
- Handles error recovery and retry logic
"""

from typing import Dict, Any, List, Optional
from google import genai
from google.adk import Agent


ORCHESTRATOR_PROMPT = """
You are the Orchestrator Agent for ResearchPro, an intelligent research assistant system.

Your role is to coordinate multiple specialized agents to perform comprehensive research:

1. **Search Agents**: Parallel execution to find information from multiple sources
2. **Fact Checker Agent**: Validate information accuracy and credibility
3. **Summarizer Agent**: Extract key insights and synthesize information
4. **Report Generator Agent**: Create well-formatted, comprehensive reports

## Your Responsibilities:

**Planning**: Break down research requests into optimal sub-tasks
**Coordination**: Execute agents in the right order (parallel where possible)
**Quality Control**: Ensure each step meets quality standards before proceeding
**Error Handling**: Retry or adjust strategy when agents encounter issues
**Aggregation**: Combine results from multiple agents into coherent output

## Workflow Pattern:

For each research request:
1. Analyze the query to understand research needs
2. Plan the execution strategy (parallel searches, validation steps, etc.)
3. Execute search agents in parallel
4. Validate results through fact checker
5. Iteratively improve summary quality
6. Generate final formatted report

## Quality Standards:

- Minimum 5 credible sources
- Fact-check claims with 85%+ confidence
- Summary quality score >= 0.8
- Proper citations in academic format
- Clear distinction between facts and analysis

You have access to specialized sub-agents as tools. Use them strategically to produce
high-quality research outputs efficiently.
"""


def create_orchestrator_agent(
    client: genai.Client,
    search_agent: Agent,
    summarizer_agent: Agent,
    fact_checker_agent: Agent,
    report_generator_agent: Agent,
    quality_scorer: Any
) -> Agent:
    """
    Create the orchestrator agent with access to all specialized agents.
    
    Args:
        client: Gemini client
        search_agent: Specialized agent for searching information
        summarizer_agent: Specialized agent for summarization
        fact_checker_agent: Specialized agent for fact verification
        report_generator_agent: Specialized agent for report generation
        quality_scorer: Tool for evaluating quality
        
    Returns:
        Configured orchestrator agent
    """
    # Create orchestrator with sub-agents
    # Note: Custom tools like quality_scorer need to be wrapped as BaseTool instances
    # For now, only using sub-agents without additional tools
    orchestrator = Agent(
        name="orchestrator_agent",
        model="gemini-2.0-flash-exp",  # Use latest Gemini model
        instruction=ORCHESTRATOR_PROMPT,
        sub_agents=[
            search_agent,
            summarizer_agent,
            fact_checker_agent,
            report_generator_agent
        ],
        generate_content_config={
            "temperature": 0.3,  # Lower for more focused coordination
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": 2048,
        }
    )
    
    return orchestrator


# Example usage showing how orchestrator coordinates agents
async def orchestrate_research_example(
    orchestrator: Agent,
    query: str,
    context: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Example of how the orchestrator coordinates the research workflow.
    
    This demonstrates:
    - Breaking down complex tasks
    - Sequential agent execution
    - Quality-based iteration
    - Result aggregation
    """
    # Orchestrator analyzes query and plans execution
    plan_prompt = f"""
    Research Query: {query}
    
    Context: {context}
    
    Create a detailed execution plan for this research request:
    1. What specific searches should be performed (can be parallel)?
    2. What validation steps are needed?
    3. What quality standards apply?
    4. What format should the final report use?
    
    Provide your plan in structured format.
    """
    
    # Orchestrator would execute this plan using its tools (sub-agents)
    # In production, this would be handled by the ADK's agent execution engine
    
    return {
        "status": "planned",
        "execution_plan": "Multi-step research plan",
        "estimated_duration": "2-3 minutes"
    }
