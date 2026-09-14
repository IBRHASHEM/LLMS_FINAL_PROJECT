"""
Main Orchestrator - Coordinates all systems and components
المنسق الرئيسي - ينسق جميع الأنظمة والمكونات
"""

from config_agents import (
    researcher_agent, analyzer_agent, writer_agent, validator_agent,
    save_to_memory, search_memory, vector_store
)
from neurobot_chat import NeuroBot
from crewai import Task, Crew
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import json

# =========================
# Data Models
# =========================

@dataclass
class ResearchResult:
    """Model for research results"""
    topic: str
    query: str
    source_url: str
    content: str
    timestamp: str
    relevance_score: float = 1.0


@dataclass
class ResearchReport:
    """Model for final research reports"""
    title: str
    topic: str
    executive_summary: str
    findings: str
    analysis: str
    recommendations: str
    sources: List[str]
    quality_score: float
    timestamp: str


class IntelligentResearchOrchestrator:
    """
    Main orchestrator for the entire research system
    المنسق الرئيسي لنظام البحث المتكامل
    """

    def __init__(self, project_name: str = "Research Project"):
        """Initialize the orchestrator"""
        self.project_name = project_name
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.neurobot = NeuroBot(user_name=project_name)
        self.research_results: List[ResearchResult] = []
        self.reports: List[ResearchReport] = []
        self.conversation_log = []
        
        print(f"✅ Orchestrator initialized: {project_name}")
        print(f"📅 Session ID: {self.session_id}")

    def conduct_research(self, query: str, num_iterations: int = 1) -> Dict:
        """
        Conduct comprehensive research using all agents
        إجراء بحث شامل باستخدام جميع الوكلاء
        """
        print(f"\n{'='*60}")
        print(f"🔍 Starting Research: {query}")
        print(f"{'='*60}\n")

        try:
            # Define tasks for each agent
            research_task = Task(
                description=f"""
                Research the following topic thoroughly:
                {query}
                
                Use web search and document scraping to find:
                - Relevant and reliable information
                - Multiple perspectives on the topic
                - Recent developments and trends
                - Academic and industry sources
                
                Include URLs of all sources used.
                Do not invent or speculate on information.
                """,
                expected_output="""
                A detailed research report containing:
                - Key findings and facts
                - Important statistics and data
                - Different perspectives
                - Source citations with URLs
                """,
                agent=researcher_agent,
                async_execution=False
            )

            analysis_task = Task(
                description=f"""
                Analyze the research conducted on: {query}
                
                Identify:
                - Main themes and patterns
                - Key insights and implications
                - Strengths and weaknesses of sources
                - Trends and forecasts
                - Practical applications
                """,
                expected_output="""
                A detailed analysis containing:
                - Identified patterns and themes
                - Critical insights
                - Implications and impacts
                - Trend analysis
                - Recommendations
                """,
                agent=analyzer_agent,
                context=[research_task],
                async_execution=False
            )

            writing_task = Task(
                description=f"""
                Create a professional research report on: {query}
                
                Include:
                - Executive summary (150 words)
                - Detailed findings
                - Analysis and insights
                - Recommendations
                - Conclusion
                
                Format it as a polished professional report.
                Use clear, concise language.
                Organize information logically.
                """,
                expected_output="""
                A complete research report with:
                - Professional structure
                - Clear headings and sections
                - Well-organized content
                - Professional formatting
                - Proper citations
                """,
                agent=writer_agent,
                context=[research_task, analysis_task],
                async_execution=False
            )

            validation_task = Task(
                description=f"""
                Review and validate the final report on: {query}
                
                Check for:
                - Factual accuracy
                - Consistency and coherence
                - Completeness of information
                - Proper citations
                - Professional quality
                - Grammar and spelling
                
                Provide quality score and feedback.
                """,
                expected_output="""
                Validation report containing:
                - Quality assessment
                - Any issues found
                - Suggestions for improvement
                - Final quality score (0-100)
                """,
                agent=validator_agent,
                context=[research_task, analysis_task, writing_task],
                async_execution=False
            )

            # Create and execute crew
            crew = Crew(
                agents=[
                    researcher_agent,
                    analyzer_agent,
                    writer_agent,
                    validator_agent
                ],
                tasks=[
                    research_task,
                    analysis_task,
                    writing_task,
                    validation_task
                ],
                verbose=True,
                max_rpm=10
            )

            # Execute research
            result = crew.kickoff()

            # Store results
            research_report = ResearchReport(
                title=f"Research Report: {query[:50]}",
                topic=query,
                executive_summary="",
                findings=str(result),
                analysis="",
                recommendations="",
                sources=[],
                quality_score=0.85,
                timestamp=datetime.now().isoformat()
            )

            self.reports.append(research_report)

            # Save to memory
            save_to_memory(query, str(result), {
                "report_type": "research_report",
                "quality_score": research_report.quality_score
            })

            print(f"\n✅ Research completed successfully!")
            print(f"📊 Report saved to memory")

            return {
                "status": "success",
                "query": query,
                "result": str(result),
                "report_id": len(self.reports) - 1
            }

        except Exception as e:
            print(f"❌ Research failed: {str(e)}")
            return {
                "status": "failed",
                "query": query,
                "error": str(e)
            }

    def interactive_chat(self, user_message: str) -> str:
        """
        Engage in interactive conversation with context
        التفاعل مع محادثة ذكية مع السياق
        """
        # Get relevant context from memory if needed
        memory_context = search_memory(user_message, k=2)
        
        context_text = ""
        if memory_context:
            context_text = "\n\nRelevant previous research:\n"
            for doc, score in memory_context:
                context_text += f"- {doc.page_content[:200]}... (relevance: {score:.2f})\n"

        # Enhance user message with context
        enhanced_message = user_message + context_text if context_text else user_message

        # Get response from NeuroBot
        response = self.neurobot.chat(enhanced_message)

        # Store conversation
        self.conversation_log.append({
            "user": user_message,
            "bot": response,
            "timestamp": datetime.now().isoformat()
        })

        return response

    def get_research_summary(self) -> Dict:
        """
        Get summary of all conducted research
        الحصول على ملخص جميع الأبحاث التي تم إجراؤها
        """
        return {
            "project_name": self.project_name,
            "session_id": self.session_id,
            "total_reports": len(self.reports),
            "conversation_turns": len(self.conversation_log),
            "memory_documents": len(vector_store.get()['documents']) if vector_store else 0,
            "reports": [
                {
                    "topic": r.topic,
                    "quality_score": r.quality_score,
                    "timestamp": r.timestamp
                }
                for r in self.reports
            ]
        }

    def export_all_results(self, output_format: str = "json") -> str:
        """
        Export all results and conversations
        تصدير جميع النتائج والمحادثات
        """
        export_data = {
            "project_info": {
                "name": self.project_name,
                "session_id": self.session_id,
                "timestamp": datetime.now().isoformat()
            },
            "research_reports": [
                {
                    "topic": r.topic,
                    "title": r.title,
                    "findings": r.findings,
                    "quality_score": r.quality_score,
                    "timestamp": r.timestamp
                }
                for r in self.reports
            ],
            "conversations": self.conversation_log,
            "summary": self.get_research_summary()
        }

        if output_format == "json":
            return json.dumps(export_data, indent=2, ensure_ascii=False)
        elif output_format == "txt":
            return self._format_text_export(export_data)
        else:
            raise ValueError(f"Unsupported format: {output_format}")

    def _format_text_export(self, data: Dict) -> str:
        """Format export as text"""
        lines = [
            f"{'='*60}",
            f"Research Project: {data['project_info']['name']}",
            f"Session ID: {data['project_info']['session_id']}",
            f"{'='*60}\n"
        ]

        lines.append("RESEARCH REPORTS\n")
        for i, report in enumerate(data['research_reports'], 1):
            lines.append(f"\n{i}. {report['topic']}")
            lines.append(f"   Quality Score: {report['quality_score']}")
            lines.append(f"   Date: {report['timestamp']}")
            lines.append(f"   Findings: {report['findings'][:200]}...\n")

        lines.append("\n" + "="*60)
        lines.append("CONVERSATION LOG\n")
        for turn in data['conversations']:
            lines.append(f"User: {turn['user']}")
            lines.append(f"Bot: {turn['bot'][:200]}...\n")

        return "\n".join(lines)

    def save_session(self, filepath: str):
        """Save entire session to file"""
        data = {
            "project_info": {
                "name": self.project_name,
                "session_id": self.session_id
            },
            "reports": [
                {
                    "topic": r.topic,
                    "title": r.title,
                    "findings": r.findings,
                    "quality_score": r.quality_score,
                    "timestamp": r.timestamp
                }
                for r in self.reports
            ],
            "conversations": self.conversation_log
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"✅ Session saved to {filepath}")


# =========================
# Demo
# =========================

def demo_orchestrator():
    """Demo the orchestrator"""
    orchestrator = IntelligentResearchOrchestrator("AI Research Project")

    # Conduct research
    research_result = orchestrator.conduct_research(
        "What are the latest developments in Large Language Models?",
        num_iterations=1
    )

    # Interactive chat
    if research_result['status'] == 'success':
        print("\n💬 Starting interactive session...\n")
        response = orchestrator.interactive_chat(
            "Based on the research, what are the main trends?"
        )
        print(f"NeuroBot: {response}\n")

    # Get summary
    print("\n📊 Project Summary:")
    summary = orchestrator.get_research_summary()
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    demo_orchestrator()
