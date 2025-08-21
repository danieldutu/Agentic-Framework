"""Synthesis agent implementation for combining and analyzing information."""

from typing import Any, Dict, List, Optional


from core.base_agent import BaseAgent
from core.agent_types import AgentCapability, AgentConfig, AgentInput, AgentOutput, AgentMessage
from config.gemini_config import GeminiConfig
from config.settings import get_settings
from memory.memory_store import MemoryStore


class SynthesisAgent(BaseAgent):
    """Agent specialized in synthesizing and analyzing information."""

    def __init__(self, config: AgentConfig) -> None:
        """Initialize the synthesis agent.

        Args:
            config: Agent configuration
        """
        super().__init__(config)

        # Initialize components
        self.settings = get_settings()
        self.gemini_config = GeminiConfig(self.settings)
        self.memory_store = MemoryStore(self.agent_id)

        # Synthesis-specific configuration
        self.synthesis_style = config.custom_config.get(
            "synthesis_style", "comprehensive"
        )
        self.max_sources = config.custom_config.get("max_sources", 20)
        self.analysis_depth = config.custom_config.get("analysis_depth", "deep")

        # Collaboration state
        self.pending_research_results = {}
        self.collaboration_sessions = {}

        self.logger.info("Synthesis agent initialized")

    def get_capabilities(self) -> List[AgentCapability]:
        """Get the capabilities of this agent.

        Returns:
            List of agent capabilities
        """
        return [
            AgentCapability.SYNTHESIS,
            AgentCapability.ANALYSIS,
            AgentCapability.REASONING,
            AgentCapability.MEMORY,
            AgentCapability.COMMUNICATION,
        ]

    async def process(self, input_data: AgentInput) -> AgentOutput:
        """Process synthesis requests.

        Args:
            input_data: Input containing information to synthesize

        Returns:
            Synthesized analysis and insights
        """
        try:
            self.logger.debug(f"Processing synthesis request: {input_data.id}")

            # Extract synthesis parameters
            if isinstance(input_data.content, dict):
                topic = input_data.content.get("topic", "")
                sources = input_data.content.get("sources", [])
                synthesis_type = input_data.content.get("type", "analysis")
                style = input_data.content.get("style", self.synthesis_style)
            else:
                # Handle simple text input
                topic = str(input_data.content)
                sources = []
                synthesis_type = "analysis"
                style = self.synthesis_style

            if not topic and not sources:
                return AgentOutput(
                    content={"error": "No topic or sources provided for synthesis"},
                    source_agent=self.agent_id,
                    confidence=0.0,
                )

            # Gather relevant information from memory
            memory_context = await self._gather_memory_context(topic)

            # If no sources provided, try to find related information
            if not sources and topic:
                sources = await self._find_related_sources(topic)

            # Perform synthesis based on type
            synthesis_result = await self._synthesize_information(
                topic, sources, memory_context, synthesis_type, style
            )

            # Generate insights and recommendations
            insights = await self._generate_insights(topic, synthesis_result)

            # Store synthesis results in memory
            await self._store_synthesis_memory(topic, synthesis_result, insights)

            # Prepare output
            output_content = {
                "topic": topic,
                "synthesis_type": synthesis_type,
                "style": style,
                "synthesis": synthesis_result,
                "insights": insights,
                "sources_analyzed": len(sources),
                "memory_context_used": len(memory_context),
                "confidence_score": synthesis_result.get("confidence", 0.8),
            }

            confidence = synthesis_result.get("confidence", 0.8)

            self.logger.debug(f"Synthesis completed for: {topic}")

            return AgentOutput(
                content=output_content,
                source_agent=self.agent_id,
                confidence=confidence,
                metadata={
                    "synthesis_type": synthesis_type,
                    "style": style,
                    "sources_count": len(sources),
                },
            )

        except Exception as e:
            self.logger.error(f"Synthesis processing failed: {e}")
            return AgentOutput(
                content={"error": f"Synthesis failed: {str(e)}"},
                source_agent=self.agent_id,
                confidence=0.0,
                metadata={"error": True},
            )

    async def _gather_memory_context(self, topic: str) -> List[Dict[str, Any]]:
        """Gather relevant context from memory.

        Args:
            topic: Topic to gather context for

        Returns:
            List of relevant memory entries
        """
        try:
            # Search for related memories
            memories = await self.memory_store.search_memories(
                query=topic, tags=["research", "synthesis", "analysis"], limit=10
            )

            self.logger.debug(f"Found {len(memories)} relevant memories for context")
            return memories

        except Exception as e:
            self.logger.error(f"Failed to gather memory context: {e}")
            return []

    async def _find_related_sources(self, topic: str) -> List[Dict[str, Any]]:
        """Find related sources from memory or suggest sources.

        Args:
            topic: Topic to find sources for

        Returns:
            List of related sources
        """
        try:
            # Look for research memories that might contain sources
            research_memories = await self.memory_store.search_memories(
                query=topic, tags=["research"], limit=5
            )

            sources = []
            for memory in research_memories:
                content = memory.get("content", {})
                if isinstance(content, dict):
                    # Extract sources from research memory
                    memory_sources = content.get("sources", [])
                    if memory_sources:
                        sources.extend(memory_sources)

                    # Extract findings as potential sources
                    findings = content.get("findings", [])
                    if findings:
                        sources.append(
                            {
                                "type": "research_findings",
                                "content": findings,
                                "source": f"Previous research on {topic}",
                            }
                        )

            self.logger.debug(f"Found {len(sources)} related sources")
            return sources

        except Exception as e:
            self.logger.error(f"Failed to find related sources: {e}")
            return []

    async def _synthesize_information(
        self,
        topic: str,
        sources: List[Dict[str, Any]],
        memory_context: List[Dict[str, Any]],
        synthesis_type: str,
        style: str,
    ) -> Dict[str, Any]:
        """Synthesize information from multiple sources.

        Args:
            topic: Main topic for synthesis
            sources: List of source materials
            memory_context: Relevant memory context
            synthesis_type: Type of synthesis to perform
            style: Synthesis style

        Returns:
            Synthesis results
        """
        try:
            # Build synthesis prompt
            synthesis_prompt = self._build_synthesis_prompt(
                topic, sources, memory_context, synthesis_type, style
            )

            # Generate synthesis using Gemini
            synthesis_response = await self.gemini_config.generate_content(
                prompt=synthesis_prompt,
                system_instruction="You are an expert analyst specializing in information synthesis. Provide comprehensive, well-structured analysis.",
            )

            # Parse and structure the synthesis
            structured_synthesis = await self._structure_synthesis_response(
                synthesis_response, synthesis_type
            )

            return structured_synthesis

        except Exception as e:
            self.logger.error(f"Failed to synthesize information: {e}")
            return {
                "summary": f"Synthesis failed: {str(e)}",
                "confidence": 0.1,
                "error": True,
            }

    def _build_synthesis_prompt(
        self,
        topic: str,
        sources: List[Dict[str, Any]],
        memory_context: List[Dict[str, Any]],
        synthesis_type: str,
        style: str,
    ) -> str:
        """Build a synthesis prompt for the AI model.

        Args:
            topic: Main topic
            sources: Source materials
            memory_context: Memory context
            synthesis_type: Type of synthesis
            style: Synthesis style

        Returns:
            Formatted synthesis prompt
        """
        type_instructions = {
            "analysis": "Analyze the information thoroughly, identifying patterns, relationships, and key insights.",
            "summary": "Provide a concise summary highlighting the most important points and conclusions.",
            "comparison": "Compare and contrast different viewpoints, approaches, or findings in the sources.",
            "evaluation": "Evaluate the quality, credibility, and implications of the information provided.",
            "integration": "Integrate information from all sources into a cohesive understanding.",
            "synthesis": "Synthesize all information into new insights and comprehensive understanding.",
        }

        style_instructions = {
            "comprehensive": "Provide detailed, thorough analysis covering all aspects.",
            "concise": "Focus on key points and essential information only.",
            "academic": "Use formal, academic tone with detailed reasoning.",
            "practical": "Focus on practical implications and actionable insights.",
            "creative": "Explore creative connections and novel perspectives.",
        }

        # Format sources for the prompt
        sources_text = ""
        for i, source in enumerate(sources, 1):
            if isinstance(source, dict):
                source_type = source.get("type", "unknown")
                content = source.get("content", source.get("text", str(source)))
                sources_text += f"\nSource {i} ({source_type}):\n{content}\n"
            else:
                sources_text += f"\nSource {i}:\n{str(source)}\n"

        # Format memory context
        context_text = ""
        for i, memory in enumerate(memory_context, 1):
            content = memory.get("content", {})
            if isinstance(content, dict):
                context_text += (
                    f"\nContext {i}: {content.get('summary', str(content))}\n"
                )
            else:
                context_text += f"\nContext {i}: {str(content)}\n"

        prompt = f"""
Topic: {topic}

Synthesis Type: {synthesis_type}
Style: {style}

Instructions:
- {type_instructions.get(synthesis_type, type_instructions['analysis'])}
- {style_instructions.get(style, style_instructions['comprehensive'])}

Sources to Synthesize:
{sources_text}

Additional Context from Memory:
{context_text}

Task:
Please synthesize all the provided information about "{topic}". Structure your response with:
1. Executive Summary
2. Key Findings
3. Analysis and Insights
4. Conclusions
5. Recommendations (if applicable)
6. Confidence Assessment

Ensure your synthesis is coherent, well-reasoned, and adds value beyond just summarizing the sources.
        """.strip()

        return prompt

    async def _structure_synthesis_response(
        self, response: str, synthesis_type: str
    ) -> Dict[str, Any]:
        """Structure the synthesis response into organized components.

        Args:
            response: Raw synthesis response
            synthesis_type: Type of synthesis performed

        Returns:
            Structured synthesis data
        """
        try:
            # Use AI to help structure the response
            structuring_prompt = f"""
Please structure the following synthesis response into organized components.
Extract and organize the information into clear sections.

Synthesis Response:
{response}

Please provide the structured analysis in this format:
EXECUTIVE_SUMMARY: [brief overview]
KEY_FINDINGS: [main findings and insights]
ANALYSIS: [detailed analysis]
CONCLUSIONS: [main conclusions]
RECOMMENDATIONS: [actionable recommendations]
CONFIDENCE: [confidence score 0.0-1.0]
GAPS: [knowledge gaps identified]
            """.strip()

            structured_response = await self.gemini_config.generate_content(
                prompt=structuring_prompt,
                system_instruction="You are a document parser. Extract and organize information accurately.",
            )

            # Parse the structured response
            structured_data = self._parse_structured_response(structured_response)

            # Add metadata
            structured_data.update(
                {
                    "synthesis_type": synthesis_type,
                    "raw_response": response,
                    "timestamp": None,
                }
            )

            return structured_data

        except Exception as e:
            self.logger.error(f"Failed to structure synthesis response: {e}")
            return {
                "summary": response,
                "confidence": 0.7,
                "synthesis_type": synthesis_type,
                "raw_response": response,
            }

    def _parse_structured_response(self, response: str) -> Dict[str, Any]:
        """Parse structured response into components.

        Args:
            response: Structured response text

        Returns:
            Parsed components
        """
        components = {}

        try:
            lines = response.split("\n")
            current_section = None
            current_content = []

            for line in lines:
                line = line.strip()
                if ":" in line and line.upper().startswith(
                    (
                        "EXECUTIVE_SUMMARY",
                        "KEY_FINDINGS",
                        "ANALYSIS",
                        "CONCLUSIONS",
                        "RECOMMENDATIONS",
                        "CONFIDENCE",
                        "GAPS",
                    )
                ):
                    # Save previous section
                    if current_section and current_content:
                        components[current_section] = "\n".join(current_content).strip()

                    # Start new section
                    parts = line.split(":", 1)
                    current_section = parts[0].lower().replace("_", "_")
                    current_content = (
                        [parts[1].strip()]
                        if len(parts) > 1 and parts[1].strip()
                        else []
                    )
                elif current_section and line:
                    current_content.append(line)

            # Save final section
            if current_section and current_content:
                components[current_section] = "\n".join(current_content).strip()

            # Handle confidence separately
            if "confidence" in components:
                try:
                    confidence_text = components["confidence"]
                    # Extract numerical value
                    import re

                    match = re.search(r"(\d+\.?\d*)", confidence_text)
                    if match:
                        components["confidence"] = float(match.group(1))
                        if components["confidence"] > 1.0:
                            components["confidence"] = components["confidence"] / 100.0
                    else:
                        components["confidence"] = 0.7
                except (ValueError, AttributeError):
                    components["confidence"] = 0.7
            else:
                components["confidence"] = 0.7

        except Exception as e:
            self.logger.error(f"Failed to parse structured response: {e}")
            components = {"summary": response, "confidence": 0.7}

        return components

    async def _generate_insights(
        self, topic: str, synthesis_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate additional insights from synthesis results.

        Args:
            topic: Original topic
            synthesis_result: Synthesis results

        Returns:
            Generated insights
        """
        try:
            insights_prompt = f"""
Based on the synthesis about "{topic}", please generate deeper insights:

Synthesis Results:
{synthesis_result.get('summary', 'No summary available')}

Key Findings:
{synthesis_result.get('key_findings', 'No key findings available')}

Please provide:
1. Hidden patterns or connections not immediately obvious
2. Implications for future developments
3. Potential risks or challenges
4. Opportunities for further exploration
5. Cross-domain connections
6. Strategic recommendations
            """.strip()

            insights_response = await self.gemini_config.generate_content(
                prompt=insights_prompt,
                system_instruction="You are a strategic analyst. Identify deeper patterns and implications.",
            )

            return {
                "deep_insights": insights_response,
                "generated_at": None,
            }

        except Exception as e:
            self.logger.error(f"Failed to generate insights: {e}")
            return {"error": str(e)}

    async def _store_synthesis_memory(
        self, topic: str, synthesis_result: Dict[str, Any], insights: Dict[str, Any]
    ) -> None:
        """Store synthesis results in memory.

        Args:
            topic: Topic that was synthesized
            synthesis_result: Synthesis results
            insights: Generated insights
        """
        try:
            memory_content = {
                "topic": topic,
                "synthesis": synthesis_result.get("summary", ""),
                "key_findings": synthesis_result.get("key_findings", ""),
                "insights": insights.get("deep_insights", ""),
                "confidence": synthesis_result.get("confidence", 0.7),
                "synthesis_type": synthesis_result.get("synthesis_type", "analysis"),
            }

            importance = min(
                synthesis_result.get("confidence", 0.7) + 0.3, 1.0
            )  # Boost importance for synthesis

            await self.memory_store.remember(
                content=memory_content,
                memory_type="semantic",
                tags=["synthesis", "analysis", "insights"],
                importance=importance,
            )

            self.logger.debug(f"Stored synthesis memory for topic: {topic}")

        except Exception as e:
            self.logger.error(f"Failed to store synthesis memory: {e}")

    async def compare_sources(
        self,
        sources: List[Dict[str, Any]],
        comparison_criteria: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Compare multiple sources on specific criteria.

        Args:
            sources: List of sources to compare
            comparison_criteria: Criteria for comparison

        Returns:
            Comparison results
        """
        try:
            criteria = comparison_criteria or [
                "reliability",
                "relevance",
                "recency",
                "depth",
                "bias",
            ]

            comparison_prompt = f"""
Compare the following sources on these criteria: {', '.join(criteria)}

Sources:
{chr(10).join([f"Source {i+1}: {source}" for i, source in enumerate(sources)])}

For each criterion, rate each source (1-10) and provide reasoning.
Provide an overall ranking and recommendation.
            """.strip()

            comparison_response = await self.gemini_config.generate_content(
                prompt=comparison_prompt,
                system_instruction="You are a source evaluation expert. Provide thorough, objective comparisons.",
            )

            return {
                "comparison": comparison_response,
                "criteria_used": criteria,
                "sources_compared": len(sources),
            }

        except Exception as e:
            self.logger.error(f"Source comparison failed: {e}")
            return {"error": str(e)}

    async def identify_knowledge_gaps(
        self, topic: str, available_information: List[Dict[str, Any]]
    ) -> List[str]:
        """Identify knowledge gaps in available information.

        Args:
            topic: Topic being analyzed
            available_information: Currently available information

        Returns:
            List of identified knowledge gaps
        """
        try:
            gap_analysis_prompt = f"""
Analyze the available information about "{topic}" and identify knowledge gaps.

Available Information:
{chr(10).join([str(info) for info in available_information])}

Identify:
1. Missing factual information
2. Unexplored perspectives
3. Gaps in reasoning or evidence
4. Areas needing more research
5. Contradictions that need resolution

List the gaps clearly and prioritize them by importance.
            """.strip()

            gaps_response = await self.gemini_config.generate_content(
                prompt=gap_analysis_prompt,
                system_instruction="You are a research analyst specializing in gap analysis.",
            )

            # Parse gaps into a list
            gaps = [
                line.strip().lstrip("0123456789.- ")
                for line in gaps_response.split("\n")
                if line.strip() and not line.strip().startswith(("Identify:", "List"))
            ]

            return gaps[:10]  # Limit to top 10 gaps

        except Exception as e:
            self.logger.error(f"Knowledge gap analysis failed: {e}")
            return []

    async def get_synthesis_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get synthesis history from memory.

        Args:
            limit: Maximum number of results

        Returns:
            List of past synthesis work
        """
        try:
            return await self.memory_store.get_memories_by_tag("synthesis", limit=limit)
        except Exception as e:
            self.logger.error(f"Failed to get synthesis history: {e}")
            return []

    async def handle_message(self, message: AgentMessage) -> None:
        """Handle incoming collaboration messages.
        
        Args:
            message: The incoming message
        """
        if message.message_type == "research_completed":
            await self._handle_research_results(message)
        else:
            await super().handle_message(message)

    async def _handle_research_results(self, message: AgentMessage) -> None:
        """Handle research results received from research agents.
        
        Args:
            message: Message containing research results
        """
        try:
            payload = message.payload
            research_query = payload.get("research_query", "")
            results = payload.get("results", {})
            
            if research_query and results:
                # Store the research results
                self.pending_research_results[research_query] = {
                    "results": results,
                    "confidence": payload.get("confidence", 0.7),
                    "from_agent": message.from_agent,
                    "processing_time": payload.get("processing_time", 0),
                    "received_at": None
                }
                
                self.logger.debug(f"Received research results for: {research_query}")
                
                # Check if we have enough results to synthesize
                await self._check_and_synthesize()
                
        except Exception as e:
            self.logger.error(f"Failed to handle research results: {e}")

    async def _check_and_synthesize(self) -> None:
        """Check if we have enough research results to perform synthesis."""
        try:
            # For now, synthesize when we have any results
            # In a more complex implementation, you might wait for multiple results
            if self.pending_research_results:
                await self._synthesize_collected_research()
                
        except Exception as e:
            self.logger.error(f"Failed to check and synthesize: {e}")

    async def _synthesize_collected_research(self) -> None:
        """Synthesize all collected research results."""
        try:
            if not self.pending_research_results:
                return
                
            # Prepare sources from research results
            sources = []
            topic_parts = []
            
            for query, result_data in self.pending_research_results.items():
                results = result_data["results"]
                topic_parts.append(query)
                
                # Convert research results to synthesis sources
                if isinstance(results, dict):
                    findings = results.get("findings", {})
                    if isinstance(findings, dict):
                        key_findings = findings.get("key_findings", [])
                        if key_findings:
                            sources.append({
                                "type": "research_findings",
                                "content": key_findings,
                                "source": f"Research on: {query}",
                                "confidence": result_data["confidence"]
                            })
            
            # Create synthesis topic from research queries
            topic = " and ".join(topic_parts) if topic_parts else "Research synthesis"
            
            if sources:
                # Perform synthesis
                synthesis_input = AgentInput(
                    content={
                        "topic": topic,
                        "sources": sources,
                        "type": "research_synthesis",
                        "style": "comprehensive"
                    }
                )
                
                # Process the synthesis
                synthesis_result = await self.process(synthesis_input)
                
                self.logger.info(f"Completed synthesis of {len(sources)} research results")
                
                # Clear processed results
                self.pending_research_results.clear()
                
                return synthesis_result
                
        except Exception as e:
            self.logger.error(f"Failed to synthesize collected research: {e}")

    async def request_research_collaboration(self, research_queries: List[str], research_agent_id: str) -> None:
        """Request research collaboration from a research agent.
        
        Args:
            research_queries: List of research queries to request
            research_agent_id: ID of the research agent to collaborate with
        """
        try:
            for query in research_queries:
                collaboration_message = AgentMessage(
                    from_agent=self.agent_id,
                    to_agent=research_agent_id,
                    message_type="collaboration_request",
                    payload={
                        "research_query": query,
                        "research_type": "analytical",
                        "research_depth": "medium",
                        "collaboration_type": "research_for_synthesis"
                    }
                )
                
                if self._communication_handler:
                    await self._communication_handler.send_message(research_agent_id, collaboration_message)
                    self.logger.debug(f"Requested research collaboration for: {query}")
                    
        except Exception as e:
            self.logger.error(f"Failed to request research collaboration: {e}")
