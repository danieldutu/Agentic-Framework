"""Research agent implementation for information gathering and research."""

from typing import Any, Dict, List


from core.base_agent import BaseAgent
from core.agent_types import AgentCapability, AgentConfig, AgentInput, AgentOutput
from config.gemini_config import GeminiConfig
from config.settings import get_settings
from memory.memory_store import MemoryStore
from core.agent_types import AgentMessage


class ResearchAgent(BaseAgent):
    """Agent specialized in research and information gathering."""

    def __init__(self, config: AgentConfig) -> None:
        """Initialize the research agent.

        Args:
            config: Agent configuration
        """
        super().__init__(config)

        # Initialize components
        self.settings = get_settings()
        self.gemini_config = GeminiConfig(self.settings)
        self.memory_store = MemoryStore(self.agent_id)

        # Research-specific configuration
        self.max_search_results = config.custom_config.get("max_search_results", 10)
        self.search_timeout = config.custom_config.get("search_timeout", 30)
        self.research_depth = config.custom_config.get("research_depth", "medium")

        self.logger.info("Research agent initialized")

    def get_capabilities(self) -> List[AgentCapability]:
        """Get the capabilities of this agent.

        Returns:
            List of agent capabilities
        """
        return [
            AgentCapability.RESEARCH,
            AgentCapability.ANALYSIS,
            AgentCapability.MEMORY,
            AgentCapability.COMMUNICATION,
        ]

    async def process(self, input_data: AgentInput) -> AgentOutput:
        """Process research requests.

        Args:
            input_data: Input containing research request

        Returns:
            Research results and findings
        """
        try:
            self.logger.debug(f"Processing research request: {input_data.id}")

            # Track requesting agent for collaboration
            requesting_agent_id = input_data.metadata.get("requesting_agent_id") if input_data.metadata else None

            # Extract research parameters
            if isinstance(input_data.content, dict):
                query = input_data.content.get("query", "")
                research_type = input_data.content.get("type", "general")
                depth = input_data.content.get("depth", self.research_depth)
            else:
                query = str(input_data.content)
                research_type = "general"
                depth = self.research_depth

            if not query:
                return AgentOutput(
                    content={"error": "No research query provided"},
                    source_agent=self.agent_id,
                    confidence=0.0,
                )

            # Check memory for similar research first
            memory_results = await self._search_memory(query)

            # Perform research based on type
            research_results = await self._conduct_research(query, research_type, depth)

            # Analyze and synthesize findings
            analysis = await self._analyze_findings(
                query, research_results, memory_results
            )

            # Store research in memory
            await self._store_research_memory(query, research_results, analysis)

            # Prepare output
            output_content = {
                "query": query,
                "research_type": research_type,
                "findings": research_results,
                "analysis": analysis,
                "memory_matches": len(memory_results),
                "sources_found": len(research_results.get("sources", [])),
                "confidence_score": research_results.get("confidence", 0.7),
            }

            confidence = min(research_results.get("confidence", 0.7), 1.0)

            output = AgentOutput(
                content=output_content,
                source_agent=self.agent_id,
                confidence=confidence,
                metadata={
                    "research_type": research_type,
                    "depth": depth,
                    "sources_count": len(research_results.get("sources", [])),
                },
            )

            # Send results back to requesting agent if this was a collaboration
            if requesting_agent_id and self._communication_handler:
                await self._send_results_to_requester(requesting_agent_id, output)

            self.logger.debug(f"Research completed for: {query}")
            return output

        except Exception as e:
            self.logger.error(f"Research processing failed: {e}")
            return AgentOutput(
                content={"error": f"Research failed: {str(e)}"},
                source_agent=self.agent_id,
                confidence=0.0,
                metadata={"error": True},
            )

    async def handle_message(self, message: AgentMessage) -> None:
        """Handle incoming collaboration messages.
        
        Args:
            message: The incoming message
        """
        if message.message_type == "collaboration_request":
            await self._handle_collaboration_request(message)
        else:
            await super().handle_message(message)

    async def _handle_collaboration_request(self, message: AgentMessage) -> None:
        """Handle collaboration research requests.
        
        Args:
            message: The collaboration request message
        """
        try:
            payload = message.payload
            research_query = payload.get("research_query", "")
            
            if research_query:
                # Create research task with requesting agent info
                task_input = AgentInput(
                    content={
                        "query": research_query,
                        "type": payload.get("research_type", "general"),
                        "depth": payload.get("research_depth", self.research_depth)
                    },
                    metadata={"requesting_agent_id": message.from_agent}
                )
                
                # Submit the research task
                await self.submit_task(task_input)
                self.logger.debug(f"Processing collaboration request from {message.from_agent}")
                
        except Exception as e:
            self.logger.error(f"Failed to handle collaboration request: {e}")

    async def _send_results_to_requester(self, requesting_agent_id: str, results: AgentOutput) -> None:
        """Send research results back to the requesting agent.
        
        Args:
            requesting_agent_id: ID of the agent that requested the research
            results: The research results to send back
        """
        try:
            response_message = AgentMessage(
                from_agent=self.agent_id,
                to_agent=requesting_agent_id,
                message_type="research_completed",
                payload={
                    "results": results.content,
                    "confidence": results.confidence,
                    "research_query": results.content.get("query") if isinstance(results.content, dict) else "unknown",
                    "completion_status": "success",
                    "processing_time": results.processing_time
                }
            )
            
            await self._communication_handler.send_message(requesting_agent_id, response_message)
            self.logger.debug(f"Sent research results back to {requesting_agent_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to send results to requester: {e}")

    async def _search_memory(self, query: str) -> List[Dict[str, Any]]:
        """Search memory for relevant past research.

        Args:
            query: Research query

        Returns:
            List of relevant memory entries
        """
        try:
            memory_results = await self.memory_store.search_memories(
                query=query, tags=["research", "findings"], limit=5
            )

            self.logger.debug(f"Found {len(memory_results)} relevant memories")
            return memory_results

        except Exception as e:
            self.logger.error(f"Memory search failed: {e}")
            return []

    async def _conduct_research(
        self, query: str, research_type: str, depth: str
    ) -> Dict[str, Any]:
        """Conduct research using various methods.

        Args:
            query: Research query
            research_type: Type of research (general, technical, factual, etc.)
            depth: Research depth (light, medium, deep)

        Returns:
            Research results
        """
        results = {
            "sources": [],
            "key_findings": [],
            "confidence": 0.7,
            "research_method": "ai_assisted",
        }

        try:
            # Use Gemini for research assistance
            research_prompt = self._build_research_prompt(query, research_type, depth)

            research_response = await self.gemini_config.generate_content(
                prompt=research_prompt,
                system_instruction="You are a thorough research assistant. Provide accurate, well-sourced information.",
            )

            # Parse the AI response
            if research_response:
                findings = await self._parse_research_response(research_response)
                results.update(findings)

            # If configured, could add web search, API calls, etc.
            if self.config.custom_config.get("enable_web_search", False):
                web_results = await self._web_search(query)
                results["sources"].extend(web_results.get("sources", []))
                results["key_findings"].extend(web_results.get("findings", []))

            self.logger.debug(f"Research conducted for: {query}")
            return results

        except Exception as e:
            self.logger.error(f"Research execution failed: {e}")
            return {
                "sources": [],
                "key_findings": [f"Research error: {str(e)}"],
                "confidence": 0.1,
                "research_method": "failed",
            }

    def _build_research_prompt(self, query: str, research_type: str, depth: str) -> str:
        """Build a research prompt for the AI model.

        Args:
            query: Research query
            research_type: Type of research
            depth: Research depth

        Returns:
            Formatted research prompt
        """
        depth_instructions = {
            "light": "Provide a brief overview with key points.",
            "medium": "Provide detailed information with multiple perspectives and examples.",
            "deep": "Provide comprehensive analysis with detailed explanations, comparisons, and implications.",
        }

        type_instructions = {
            "general": "Research this topic broadly, covering main aspects and current understanding.",
            "technical": "Focus on technical details, specifications, and implementation aspects.",
            "factual": "Verify facts and provide accurate, current information with sources when possible.",
            "comparative": "Compare different options, approaches, or solutions related to this topic.",
            "trend": "Research current trends, developments, and future predictions for this topic.",
        }

        prompt = f"""
Research Query: {query}

Research Type: {research_type}
Research Depth: {depth}

Instructions:
- {type_instructions.get(research_type, type_instructions['general'])}
- {depth_instructions.get(depth, depth_instructions['medium'])}
- Structure your response with clear sections
- Include key findings, insights, and relevant details
- If making claims, indicate confidence level
- Suggest related topics for further research

Please provide a comprehensive research response.
        """.strip()

        return prompt

    async def _parse_research_response(self, response: str) -> Dict[str, Any]:
        """Parse AI research response into structured data.

        Args:
            response: AI response text

        Returns:
            Structured research data
        """
        try:
            # Use AI to help structure the response
            parsing_prompt = f"""
Please parse the following research response into a structured format.
Extract key findings, sources mentioned, and determine a confidence score (0.0-1.0).

Research Response:
{response}

Please provide your analysis in this format:
KEY_FINDINGS: [list the main findings]
SOURCES: [list any sources mentioned] 
CONFIDENCE: [score from 0.0-1.0 based on quality and specificity]
INSIGHTS: [key insights and implications]
            """.strip()

            parsed_response = await self.gemini_config.generate_content(
                prompt=parsing_prompt,
                system_instruction="You are a data parser. Extract information accurately and provide confidence scores based on specificity and reliability.",
            )

            # Extract structured data from parsed response
            findings = self._extract_findings_from_text(parsed_response)

            return {
                "key_findings": findings.get("findings", [response]),
                "sources": findings.get("sources", ["AI Research Assistant"]),
                "confidence": findings.get("confidence", 0.7),
                "insights": findings.get("insights", []),
                "raw_response": response,
            }

        except Exception as e:
            self.logger.error(f"Failed to parse research response: {e}")
            return {
                "key_findings": [response],
                "sources": ["AI Research Assistant"],
                "confidence": 0.6,
                "insights": [],
                "raw_response": response,
            }

    def _extract_findings_from_text(self, text: str) -> Dict[str, Any]:
        """Extract structured findings from parsed text.

        Args:
            text: Parsed text containing structured information

        Returns:
            Extracted structured data
        """
        findings = {}

        try:
            lines = text.split("\n")
            current_section = None
            current_content = []

            for line in lines:
                line = line.strip()
                if line.startswith("KEY_FINDINGS:"):
                    if current_section:
                        findings[current_section] = current_content
                    current_section = "findings"
                    current_content = [line.replace("KEY_FINDINGS:", "").strip()]
                elif line.startswith("SOURCES:"):
                    if current_section:
                        findings[current_section] = current_content
                    current_section = "sources"
                    current_content = [line.replace("SOURCES:", "").strip()]
                elif line.startswith("CONFIDENCE:"):
                    if current_section:
                        findings[current_section] = current_content
                    confidence_text = line.replace("CONFIDENCE:", "").strip()
                    try:
                        findings["confidence"] = float(confidence_text)
                    except ValueError:
                        findings["confidence"] = 0.7
                    current_section = None
                    current_content = []
                elif line.startswith("INSIGHTS:"):
                    if current_section:
                        findings[current_section] = current_content
                    current_section = "insights"
                    current_content = [line.replace("INSIGHTS:", "").strip()]
                elif line and current_section:
                    current_content.append(line)

            # Add final section
            if current_section and current_content:
                findings[current_section] = current_content

        except Exception as e:
            self.logger.error(f"Failed to extract findings: {e}")

        return findings

    async def _web_search(self, query: str) -> Dict[str, Any]:
        """Perform web search (placeholder for future implementation).

        Args:
            query: Search query

        Returns:
            Web search results
        """
        # Placeholder for web search implementation
        # In a real implementation, you might use:
        # - Google Custom Search API
        # - Bing Search API
        # - DuckDuckGo API
        # - Web scraping with aiohttp

        return {
            "sources": ["Web search not yet implemented"],
            "findings": ["Web search functionality would be implemented here"],
        }

    async def _analyze_findings(
        self,
        query: str,
        research_results: Dict[str, Any],
        memory_results: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Analyze research findings and provide insights.

        Args:
            query: Original research query
            research_results: Current research results
            memory_results: Relevant past research from memory

        Returns:
            Analysis and insights
        """
        try:
            analysis_prompt = f"""
Analyze the following research findings for the query: "{query}"

Current Research Results:
{research_results.get('key_findings', [])}

Previous Related Research:
{[mem.get('content', {}) for mem in memory_results]}

Please provide:
1. Key insights and patterns
2. Reliability assessment
3. Gaps in knowledge
4. Recommendations for further research
5. Practical implications
            """.strip()

            analysis_response = await self.gemini_config.generate_content(
                prompt=analysis_prompt,
                system_instruction="You are a research analyst. Provide thorough analysis and actionable insights.",
            )

            return {
                "summary": analysis_response,
                "key_insights": research_results.get("insights", []),
                "reliability_score": research_results.get("confidence", 0.7),
                "knowledge_gaps": [],
                "recommendations": [],
                "sources_analyzed": len(research_results.get("sources", [])),
                "memory_context": len(memory_results),
            }

        except Exception as e:
            self.logger.error(f"Analysis failed: {e}")
            return {"summary": "Analysis could not be completed", "error": str(e)}

    async def _store_research_memory(
        self, query: str, results: Dict[str, Any], analysis: Dict[str, Any]
    ) -> None:
        """Store research results in memory.

        Args:
            query: Research query
            results: Research results
            analysis: Research analysis
        """
        try:
            memory_content = {
                "query": query,
                "findings": results.get("key_findings", []),
                "sources": results.get("sources", []),
                "analysis": analysis.get("summary", ""),
                "confidence": results.get("confidence", 0.7),
                "research_date": None,
            }

            importance = min(
                results.get("confidence", 0.7) + 0.2, 1.0
            )  # Boost importance for research

            await self.memory_store.remember(
                content=memory_content,
                memory_type="semantic",
                tags=["research", "findings", "analysis"],
                importance=importance,
            )

            self.logger.debug(f"Stored research memory for query: {query}")

        except Exception as e:
            self.logger.error(f"Failed to store research memory: {e}")

    async def get_research_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get research history from memory.

        Args:
            limit: Maximum number of results

        Returns:
            List of past research
        """
        try:
            return await self.memory_store.get_memories_by_tag("research", limit=limit)
        except Exception as e:
            self.logger.error(f"Failed to get research history: {e}")
            return []

    async def suggest_related_research(self, query: str) -> List[str]:
        """Suggest related research topics.

        Args:
            query: Current research query

        Returns:
            List of suggested research topics
        """
        try:
            suggestion_prompt = f"""
Based on the research query: "{query}"

Suggest 5 related research topics that would provide valuable additional context or deeper understanding.
Focus on:
- Adjacent topics
- Underlying concepts
- Practical applications
- Current developments
- Comparative analysis opportunities

Provide just the topic suggestions, one per line.
            """.strip()

            suggestions_response = await self.gemini_config.generate_content(
                prompt=suggestion_prompt,
                system_instruction="You are a research advisor. Suggest relevant and valuable research directions.",
            )

            # Parse suggestions
            suggestions = [
                line.strip()
                for line in suggestions_response.split("\n")
                if line.strip() and not line.startswith("-")
            ]

            return suggestions[:5]  # Limit to 5 suggestions

        except Exception as e:
            self.logger.error(f"Failed to generate research suggestions: {e}")
            return []
