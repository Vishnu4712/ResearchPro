"""
ResearchPro: Intelligent Research Assistant Agent System
Main entry point for the multi-agent research system.

Author: [Your Name]
Course: Kaggle 5-Day AI Agents Course
Track: Agents for Good
"""

import os
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ADK imports
from google import genai
from google.genai import types
from google.adk import Agent, Runner
from google.adk.tools.google_search_tool import GoogleSearchTool
from google.adk.sessions import InMemorySessionService
from google.adk.memory import InMemoryMemoryService

# Local imports
from agents.orchestrator import create_orchestrator_agent
from agents.search_agent import create_search_agent
from agents.summarizer import create_summarizer_agent
from agents.fact_checker import create_fact_checker_agent
from agents.report_generator import create_report_generator_agent

from tools.academic_search import AcademicSearchTool
from tools.citation_tool import CitationFormatterTool
from tools.quality_scorer import QualityScorerTool

from services.session_service import ResearchSessionService
from services.memory_service import ResearchMemoryService
from services.state_manager import ResearchStateManager

from observability.logging_config import setup_logging
from observability.tracing import setup_tracing
from observability.metrics import MetricsCollector

# Setup observability
logger = setup_logging()
tracer = setup_tracing()
metrics = MetricsCollector()


class ResearchProSystem:
    """
    Main ResearchPro system that orchestrates multiple specialized agents
    to perform comprehensive research tasks.
    
    This system demonstrates:
    - Multi-agent coordination (Sequential + Parallel + Loop)
    - Custom and built-in tools
    - Long-running operations with pause/resume
    - Session and memory management
    - Comprehensive observability
    - Evaluation framework
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        enable_memory: bool = True,
        enable_tracing: bool = True,
        use_vertex_memory: bool = False
    ):
        """
        Initialize the ResearchPro system.
        
        Args:
            api_key: Gemini API key (or set GOOGLE_API_KEY env var)
            enable_memory: Enable persistent memory across sessions
            enable_tracing: Enable distributed tracing
            use_vertex_memory: Use Vertex AI Memory Bank (requires GCP setup)
        """
        logger.info("Initializing ResearchPro System")
        
        # Initialize Gemini client
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY must be set")
        
        self.client = genai.Client(api_key=self.api_key)
        
        # Initialize services
        self.session_service = ResearchSessionService()
        
        if use_vertex_memory:
            # Use Vertex AI Memory Bank for production
            self.memory_service = ResearchMemoryService(use_vertex=True)
        else:
            # Use in-memory for development
            self.memory_service = ResearchMemoryService(use_vertex=False)
        
        self.state_manager = ResearchStateManager()
        
        # Initialize tools
        self._initialize_tools()
        
        # Initialize agents
        self._initialize_agents()
        
        # Metrics
        self.metrics = metrics
        self.enable_tracing = enable_tracing
        
        logger.info("ResearchPro System initialized successfully")
    
    def _initialize_tools(self):
        """Initialize all tools available to agents."""
        logger.info("Initializing tools")

        # Built-in tools
        self.google_search = GoogleSearchTool()
        # Note: CodeExecutionTool not available in google.adk.tools
        # Consider using FunctionTool or another alternative
        # self.code_executor = CodeExecutionTool()

        # Custom tools
        self.academic_search = AcademicSearchTool()
        self.citation_formatter = CitationFormatterTool()
        self.quality_scorer = QualityScorerTool()

        logger.info("Tools initialized")
    
    def _initialize_agents(self):
        """Initialize all specialized agents."""
        logger.info("Initializing agents")
        
        # Create specialized agents
        # Note: Custom tools (academic_search) need to be wrapped as BaseTool instances
        # For now, only using google_search which is a built-in tool
        self.search_agent = create_search_agent(
            client=self.client,
            tools=[self.google_search]
        )
        
        self.summarizer_agent = create_summarizer_agent(
            client=self.client,
            tools=[]
        )
        
        self.fact_checker_agent = create_fact_checker_agent(
            client=self.client,
            tools=[self.google_search]
        )
        
        self.report_generator_agent = create_report_generator_agent(
            client=self.client,
            tools=[]
        )
        
        # Create orchestrator with all sub-agents
        self.orchestrator = create_orchestrator_agent(
            client=self.client,
            search_agent=self.search_agent,
            summarizer_agent=self.summarizer_agent,
            fact_checker_agent=self.fact_checker_agent,
            report_generator_agent=self.report_generator_agent,
            quality_scorer=self.quality_scorer
        )
        
        logger.info("Agents initialized")
    
    async def research(
        self,
        query: str,
        user_id: str = "default_user",
        session_id: Optional[str] = None,
        max_sources: int = 10,
        require_approval: bool = False
    ) -> Dict[str, Any]:
        """
        Perform comprehensive research on a given query.
        
        Args:
            query: Research question or topic
            user_id: User identifier for memory/session management
            session_id: Optional session ID to continue previous research
            max_sources: Maximum number of sources to search
            require_approval: Pause for human approval before generating report
            
        Returns:
            Dictionary containing research results, report, and metadata
        """
        # Start metrics collection
        start_time = datetime.now()
        self.metrics.increment_counter("research_requests_total")
        
        with tracer.start_as_current_span("research_request") as span:
            span.set_attribute("query", query)
            span.set_attribute("user_id", user_id)
            span.set_attribute("max_sources", max_sources)
            
            try:
                logger.info(f"Starting research for query: {query[:100]}...")
                
                # Get or create session
                if session_id:
                    session = self.session_service.get_session(session_id)
                    logger.info(f"Continuing session: {session_id}")
                else:
                    session = self.session_service.create_session(
                        user_id=user_id,
                        initial_query=query
                    )
                    session_id = session["session_id"]
                    logger.info(f"Created new session: {session_id}")
                
                # Retrieve relevant memories
                memories = await self.memory_service.search_memories(
                    user_id=user_id,
                    query=query
                )
                
                logger.info(f"Retrieved {len(memories)} relevant memories")
                
                # Prepare context for orchestrator
                context = {
                    "query": query,
                    "user_id": user_id,
                    "session_id": session_id,
                    "max_sources": max_sources,
                    "memories": memories,
                    "require_approval": require_approval,
                    "research_preferences": self._get_user_preferences(user_id)
                }
                
                # Execute research workflow through orchestrator
                logger.info("Executing research workflow")
                
                result = await self._execute_research_workflow(
                    context=context,
                    session=session
                )
                
                # Store findings in memory
                await self._store_research_memory(
                    user_id=user_id,
                    query=query,
                    result=result
                )
                
                # Update session
                self.session_service.update_session(
                    session_id=session_id,
                    result=result
                )
                
                # Record metrics
                duration = (datetime.now() - start_time).total_seconds()
                self.metrics.record_histogram(
                    "research_duration_seconds",
                    duration
                )
                self.metrics.increment_counter("research_requests_success")
                
                logger.info(f"Research completed successfully in {duration:.2f}s")
                
                return {
                    "success": True,
                    "session_id": session_id,
                    "query": query,
                    "result": result,
                    "duration_seconds": duration,
                    "sources_processed": result.get("sources_count", 0),
                    "quality_score": result.get("quality_score", 0)
                }
                
            except Exception as e:
                logger.error(f"Research failed: {str(e)}", exc_info=True)
                self.metrics.increment_counter("research_requests_failed")
                span.set_attribute("error", str(e))
                
                return {
                    "success": False,
                    "error": str(e),
                    "session_id": session_id,
                    "query": query
                }
    
    async def _execute_research_workflow(
        self,
        context: Dict[str, Any],
        session: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute the multi-agent research workflow.
        
        This demonstrates:
        - Sequential execution (search -> fact-check -> summarize -> report)
        - Parallel execution (multiple search agents)
        - Loop execution (iterative quality improvement)
        """
        with tracer.start_as_current_span("research_workflow") as span:
            
            # Phase 1: Parallel Search
            logger.info("Phase 1: Parallel search across multiple sources")
            search_results = await self._parallel_search(
                query=context["query"],
                max_sources=context["max_sources"]
            )
            span.set_attribute("sources_found", len(search_results))
            
            # Phase 2: Fact Checking
            logger.info("Phase 2: Fact checking and validation")
            validated_results = await self._fact_check_results(search_results)
            
            # Phase 3: Iterative Summarization (Loop until quality threshold)
            logger.info("Phase 3: Iterative summarization with quality loop")
            summary = await self._iterative_summarization(
                results=validated_results,
                min_quality_score=0.8
            )
            
            # Phase 4: Approval Gate (Long-running operation)
            if context.get("require_approval"):
                logger.info("Phase 4: Pausing for human approval")
                approval = await self._request_human_approval(
                    session_id=context["session_id"],
                    summary=summary
                )
                
                if not approval:
                    logger.info("Research paused pending approval")
                    return {
                        "status": "paused",
                        "reason": "awaiting_approval",
                        "summary": summary
                    }
            
            # Phase 5: Report Generation
            logger.info("Phase 5: Generating final report")
            report = await self._generate_report(
                query=context["query"],
                summary=summary,
                sources=validated_results,
                user_preferences=context["research_preferences"]
            )
            
            return {
                "status": "completed",
                "summary": summary,
                "report": report,
                "sources_count": len(validated_results),
                "quality_score": summary.get("quality_score", 0),
                "sources": validated_results
            }
    
    async def _parallel_search(
        self,
        query: str,
        max_sources: int
    ) -> List[Dict[str, Any]]:
        """
        Execute parallel searches across multiple search agents.
        
        Demonstrates: Parallel agent execution
        """
        with tracer.start_as_current_span("parallel_search"):
            # Split query into multiple search angles
            search_angles = self._generate_search_angles(query)
            
            # Create parallel search tasks
            search_tasks = []
            for angle in search_angles[:3]:  # Max 3 parallel searches
                task = self._search_with_agent(angle, max_sources // 3)
                search_tasks.append(task)
            
            # Execute searches in parallel
            logger.info(f"Executing {len(search_tasks)} parallel searches")
            results = await asyncio.gather(*search_tasks)
            
            # Combine and deduplicate results
            all_results = []
            seen_urls = set()
            
            for result_list in results:
                for result in result_list:
                    url = result.get("url")
                    if url and url not in seen_urls:
                        all_results.append(result)
                        seen_urls.add(url)
            
            logger.info(f"Found {len(all_results)} unique sources")
            return all_results[:max_sources]
    
    def _generate_search_angles(self, query: str) -> List[str]:
        """Generate multiple search perspectives for parallel execution."""
        # In production, use LLM to generate angles
        # For now, simple variations
        return [
            f"{query} recent research",
            f"{query} academic papers",
            f"{query} expert analysis"
        ]
    
    async def _search_with_agent(
        self,
        query: str,
        max_results: int
    ) -> List[Dict[str, Any]]:
        """Execute search using search agent."""
        # Simulate agent search (replace with actual agent call)
        # In production: return await self.search_agent.run(query, max_results)
        return [
            {
                "url": f"https://example.com/{i}",
                "title": f"Result {i} for {query}",
                "snippet": f"Relevant content about {query}",
                "source": "google_search"
            }
            for i in range(max_results)
        ]
    
    async def _fact_check_results(
        self,
        results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Validate results using fact checker agent."""
        with tracer.start_as_current_span("fact_checking"):
            logger.info(f"Fact checking {len(results)} results")
            
            # In production, use actual fact checker agent
            # For now, simulate validation
            validated = []
            for result in results:
                result["validated"] = True
                result["confidence_score"] = 0.85
                validated.append(result)
            
            return validated
    
    async def _iterative_summarization(
        self,
        results: List[Dict[str, Any]],
        min_quality_score: float
    ) -> Dict[str, Any]:
        """
        Iteratively improve summary until quality threshold is met.
        
        Demonstrates: Loop agent architecture
        """
        with tracer.start_as_current_span("iterative_summarization"):
            max_iterations = 3
            iteration = 0
            
            summary = None
            quality_score = 0.0
            
            while iteration < max_iterations:
                iteration += 1
                logger.info(f"Summarization iteration {iteration}")
                
                # Generate/refine summary
                summary = await self._generate_summary(results, summary)
                
                # Evaluate quality
                quality_score = await self._evaluate_summary_quality(summary)
                
                logger.info(f"Quality score: {quality_score:.2f}")
                
                if quality_score >= min_quality_score:
                    logger.info("Quality threshold met")
                    break
                
                logger.info("Quality below threshold, refining...")
            
            return {
                "content": summary,
                "quality_score": quality_score,
                "iterations": iteration
            }
    
    async def _generate_summary(
        self,
        results: List[Dict[str, Any]],
        previous_summary: Optional[str] = None
    ) -> str:
        """Generate or refine summary using summarizer agent."""
        # In production, use actual summarizer agent
        # For now, simulate
        if previous_summary:
            return f"Refined summary based on {len(results)} sources"
        else:
            return f"Initial summary based on {len(results)} sources"
    
    async def _evaluate_summary_quality(self, summary: str) -> float:
        """Evaluate summary quality using quality scorer tool."""
        # In production, use actual quality scorer
        # For now, simulate
        return 0.85
    
    async def _request_human_approval(
        self,
        session_id: str,
        summary: Dict[str, Any]
    ) -> bool:
        """
        Request human approval before proceeding.
        
        Demonstrates: Long-running operations with pause/resume
        """
        logger.info("Requesting human approval")
        
        # In production, this would:
        # 1. Save current state
        # 2. Send notification to user
        # 3. Wait for callback/webhook
        # 4. Resume from saved state
        
        # For demo purposes, auto-approve
        return True
    
    async def _generate_report(
        self,
        query: str,
        summary: Dict[str, Any],
        sources: List[Dict[str, Any]],
        user_preferences: Dict[str, Any]
    ) -> str:
        """Generate final formatted report."""
        with tracer.start_as_current_span("report_generation"):
            # In production, use report generator agent
            # For now, simulate
            report = f"""
# Research Report: {query}

## Summary
{summary.get('content', '')}

## Quality Metrics
- Sources Analyzed: {len(sources)}
- Quality Score: {summary.get('quality_score', 0):.2%}
- Iterations: {summary.get('iterations', 1)}

## Sources
{self._format_sources(sources[:5])}

## Methodology
This report was generated using a multi-agent research system with:
- Parallel search across multiple sources
- Fact-checking and validation
- Iterative quality improvement
- Automated citation formatting

---
Generated by ResearchPro AI Agent System
"""
            return report
    
    def _format_sources(self, sources: List[Dict[str, Any]]) -> str:
        """Format sources for report."""
        formatted = []
        for i, source in enumerate(sources, 1):
            formatted.append(
                f"{i}. [{source['title']}]({source['url']}) - "
                f"Confidence: {source.get('confidence_score', 0):.0%}"
            )
        return "\n".join(formatted)
    
    async def _store_research_memory(
        self,
        user_id: str,
        query: str,
        result: Dict[str, Any]
    ):
        """Store research findings in long-term memory."""
        logger.info("Storing research in long-term memory")
        
        # Extract key facts to store
        facts = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "sources_count": result.get("sources_count", 0),
            "quality_score": result.get("quality_score", 0),
            "summary": result.get("summary", {}).get("content", "")[:500]
        }
        
        await self.memory_service.store_memory(
            user_id=user_id,
            memory_data=facts
        )
    
    def _get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Retrieve user preferences from memory."""
        # In production, query memory service
        return {
            "citation_style": "APA",
            "detail_level": "comprehensive",
            "preferred_sources": ["academic", "peer-reviewed"]
        }
    
    async def resume_session(self, session_id: str) -> Dict[str, Any]:
        """
        Resume a paused research session.
        
        Demonstrates: Long-running operations resume capability
        """
        logger.info(f"Resuming session: {session_id}")
        
        session = self.session_service.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        if session.get("status") != "paused":
            raise ValueError(f"Session {session_id} is not paused")
        
        # Resume from saved state
        context = session.get("context")
        result = await self._execute_research_workflow(
            context=context,
            session=session
        )
        
        return result


# CLI interface for testing
async def main():
    """Main entry point for CLI testing."""
    print("🔬 ResearchPro: Intelligent Research Assistant")
    print("=" * 60)
    
    # Initialize system
    system = ResearchProSystem()
    
    # Example research query
    query = "What are the latest developments in quantum computing?"
    
    print(f"\n📝 Research Query: {query}")
    print("-" * 60)
    
    # Execute research
    result = await system.research(
        query=query,
        user_id="demo_user",
        max_sources=10,
        require_approval=False
    )
    
    # Display results
    if result["success"]:
        print("\n✅ Research Completed Successfully!")
        print(f"⏱️  Duration: {result['duration_seconds']:.2f} seconds")
        print(f"📚 Sources Processed: {result['sources_processed']}")
        print(f"⭐ Quality Score: {result['quality_score']:.2%}")
        print(f"🆔 Session ID: {result['session_id']}")
        print("\n📄 Report:")
        print("-" * 60)
        print(result['result'].get('report', ''))
    else:
        print(f"\n❌ Research Failed: {result['error']}")


if __name__ == "__main__":
    asyncio.run(main())
