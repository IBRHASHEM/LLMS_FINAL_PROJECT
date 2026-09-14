# -*- coding: utf-8 -*-
"""
Intelligent Research Platform - Single File Version

Combined from:
- config_agents.py
- neurobot_chat.py
- orchestrator.py
- app.py

Run:
    streamlit run app_single.py
"""


# ==========================================================================
# MERGED MODULE: config_agents.py
# ==========================================================================

"""
Configuration file for all AI Agents
تكوين جميع وكلاء الذكاء الاصطناعي المتخصصة
"""
import crewai.llms.cache as _crewai_cache
from litellm import query
_crewai_cache.mark_cache_breakpoint = lambda msg: msg
from crewai import Agent, Task, Crew, LLM
from langchain_groq import ChatGroq
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.document_loaders import WebBaseLoader
from crewai.tools import tool
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import os
from dotenv import load_dotenv

load_dotenv()

# =========================
# LLM Configuration
# =========================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

llm = LLM(
    model="groq/openai/gpt-oss-20b",  # ✅ النموذج الصحيح
    temperature=0,
    max_tokens=800,
    api_key=GROQ_API_KEY,
)

llm_fast = LLM(
    model="groq/openai/gpt-oss-20b",  # ✅ النموذج الصحيح
    temperature=0.2,
    max_tokens=800,
    api_key=GROQ_API_KEY,
)
#=========================
# for testing the LLM connection
# =========================
# Tools Definition
# =========================

@tool
def web_search_tool(query: str) -> str:
    """
    Search the web for given query to find information
    البحث على الويب للعثور على معلومات محددة
    """
    try:
        search_tool = DuckDuckGoSearchRun()
        results = search_tool.run(query)
        if results and len(results.strip()) > 10:
            return results[:2500]
    except Exception as e:
        print(f"DuckDuckGo search error: {e}")
    return f"Live web search temporarily rate-limited or unavailable for query: '{query}'. Analysis will proceed based on foundational intelligence and supplied materials."


@tool
def web_scraper_tool(url: str) -> str:
    """
    Scrape a webpage using LangChain WebBaseLoader
    نسخ محتوى صفحة ويب
    """
    try:
        loader = WebBaseLoader(
            web_paths=(url,),
            header_template={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/131.0.0.0 Safari/537.36"
                )
            }
        )
        documents = loader.load()
        text = " ".join(doc.page_content for doc in documents)
        clean_text = " ".join(text.split())
        return clean_text[:2000]
    except Exception as e:
        return f"Scraping error: {str(e)}"


def extract_text_from_file(uploaded_file) -> str:
    """
    Extract text content from uploaded file (PDF, TXT, MD, CSV, JSON)
    استخراج النصوص من الملفات المرفوعة
    """
    filename = uploaded_file.name.lower()
    try:
        if filename.endswith(".pdf"):
            import pdfplumber
            import io
            text_parts = []
            with pdfplumber.open(io.BytesIO(uploaded_file.getvalue())) as pdf:
                for idx, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(f"--- [الصفحة {idx+1}] ---\n{page_text}")
            return "\n\n".join(text_parts) if text_parts else "ملف PDF فارغ أو يحتوي على صور ممسوحة ضوئياً فقط."
        elif filename.endswith((".txt", ".md", ".json", ".csv", ".py")):
            return uploaded_file.getvalue().decode("utf-8", errors="replace")
        else:
            return uploaded_file.getvalue().decode("utf-8", errors="replace")
    except Exception as e:
        return f"خطأ أثناء استخراج النص من الملف {filename}: {str(e)}"


@tool
def statistical_analyzer_tool(text: str) -> str:
    """
    Analyze text to extract quantitative metrics, statistics, percentages, dates, and trends.
    استخراج المؤشرات الإحصائية والأرقام والنسب المئوية والاتجاهات من النص
    """
    try:
        import re
        numbers = re.findall(r'(\d+(?:\.\d+)?%|\$\d+(?:\.\d+)?|\d+(?:\.\d+)?\s*(?:billion|million|trillion|USD|GB|TB|users|مليار|مليون|دولار|مستخدم|بالمئة|بالمائة))', text, re.IGNORECASE)
        dates = re.findall(r'\b(20\d{2}|19\d{2})\b', text)
        stats = []
        if numbers:
            stats.append("Key Metrics / أرقام ونسب رئيسية: " + ", ".join(list(dict.fromkeys(numbers))[:8]))
        if dates:
            stats.append("Key Years / تواريخ مفتاحية: " + ", ".join(sorted(list(set(dates)))))
        
        from groq import Groq
        groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        completion = groq_client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[{
                "role": "user",
                "content": f"Extract top 3-4 quantitative metrics, statistics, and trends from this content:\n\n{text[:2000]}"
            }],
            max_tokens=250,
            temperature=0.1
        )
        llm_insights = completion.choices[0].message.content.strip()
        stats.append("\nQuantitative Analysis / التحليل الكمي:\n" + llm_insights)
        return "\n".join(stats)
    except Exception as e:
        return f"Statistical summary: Quantitative data extracted. ({str(e)})"


@tool
def sentiment_and_tone_analyzer_tool(text: str) -> str:
    """
    Analyze sentiment, objectivity, tone, and source credibility level of the text.
    تحليل النبرة والمشاعر ومستوى الموضوعية ومصداقية المصادر
    """
    try:
        from groq import Groq
        groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        completion = groq_client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[{
                "role": "user",
                "content": f"Analyze the tone, objectivity, sentiment polarity, and credibility level of this content in 2-3 concise points:\n\n{text[:2000]}"
            }],
            max_tokens=200,
            temperature=0.1
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"Tone: Informative, analytical, objective. ({str(e)})"


@tool
def summarize_text_tool(text: str) -> str:
    """
    Summarize the given text quickly and accurately in Arabic or English.
    تلخيص النص بدقة وسرعة فائقة باللغتين العربية أو الإنجليزية
    """
    try:
        from groq import Groq
        groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        completion = groq_client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[{
                "role": "user",
                "content": f"Provide a concise executive summary of the following text with key takeaways:\n\n{text[:2500]}"
            }],
            max_tokens=300,
            temperature=0.2
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 15]
        return ". ".join(sentences[:3]) + "." if sentences else text[:300]


# =========================
# Vector Store for Memory
# =========================

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vector_store = Chroma(
    collection_name='research_memories',
    embedding_function=embeddings,
    persist_directory='./memory_db'
)


# =========================
# Agents Definition
# =========================
researcher_agent = Agent(
    role="Research Results Analyst",
    goal="Analyze the supplied search results and documents accurately to extract reliable facts",
    backstory="""
    You are an expert research analyst.
    Your job is to analyze search results and documents that are provided to you.
    You rely only on the supplied facts and documents without inventing details.
    You extract key facts, relevant data points, and documented sources.
    
    أنت باحث خبير تحلل نتائج البحث والوثائق بدقة وتستخرج الحقائق الموثوقة.
    """,
    tools=[],
    llm=llm,
    max_iter=1,
    allow_delegation=False,
    verbose=True
)

analyzer_agent = Agent(
    role="Data & Sentiment Analyst",
    goal="Perform critical quantitative, statistical, and sentiment analysis on research findings",
    backstory="""
    You are an expert data analyst and critical evaluator with deep expertise in pattern recognition.
    You extract quantitative metrics, percentages, timeline dates, and trends.
    You evaluate the objectivity, sentiment, and reliability of the data sources.
    You organize complex insights into clear analytical structures.
    
    أنت محلل بيانات ونبرة متمرس متخصص في فحص النتائج واستخراج الإحصائيات والأرقام وتقييم الموثوقية والموضوعية.
    """,
    tools=[statistical_analyzer_tool, sentiment_and_tone_analyzer_tool],
    llm=llm,
    max_iter=2,
    allow_delegation=False,
    verbose=True
)
#==========================

writer_agent = Agent(
    role="Report Writer",
    goal="Create clear, professional, and well-structured reports",
    backstory="""
    You are an experienced technical writer specializing in research reports.
    You take analyzed data and create compelling, well-organized documents.
    You use clear language, proper formatting, and logical flow.
    You ensure all claims are backed by evidence and properly cited.
    You adapt your writing style to the audience and purpose.
    
    أنت كاتب تقني متمرس متخصص في تقارير البحث.
    تأخذ البيانات المحللة وتنشئ وثائق منظمة بشكل جيد.
    """,
    tools=[summarize_text_tool],
    llm=llm,
    max_iter=2,
    allow_delegation=False,
    verbose=True
)


validator_agent = Agent(
    role="Quality Assurance Specialist",
    goal="Validate and ensure quality, accuracy, and completeness of all outputs",
    backstory="""
    You are a meticulous quality assurance expert with high standards.
    You review all information for accuracy, completeness, and consistency.
    You check for factual errors, logical inconsistencies, and missing information.
    You provide constructive feedback and suggest improvements.
    You ensure all outputs meet professional standards.
    
    أنت متخصص ضمان الجودة دقيق جداً بمعايير عالية.
    تراجع كل المعلومات للتحقق من الدقة والكمال والاتساق.
    """,
    llm=llm_fast,
    max_iter=2,
    allow_delegation=False,
    verbose=True
)


# =========================
# Memory Management Functions
# =========================

def save_to_memory(topic: str, content: str, metadata: dict = None):
    """
    Save research results to vector memory for future retrieval
    حفظ نتائج البحث في الذاكرة المتجهة
    """
    from langchain_core.documents import Document
    
    doc = Document(
        page_content=content,
        metadata={
            "topic": topic,
            "type": "research_output",
            **(metadata or {})
        }
    )
    vector_store.add_documents([doc])
    return True


def search_memory(query: str, k: int = 3):
    """
    Search previous research in memory
    البحث عن الأبحاث السابقة في الذاكرة
    """
    try:
        results = vector_store.similarity_search_with_score(query, k=k)
        return results
    except Exception as e:
        print(f"Memory search error: {e}")
        return []


# =========================
# Crew Configuration
# =========================

def create_research_crew():
    """
    Create a complete research crew with all agents
    إنشاء فريق بحث متكامل مع جميع الوكلاء
    """
    crew = Crew(
        agents=[researcher_agent, analyzer_agent, writer_agent, validator_agent],
        verbose=True,
        max_rpm=10
    )
    return crew


# =========================
# Export
# =========================

__all__ = [
    'researcher_agent',
    'analyzer_agent',
    'writer_agent',
    'validator_agent',
    'create_research_crew',
    'save_to_memory',
    'search_memory',
    'vector_store',
    'llm',
    'llm_fast'
]

#=========================
# 
#test
# print("\n" + "=" * 70)
# print("DIRECT RESEARCH AGENT TEST")
# print("=" * 70)
# 
# test_prompt = """
# Analyze the following research topic:
# 
# ML & LLMs
# 
# Use ONLY the following information:
# 
# 1. MLX is Apple's machine learning framework.
# 2. Ollama allows users to run language models locally.
# 3. llama.cpp provides CPU and GPU inference for language models.
# 4. vLLM is designed for high-throughput LLM inference.
# 5. LLMs are deep learning models trained on large amounts of data.
# 
# Rules:
# - Do not use tools.
# - Do not search the web.
# - Do not invent information.
# 
# Return exactly 5 short bullet points.
# """
# 
# try:
    # direct_result = researcher_agent.llm.call(
        # messages=[
            # {
                # "role": "user",
                # "content": test_prompt
            # }
        # ]
    # )
# 
    # print("\nDIRECT LLM RESULT:")
    # print(repr(direct_result))
    # print("=" * 70)
# 
# except Exception as e:
    # print("\nDIRECT LLM ERROR:")
    # print(type(e).__name__)
    # print(str(e))

# ==========================================================================
# MERGED MODULE: neurobot_chat.py
# ==========================================================================

"""
NeuroBot - Intelligent Conversational AI with Context Awareness
نظام محادثة ذكي مع تذكر السياق والسجل
"""

from google import genai
from google.genai import types
import json
import os
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from dotenv import load_dotenv

load_dotenv()

# =========================
# Configuration
# =========================

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MODEL_ID = "gemini-3.6-flash"

client = genai.Client(api_key=GOOGLE_API_KEY)


@dataclass
class ConversationMessage:
    """Data class for storing conversation messages"""
    role: str  # "user" or "assistant"
    content: str
    timestamp: str
    tokens: Optional[Dict] = None


class NeuroBot:
    """
    NeuroBot - Intelligent conversational AI system
    نظام NeuroBot الذكي للمحادثة
    """

    def __init__(self, user_name: str = "User"):
        """Initialize NeuroBot with user context"""
        self.user_name = user_name
        self.conversation_history: List[ConversationMessage] = []
        self.session_start = datetime.now().isoformat()
        self.system_instruction = """
        You are NeuroBot, an intelligent AI assistant designed for research and analysis.
        
        Your capabilities:
        1. Remember the entire conversation history
        2. Understand context and nuance in user questions
        3. Provide accurate, well-structured responses
        4. Ask clarifying questions when needed
        5. Adapt your response style to the user's preferences
        6. Maintain consistency across the conversation
        
        Rules:
        - Always be helpful, harmless, and honest
        - Cite sources when providing factual information
        - Admit when you don't know something
        - Respect user privacy and preferences
        - Provide clear, structured responses
        
        أنت NeuroBot، مساعد ذكي متخصص في البحث والتحليل.
        
        قدراتك:
        1. تذكر محتوى المحادثة كاملاً
        2. فهم السياق والتفاصيل الدقيقة
        3. تقديم إجابات دقيقة ومنظمة
        4. طرح أسئلة توضيحية عند الحاجة
        5. التكيف مع تفضيلات المستخدم
        """

    def _build_conversation_context(self, new_message: str) -> List[Dict]:
        """
        Build the full conversation context including history
        بناء سياق المحادثة الكامل بما فيه السجل
        """
        contents = []
        
        # Add previous messages
        for msg in self.conversation_history:
            contents.append({
                "role": msg.role,
                "parts": [{"text": msg.content}]
            })
        
        # Add new message
        contents.append({
            "role": "user",
            "parts": [{"text": new_message}]
        })
        
        return contents

    def chat(self, user_message: str, attached_doc_text: Optional[str] = None, use_memory_search: bool = True) -> str:
        """
        Process user message and generate response with optional document context and memory search
        معالجة رسالة المستخدم وتوليد الرد مع دعم المستندات والذاكرة
        """
        try:
            # Augment with semantic memory if relevant
            memory_context = ""
            if use_memory_search:
                mem_results = search_memory(user_message, k=2)
                if mem_results:
                    mem_snippets = []
                    for doc, score in mem_results:
                        topic_name = doc.metadata.get('topic', 'General Research')
                        mem_snippets.append(f"- [بحث سابق: {topic_name}]: {doc.page_content[:350]}...")
                    if mem_snippets:
                        memory_context = "\n\n📚 [سياق من الأبحاث السابقة المخزنة في الذاكرة]:\n" + "\n".join(mem_snippets)

            full_prompt = user_message
            if attached_doc_text:
                full_prompt = f"📄 [المستند المرفق من المستخدم]:\n{attached_doc_text[:4000]}\n\n❓ سؤال/طلب المستخدم:\n{user_message}"
            
            if memory_context:
                full_prompt += memory_context

            # Build conversation context
            contents = self._build_conversation_context(full_prompt)
            
            # Generate response
            response = client.models.generate_content(
                model=MODEL_ID,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_instruction,
                    temperature=0.7,
                    top_p=0.9,
                    top_k=40,
                    max_output_tokens=2048,
                )
            )
            
            assistant_response = response.text
            
            # Store in history
            self.conversation_history.append(
                ConversationMessage(
                    role="user",
                    content=user_message + (f" 📎 (مع ملف مرفق)" if attached_doc_text else ""),
                    timestamp=datetime.now().isoformat(),
                    tokens={"prompt": len(user_message.split())}
                )
            )
            
            self.conversation_history.append(
                ConversationMessage(
                    role="assistant",
                    content=assistant_response,
                    timestamp=datetime.now().isoformat(),
                    tokens={
                        "completion": len(assistant_response.split())
                    }
                )
            )
            
            return assistant_response
            
        except Exception as e:
            error_msg = f"Error in NeuroBot: {str(e)}"
            print(error_msg)
            return error_msg

    def clear_history(self):
        """Clear conversation history for new session"""
        self.conversation_history = []
        self.session_start = datetime.now().isoformat()

    def get_conversation_summary(self) -> Dict:
        """
        Get a summary of the current conversation
        الحصول على ملخص المحادثة الحالية
        """
        return {
            "user": self.user_name,
            "session_start": self.session_start,
            "message_count": len(self.conversation_history),
            "last_message": (
                self.conversation_history[-1].timestamp
                if self.conversation_history
                else None
            ),
            "total_tokens": sum(
                sum(msg.tokens.values()) if msg.tokens else 0
                for msg in self.conversation_history
            )
        }

    def get_conversation_context(self, max_messages: int = 10) -> str:
        """
        Get recent conversation context as a string
        الحصول على السياق الحديث للمحادثة
        """
        recent = self.conversation_history[-max_messages:] if self.conversation_history else []
        
        context_lines = []
        for msg in recent:
            role_label = "You" if msg.role == "user" else "NeuroBot"
            context_lines.append(f"{role_label}: {msg.content}\n")
        
        return "\n".join(context_lines)

    def save_conversation(self, filepath: str):
        """Save conversation to JSON file"""
        data = {
            "user": self.user_name,
            "session_start": self.session_start,
            "messages": [asdict(msg) for msg in self.conversation_history]
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"Conversation saved to {filepath}")

    def load_conversation(self, filepath: str):
        """Load conversation from JSON file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.user_name = data.get("user", "User")
        self.session_start = data.get("session_start")
        
        for msg_data in data.get("messages", []):
            msg = ConversationMessage(
                role=msg_data["role"],
                content=msg_data["content"],
                timestamp=msg_data["timestamp"],
                tokens=msg_data.get("tokens")
            )
            self.conversation_history.append(msg)
        
        print(f"Conversation loaded from {filepath}")

    def export_conversation(self, output_format: str = "md") -> str:
        """
        Export conversation in different formats (markdown, txt, html)
        تصدير المحادثة بصيغ مختلفة
        """
        if output_format == "md":
            return self._export_markdown()
        elif output_format == "txt":
            return self._export_text()
        elif output_format == "html":
            return self._export_html()
        else:
            raise ValueError(f"Unsupported format: {output_format}")

    def _export_markdown(self) -> str:
        """Export as markdown"""
        lines = [
            f"# Conversation with NeuroBot",
            f"## Session: {self.session_start}",
            f"## User: {self.user_name}",
            f"---\n"
        ]
        
        for msg in self.conversation_history:
            prefix = "**You:**" if msg.role == "user" else "**NeuroBot:**"
            lines.append(f"\n{prefix}\n\n{msg.content}\n")
        
        return "\n".join(lines)

    def _export_text(self) -> str:
        """Export as plain text"""
        lines = [
            f"Conversation with NeuroBot",
            f"Session: {self.session_start}",
            f"User: {self.user_name}",
            f"{'='*60}\n"
        ]
        
        for msg in self.conversation_history:
            prefix = "USER" if msg.role == "user" else "NEUROBOT"
            lines.append(f"[{prefix}] {msg.content}\n")
        
        return "\n".join(lines)

    def _export_html(self) -> str:
        """Export as HTML"""
        html = f"""
        <html>
        <head>
            <meta charset="utf-8">
            <title>NeuroBot Conversation</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .metadata {{ background: #f0f0f0; padding: 10px; border-radius: 5px; }}
                .message {{ margin: 15px 0; padding: 10px; border-left: 3px solid #007bff; }}
                .user {{ border-left-color: #28a745; background: #e8f5e9; }}
                .assistant {{ border-left-color: #007bff; background: #e3f2fd; }}
                .label {{ font-weight: bold; }}
            </style>
        </head>
        <body>
            <h1>NeuroBot Conversation</h1>
            <div class="metadata">
                <p><strong>User:</strong> {self.user_name}</p>
                <p><strong>Session:</strong> {self.session_start}</p>
                <p><strong>Total Messages:</strong> {len(self.conversation_history)}</p>
            </div>
        """
        
        for msg in self.conversation_history:
            css_class = "user" if msg.role == "user" else "assistant"
            label = "You" if msg.role == "user" else "NeuroBot"
            html += f"""
            <div class="message {css_class}">
                <p class="label">{label} ({msg.timestamp})</p>
                <p>{msg.content}</p>
            </div>
            """
        
        html += "</body></html>"
        return html


# =========================
# Demo Function
# =========================

def demo_neurobot():
    """Demo NeuroBot functionality"""
    bot = NeuroBot(user_name="عمرو")
    
    print("🤖 NeuroBot - Demo Session")
    print("=" * 60)
    
    # Sample conversation
    questions = [
        "ما هي الشبكات العصبية؟",
        "كيف تعمل شبكات المحولات (Transformers)؟",
        "ما الفرق بين BERT و GPT؟"
    ]
    
    for question in questions:
        print(f"\n📝 You: {question}")
        response = bot.chat(question)
        print(f"🤖 NeuroBot: {response}\n")
        print("-" * 60)
    
    # Show summary
    print("\n📊 Conversation Summary:")
    summary = bot.get_conversation_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    # Export conversation
    bot.save_conversation("conversation_demo.json")
    print("\n✅ Conversation saved to conversation_demo.json")

# ==========================================================================
# MERGED MODULE: orchestrator.py
# ==========================================================================

"""
Main Orchestrator - Coordinates all systems and components
المنسق الرئيسي - ينسق جميع الأنظمة والمكونات
"""

from crewai import Task, Crew
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import json
import os

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


def generate_mermaid_mindmap(topic: str, summary: str = "") -> str:
    """
    Generate a clean Mermaid.js flowchart for the research topic
    توليد مخطط انسيابي تفاعلي للموضوع
    """
    try:
        from groq import Groq
        groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        completion = groq_client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[{
                "role": "user",
                "content": f"""Generate a valid Mermaid.js flowchart (graph TD) summarizing this topic and its 4-5 core subtopics.
Wrap node labels in double quotes. Do NOT use unquoted special characters.
Return ONLY valid Mermaid code inside ```mermaid ... ```.
Topic: {topic}
Summary: {summary[:800]}"""
            }],
            max_tokens=600,
            temperature=0.2
        )
        msg = completion.choices[0].message
        content = msg.content or getattr(msg, 'reasoning', '')
        if "```mermaid" in content:
            code = content.split("```mermaid")[1].split("```")[0].strip()
            return code
        elif "graph TD" in content or "graph LR" in content:
            return content.replace("```", "").strip()
        else:
            clean_t = topic.replace('"', '').strip()
            return f"""graph TD
    Root["{clean_t[:35]}"] --> A["النتائج الرئيسية / Key Findings"]
    Root --> B["البيانات والاتجاهات / Data & Trends"]
    Root --> C["الرؤى الاستراتيجية / Strategic Insights"]
    Root --> D["التوصيات العملية / Action Plan"]
    A --> A1["أدلة وحقائق مثبتة"]
    B --> B1["مؤشرات كمية"]
    C --> C1["تقييم الأثر"]
    D --> D1["خطوات التنفيذ"]"""
    except Exception:
        clean_t = topic.replace('"', '').strip()
        return f"""graph TD
    Root["{clean_t[:35]}"] --> A["النتائج الرئيسية"]
    Root --> B["التحليل والبيانات"]
    Root --> C["التوصيات"]"""


def generate_styled_html_report(topic: str, report_text: str, validation_text: str = "", timestamp: str = "") -> str:
    """
    Generate a high-end, print-ready styled HTML report
    توليد تقرير HTML مصمم وفاخر جاهز للطباعة المباشرة كـ PDF
    """
    import html
    clean_topic = html.escape(topic)
    
    lines = report_text.splitlines()
    body_html = []
    in_list = False
    
    for line in lines:
        line_s = line.strip()
        if line_s.startswith("# "):
            if in_list:
                body_html.append("</ul>")
                in_list = False
            body_html.append(f"<h1>{html.escape(line_s[2:])}</h1>")
        elif line_s.startswith("## "):
            if in_list:
                body_html.append("</ul>")
                in_list = False
            body_html.append(f"<h2>{html.escape(line_s[3:])}</h2>")
        elif line_s.startswith("### "):
            if in_list:
                body_html.append("</ul>")
                in_list = False
            body_html.append(f"<h3>{html.escape(line_s[4:])}</h3>")
        elif line_s.startswith("- ") or line_s.startswith("* "):
            if not in_list:
                body_html.append("<ul>")
                in_list = True
            body_html.append(f"<li>{html.escape(line_s[2:])}</li>")
        elif line_s:
            if in_list:
                body_html.append("</ul>")
                in_list = False
            body_html.append(f"<p>{html.escape(line_s)}</p>")
            
    if in_list:
        body_html.append("</ul>")
        
    formatted_body = "\n".join(body_html)
    
    return f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<title>{clean_topic} - NeuroResearch Report</title>
<link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&family=Outfit:wght@400;600;700&display=swap" rel="stylesheet">
<style>
    @media print {{
        .no-print {{ display: none !important; }}
        body {{ background: #ffffff !important; color: #1e293b !important; padding: 0 !important; }}
        .report-box {{ border: none !important; box-shadow: none !important; background: transparent !important; }}
        h1 {{ color: #0f172a !important; }}
        h2 {{ color: #2563eb !important; }}
        p, li {{ color: #334155 !important; }}
    }}
    body {{
        font-family: 'Cairo', 'Outfit', sans-serif;
        background: #0b0f19;
        color: #e2e8f0;
        margin: 0;
        padding: 40px 20px;
        line-height: 1.8;
    }}
    .report-container {{
        max-width: 900px;
        margin: 0 auto;
    }}
    .no-print-bar {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 24px;
        background: rgba(30, 41, 59, 0.85);
        padding: 14px 24px;
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.1);
        backdrop-filter: blur(12px);
    }}
    .print-btn {{
        background: linear-gradient(135deg, #6366f1, #06b6d4);
        color: white;
        border: none;
        padding: 10px 24px;
        border-radius: 8px;
        font-weight: 700;
        cursor: pointer;
        font-family: inherit;
        font-size: 0.95rem;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
    }}
    .report-box {{
        background: #111827;
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 20px;
        padding: 48px;
        box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5);
    }}
    .header-badge {{
        display: inline-block;
        background: rgba(99, 102, 241, 0.15);
        color: #818cf8;
        border: 1px solid rgba(99, 102, 241, 0.3);
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 700;
        margin-bottom: 16px;
    }}
    h1 {{
        font-size: 2.2rem;
        font-weight: 800;
        color: #ffffff;
        margin-top: 0;
        border-bottom: 2px solid rgba(99, 102, 241, 0.4);
        padding-bottom: 16px;
    }}
    h2 {{
        font-size: 1.45rem;
        font-weight: 700;
        color: #38bdf8;
        margin-top: 32px;
        border-right: 4px solid #6366f1;
        padding-right: 12px;
    }}
    h3 {{
        font-size: 1.15rem;
        font-weight: 600;
        color: #a855f7;
    }}
    p {{
        margin-bottom: 14px;
        color: #cbd5e1;
    }}
    ul {{
        padding-right: 24px;
        margin-bottom: 18px;
    }}
    li {{
        margin-bottom: 8px;
        color: #cbd5e1;
    }}
    .qa-box {{
        background: rgba(16, 185, 129, 0.08);
        border: 1px solid rgba(16, 185, 129, 0.25);
        border-radius: 12px;
        padding: 20px;
        margin-top: 30px;
    }}
    .meta-footer {{
        margin-top: 40px;
        border-top: 1px solid rgba(255,255,255,0.1);
        padding-top: 20px;
        font-size: 0.85rem;
        color: #64748b;
        display: flex;
        justify-content: space-between;
    }}
</style>
</head>
<body>
<div class="report-container">
    <div class="no-print-bar no-print">
        <span style="font-weight: 700; color: #38bdf8; font-size: 1.05rem;">🧬 تقرير منصة البحث والتحليل الذكي (NeuroResearch AI)</span>
        <button class="print-btn" onclick="window.print()">🖨️ طباعة / حفظ كـ PDF</button>
    </div>
    <div class="report-box">
        <div class="header-badge">AI MULTI-AGENT VERIFIED REPORT</div>
        <div class="meta-footer" style="margin-top: 0; border: none; padding-bottom: 20px;">
            <span>📅 تاريخ التوليد: {timestamp or datetime.now().strftime("%Y-%m-%d %H:%M")}</span>
            <span>🛡️ نظام التدقيق: 4 Autonomous AI Agents Verified</span>
        </div>
        {formatted_body}
        
        {f'<div class="qa-box"><b style="color: #10b981;">🛡️ ملخص تدقيق الجودة (QA Verification):</b><p style="margin-top: 6px; font-size: 0.95rem;">{html.escape(validation_text)}</p></div>' if validation_text else ''}

        <div class="meta-footer">
            <span>منصة البحث والتحليل الذكي &copy; 2026</span>
            <span>Powered by Groq LLMs, CrewAI & ChromaDB</span>
        </div>
    </div>
</div>
</body>
</html>"""


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

    def update_llm(self, model_name: str, temperature: float = 0.2):
        """Update LLM across all agents dynamically"""
        try:
            new_llm = LLM(
                model=f"groq/{model_name}",
                temperature=temperature,
                max_tokens=1500,
                api_key=GROQ_API_KEY
            )
            researcher_agent.llm = new_llm
            analyzer_agent.llm = new_llm
            writer_agent.llm = new_llm
            validator_agent.llm = new_llm
            print(f"✅ Dynamic LLM updated to {model_name} with temp {temperature}")
        except Exception as e:
            print(f"⚠️ Error updating LLM: {e}")

    def conduct_research(self, query: str, source_mode: str = "web", doc_content: str = "", doc_filename: str = "") -> Dict:
        """
        Conduct comprehensive research using all agents with support for web, uploaded documents, or hybrid mode.
        إجراء بحث شامل باستخدام جميع الوكلاء مع دعم الويب والمستندات والبحث الهجين
        """
        print(f"\n{'='*60}")
        print(f"🔍 Starting Research [{source_mode.upper()}]: {query}")
        print(f"{'='*60}\n")

        try:
            # Source aggregation
            if source_mode == "web":
                raw_sources = web_search_tool.run(query)
                data_header = f"Web Search Data for '{query}'"
            elif source_mode == "doc":
                raw_sources = f"--- CONTENT FROM UPLOADED DOCUMENT ({doc_filename}) ---\n{doc_content[:4500]}"
                data_header = f"Uploaded Document '{doc_filename}'"
            else:  # hybrid
                web_part = web_search_tool.run(query)
                raw_sources = f"--- UPLOADED DOCUMENT ({doc_filename}) ---\n{doc_content[:2500]}\n\n--- WEB SEARCH RESULTS ---\n{web_part[:2000]}"
                data_header = f"Hybrid Multi-Source ({doc_filename} + Web)"

            print("\n" + "=" * 70)
            print("RESEARCH SOURCES PREPARED")
            print("=" * 70)
            print(f"Found {len(raw_sources)} characters of data ({source_mode})")
            print("=" * 70)

            # Define tasks for each agent
            research_task = Task(
                description=f"""
                Analyze the following research inquiry:
                {query}

                Source Information ({data_header}):
                --- DATA SOURCES ---
                {raw_sources}
                --- END DATA SOURCES ---

                Extract key empirical findings, factual data points, and documented sources.
                Never invent details. Provide a structured research summary.
                """,
                expected_output="""
                A comprehensive research summary including:
                1. Main findings and discoveries
                2. Key points and insights
                3. Relevant sources and citations
                4. Analysis of the core subject
                """,
                agent=researcher_agent
            )

            analysis_task = Task(
                description=f"""
                Based on the research findings for '{query}', conduct a comprehensive quantitative, statistical, and sentiment analysis:
                1. Quantitative figures, metrics, percentages, timeline dates, and trends.
                2. Sentiment polarity, objectivity, tone, and source credibility level.
                3. Key patterns, strategic implications, and identified research gaps.
                You may invoke your analytical tools (statistical_analyzer_tool, sentiment_and_tone_analyzer_tool).
                """,
                expected_output="""
                Detailed analytical assessment covering:
                - Key quantitative metrics & trends
                - Sentiment, objectivity, and credibility evaluation
                - Critical assessment of findings & strategic implications
                - Recommendations for future exploration
                """,
                agent=analyzer_agent,
                context=[research_task]
            )

            writing_task = Task(
                description=f"""
                Create a high-impact, professional executive research report about '{query}' based on:
                1. The research findings
                2. The detailed quantitative and sentiment analysis
                
                Structure the report with standard professional markdown formatting:
                # {query}
                ## 1. Executive Summary (الملخص التنفيذي)
                ## 2. Key Findings & Quantitative Data (النتائج والبيانات الكمية)
                ## 3. In-Depth Analysis & Trends (التحليل المعمق والاتجاهات)
                ## 4. Strategic Recommendations & Action Plan (التوصيات وخطة العمل)
                ## 5. Potential Risks & Limitations (المخاطر والقيود)
                ## 6. Sources & References (المصادر والمراجع)
                
                Ensure the language (Arabic / English) reflects and matches the language of the prompt.
                """,
                expected_output="""
                A well-formatted, professional executive research report including all sections
                and proper citations of sources.
                """,
                agent=writer_agent,
                context=[research_task, analysis_task]
            )

            validation_task = Task(
                description=f"""
                Audit and validate the research report about '{query}' against the supplied sources:
                1. Fact-check consistency with the provided sources.
                2. Check logical flow and formatting rigor.
                3. Assign an overall Quality & Confidence Score (0-100).
                4. Highlight any recommendations for improvement or further verification.
                """,
                expected_output="""
                Validation scorecard with:
                - Quality score (0-100)
                - List of verified assertions or issues found
                - Constructive recommendations for quality
                """,
                agent=validator_agent,
                context=[writing_task]
            )

            # Create and run crew
            crew = Crew(
                agents=[researcher_agent, analyzer_agent, writer_agent, validator_agent],
                tasks=[research_task, analysis_task, writing_task, validation_task],
                verbose=True,
                max_rpm=10
            )

            print("\n🚀 Starting crew execution...")
            result = crew.kickoff()
            print("\n✅ Research completed successfully!")

            # Collect agent outputs
            research_report = str(writing_task.output)
            validation_report = str(validation_task.output)
            analysis_report = str(analysis_task.output)

            # Generate Mermaid mindmap diagram
            mermaid_code = generate_mermaid_mindmap(query, research_report)

            # Save the actual research report to memory
            save_to_memory(
                query,
                research_report,
                metadata={"source_mode": source_mode, "doc_name": doc_filename}
            )

            # Store result
            research_result = ResearchResult(
                topic=query,
                query=query,
                source_url=f"{source_mode.capitalize()} ({doc_filename if doc_filename else 'Web Search'})",
                content=research_report[:500],
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                relevance_score=0.96
            )
            self.research_results.append(research_result)

            return {
                'status': 'success',
                'result': research_report,
                'validation_report': validation_report,
                'analysis_report': analysis_report,
                'mermaid_diagram': mermaid_code,
                'raw_sources': raw_sources,
                'source_mode': source_mode,
                'doc_filename': doc_filename,
                'query': query,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

        except Exception as e:
            print(f"\n❌ Research failed: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'query': query,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

    def interactive_chat(self, user_input: str) -> str:
        """
        Interactive chat with NeuroBot
        محادثة تفاعلية مع NeuroBot
        """
        try:
            print(f"\n💬 User: {user_input}")
            response = self.neurobot.chat(user_input)
            print(f"🤖 NeuroBot: {response[:100]}...")
            
            self.conversation_log.append({
                'user': user_input,
                'bot': response,
                'timestamp': datetime.now().isoformat()
            })
            
            return response
        except Exception as e:
            print(f"\n❌ Chat failed: {str(e)}")
            error_message = f"Error: {str(e)}"
            
            self.conversation_log.append({
                'user': user_input,
                'bot': error_message,
                'timestamp': datetime.now().isoformat()
            })
            
            return error_message

    def get_research_summary(self) -> Dict:
        """Get summary of all research conducted"""
        return {
            'total_reports': len(self.reports),
            'total_research': len(self.research_results),
            'conversations': len(self.conversation_log),
            'session_id': self.session_id,
            'timestamp': datetime.now().isoformat()
        }

    def save_session(self, filepath: str):
        """Save session to JSON file"""
        try:
            session_data = {
                'project_name': self.project_name,
                'session_id': self.session_id,
                'research_results': [
                    {
                        'topic': r.topic,
                        'query': r.query,
                        'timestamp': r.timestamp,
                        'relevance_score': r.relevance_score
                    }
                    for r in self.research_results
                ],
                'conversation_count': len(self.conversation_log),
                'last_saved': datetime.now().isoformat()
            }
            
            os.makedirs(os.path.dirname(filepath) or '.', exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Session saved to {filepath}")
        except Exception as e:
            print(f"❌ Failed to save session: {str(e)}")

    def load_session(self, filepath: str):
        """Load session from JSON file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            self.project_name = session_data.get('project_name', self.project_name)
            self.session_id = session_data.get('session_id', self.session_id)
            
            print(f"✅ Session loaded from {filepath}")
        except Exception as e:
            print(f"❌ Failed to load session: {str(e)}")


def demo_orchestrator():
    """Demo function for testing"""
    print("\n" + "="*60)
    print("🤖 Intelligent Research Orchestrator - Demo")
    print("="*60 + "\n")
    
    try:
        orchestrator = IntelligentResearchOrchestrator("Demo Project")
        
        # Demo research
        print("📚 Conducting sample research...")
        # result = orchestrator.conduct_research("Artificial Intelligence")
        # print(f"Result: {result['status']}\n")
        
        # Demo chat
        print("💬 Starting chat demo...")
        response = orchestrator.interactive_chat("Hello! What is AI?")
        print(f"✅ Response received\n")
        
        # Summary
        summary = orchestrator.get_research_summary()
        print(f"📊 Session Summary:")
        print(json.dumps(summary, indent=2))
        
    except Exception as e:
        print(f"❌ Demo error: {str(e)}")

# ==========================================================================
# MERGED MODULE: app.py (Modern Glassmorphism UI)
# ==========================================================================

"""
Streamlit App - Modern High-End UI for Intelligent Document Analysis & Research Platform
واجهة عصرية متطورة لنظام تحليل الوثائق والبحث الذكي باستخدام وكلاء الذكاء الاصطناعي
"""

import streamlit as st
import json
import os
import pandas as pd
import altair as alt
from datetime import datetime

SESSION_FILE = os.path.join(os.path.dirname(__file__), "conversations", "current_session.json")

# =========================
# Page Configuration
# =========================

st.set_page_config(
    page_title="Intelligent Research Platform | منصة البحث والتحليل الذكي",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# Modern Glassmorphic CSS Theme
# =========================
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&family=Outfit:wght@400;500;600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">

<style>
    /* Global Typography & Palette */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', 'Cairo', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #e2e8f0;
    }
    
    /* Background Gradient */
    .stApp {
        background: radial-gradient(circle at 15% 15%, rgba(99, 102, 241, 0.08) 0%, transparent 40%),
                    radial-gradient(circle at 85% 20%, rgba(6, 182, 212, 0.07) 0%, transparent 40%),
                    radial-gradient(circle at 50% 80%, rgba(168, 85, 247, 0.06) 0%, transparent 50%),
                    #0b0f19;
    }

    /* Hero Banner Container */
    .hero-container {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.8) 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 32px 36px;
        margin-bottom: 24px;
        box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(16px);
        position: relative;
        overflow: hidden;
    }
    .hero-container::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; height: 3px;
        background: linear-gradient(90deg, #6366f1, #06b6d4, #10b981);
    }
    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(99, 102, 241, 0.15);
        color: #818cf8;
        border: 1px solid rgba(99, 102, 241, 0.3);
        padding: 6px 14px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin-bottom: 12px;
    }
    .hero-title {
        font-size: 2.5rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        background: linear-gradient(135deg, #ffffff 30%, #cbd5e1 70%, #94a3b8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 8px;
    }
    .hero-subtitle {
        color: #94a3b8;
        font-size: 1.05rem;
        line-height: 1.6;
        max-width: 850px;
    }

    /* KPI Cards */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 16px;
        margin-bottom: 24px;
    }
    .kpi-card {
        background: linear-gradient(145deg, rgba(30, 41, 59, 0.6) 0%, rgba(15, 23, 42, 0.7) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 20px;
        backdrop-filter: blur(12px);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        box-shadow: 0 10px 25px -10px rgba(0,0,0,0.3);
    }
    .kpi-card:hover {
        transform: translateY(-3px);
        border-color: rgba(99, 102, 241, 0.4);
        box-shadow: 0 15px 30px -10px rgba(99, 102, 241, 0.2);
    }
    .kpi-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
    }
    .kpi-title {
        color: #94a3b8;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .kpi-icon {
        font-size: 1.4rem;
        padding: 8px;
        border-radius: 10px;
        background: rgba(255, 255, 255, 0.05);
    }
    .kpi-value {
        font-size: 2rem;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: -0.02em;
    }
    .kpi-subtext {
        font-size: 0.8rem;
        color: #64748b;
        margin-top: 4px;
    }

    /* AI Agent Fleet Cards */
    .agent-card {
        background: linear-gradient(145deg, rgba(30, 41, 59, 0.5) 0%, rgba(15, 23, 42, 0.6) 100%);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 18px;
        padding: 22px;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .agent-card:hover {
        border-color: rgba(6, 182, 212, 0.4);
        transform: translateY(-4px);
        box-shadow: 0 16px 32px -12px rgba(6, 182, 212, 0.2);
    }
    .agent-header {
        display: flex;
        align-items: center;
        gap: 14px;
        margin-bottom: 14px;
    }
    .agent-avatar {
        width: 48px;
        height: 48px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        background: linear-gradient(135deg, rgba(99,102,241,0.2) 0%, rgba(6,182,212,0.2) 100%);
        border: 1px solid rgba(255,255,255,0.1);
    }
    .agent-role {
        font-size: 1.1rem;
        font-weight: 700;
        color: #f8fafc;
        margin: 0;
    }
    .agent-spec {
        font-size: 0.8rem;
        color: #06b6d4;
        font-weight: 600;
    }
    .agent-desc {
        color: #94a3b8;
        font-size: 0.85rem;
        line-height: 1.5;
        margin-bottom: 16px;
        flex-grow: 1;
    }
    .agent-pill-container {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
    }
    .agent-pill {
        background: rgba(255, 255, 255, 0.05);
        color: #cbd5e1;
        font-size: 0.72rem;
        padding: 3px 9px;
        border-radius: 6px;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }

    /* Glass Panels */
    .glass-panel {
        background: rgba(17, 24, 39, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 18px;
        padding: 24px;
        backdrop-filter: blur(14px);
        margin-bottom: 20px;
        box-shadow: 0 10px 30px -10px rgba(0,0,0,0.4);
    }
    .panel-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    /* Status Pill Animation */
    .pulse-dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #10b981;
        box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 8px rgba(16, 185, 129, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
    }

    /* Streamlit Widget Overrides */
    div.stButton > button {
        background: linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%) !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 10px 24px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 8px 20px -6px rgba(79, 70, 229, 0.5) !important;
    }
    div.stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 12px 25px -6px rgba(6, 182, 212, 0.6) !important;
        color: #ffffff !important;
    }
    
    /* Input Styling */
    div.stTextInput > div > div > input {
        background-color: rgba(15, 23, 42, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 12px !important;
        color: #f8fafc !important;
        padding: 12px 16px !important;
    }
    div.stTextInput > div > div > input:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.25) !important;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #090d16 0%, #0d1322 100%) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
    }
    
    /* Tabs Overhaul */
    div[data-baseweb="tab-list"] {
        gap: 8px !important;
        background-color: rgba(15, 23, 42, 0.6) !important;
        padding: 6px !important;
        border-radius: 14px !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
    }
    button[data-baseweb="tab"] {
        border-radius: 10px !important;
        padding: 8px 18px !important;
        color: #94a3b8 !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
        border: none !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.3) 0%, rgba(6, 182, 212, 0.2) 100%) !important;
        color: #ffffff !important;
        border: 1px solid rgba(99, 102, 241, 0.4) !important;
    }

    /* Result Box Card */
    .result-box {
        background: rgba(15, 23, 42, 0.75);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 24px;
        color: #e2e8f0;
        line-height: 1.7;
    }
    
    /* Chip buttons for suggestions */
    .suggestion-container {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin: 12px 0 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# =========================
# Initialize Session State
# =========================

if 'orchestrator' not in st.session_state:
    st.session_state.orchestrator = IntelligentResearchOrchestrator("Research Project")
    if os.path.exists(SESSION_FILE):
        try:
            st.session_state.orchestrator.load_session(SESSION_FILE)
        except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
            st.warning(f"تعذر تحميل الجلسة المحفوظة: {error}")

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'active_query' not in st.session_state:
    st.session_state.active_query = ""

if 'last_research_result' not in st.session_state:
    st.session_state.last_research_result = None

# Chroma Memory Count Helper
def get_memory_count():
    try:
        return vector_store._collection.count()
    except Exception:
        return 0


def render_mermaid(code: str):
    """Renders a Mermaid.js diagram with Dark Mode styling"""
    clean_code = code.strip()
    if clean_code.startswith("mermaid"):
        clean_code = clean_code[7:].strip()
    clean_code = clean_code.replace("```mermaid", "").replace("```", "").strip()
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
      <style>
        body {{
            background: transparent;
            margin: 0;
            padding: 10px;
            display: flex;
            justify-content: center;
            align-items: center;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }}
        .mermaid {{
            background: rgba(15, 23, 42, 0.7);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
            width: 95%;
            text-align: center;
        }}
      </style>
    </head>
    <body>
      <div class="mermaid">
{clean_code}
      </div>
      <script>
        mermaid.initialize({{
            startOnLoad: true,
            theme: 'dark',
            themeVariables: {{
                primaryColor: '#6366f1',
                primaryTextColor: '#f8fafc',
                primaryBorderColor: '#818cf8',
                lineColor: '#06b6d4',
                secondaryColor: '#1e293b',
                tertiaryColor: '#0f172a'
            }}
        }});
      </script>
    </body>
    </html>
    """
    import streamlit.components.v1 as components
    components.html(html_content, height=420, scrolling=True)


# =========================
# Modern Sidebar Navigation
# =========================

model_labels = {
    "openai/gpt-oss-20b": "⚡ GPT-OSS 20B (سريع ومتوازن)",
    "qwen/qwen3.6-27b": "🧠 Qwen 3.6 27B (قدرات بحثية عالية)",
    "allam-2-7b": "🇸🇦 Allam 2 7B (متخصص باللغة العربية)",
    "openai/gpt-oss-120b": "👑 GPT-OSS 120B (أعلى دقة وعمق)"
}

with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 10px 0 20px 0;">
        <div style="font-size: 2.8rem; margin-bottom: 6px;">🧬</div>
        <div style="font-size: 1.25rem; font-weight: 800; color: #ffffff; letter-spacing: -0.01em;">NeuroResearch AI</div>
        <div style="display: flex; align-items: center; justify-content: center; gap: 8px; margin-top: 6px;">
            <span class="pulse-dot"></span>
            <span style="font-size: 0.75rem; color: #10b981; font-weight: 700; text-transform: uppercase;">System Online</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06); border-radius: 12px; padding: 12px; margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; font-size: 0.78rem; margin-bottom: 6px;">
            <span style="color: #94a3b8;">🤖 LLM Engine:</span>
            <span style="color: #38bdf8; font-weight: 600;">Groq AI Fleet</span>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 0.78rem; margin-bottom: 6px;">
            <span style="color: #94a3b8;">👥 AI Agents:</span>
            <span style="color: #a855f7; font-weight: 600;">4 Agents Active</span>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 0.78rem;">
            <span style="color: #94a3b8;">🧠 Vector Store:</span>
            <span style="color: #10b981; font-weight: 600;">ChromaDB Ready</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    page = st.radio(
        "التنقل بين الصفحات / Navigation",
        [
            "🏠 الرئيسية (Home)",
            "🔍 منصة البحث (Research)",
            "💬 المحادثة الذكية (Chat)",
            "📊 لوحة التحليلات (Dashboard)",
            "⚙️ الإعدادات (Settings)"
        ],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    st.markdown("<div style='font-size: 0.82rem; color: #94a3b8; font-weight: 700; margin-bottom: 6px;'>🎛️ محرك الذكاء الاصطناعي (AI Engine):</div>", unsafe_allow_html=True)
    selected_model = st.selectbox(
        "نموذج اللغة (Model):",
        options=list(model_labels.keys()),
        format_func=lambda k: model_labels.get(k, k),
        key="sidebar_model_select"
    )
    selected_temp = st.slider(
        "درجة الإبداع (Creativity):",
        min_value=0.0,
        max_value=1.0,
        value=0.2,
        step=0.05,
        key="sidebar_temp_slider",
        help="0.0 = دقة والتزام صارم بالمصادر | 1.0 = استنتاج وإبداع أوسع"
    )
    
    # Update orchestrator when model or temperature changes
    if 'curr_model' not in st.session_state or st.session_state.curr_model != selected_model or st.session_state.get('curr_temp') != selected_temp:
        st.session_state.curr_model = selected_model
        st.session_state.curr_temp = selected_temp
        st.session_state.orchestrator.update_llm(selected_model, selected_temp)
    
    st.markdown("---")
    
    # Sidebar quick stats & actions
    st.caption(f"📁 Session ID: `{st.session_state.orchestrator.session_id[:12]}...`")
    st.caption(f"📌 Project: `{st.session_state.orchestrator.project_name}`")
    
    if st.button("🔄 جلسة جديدة (Reset Session)", use_container_width=True):
        st.session_state.messages = []
        st.session_state.last_research_result = None
        st.session_state.orchestrator.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.success("تم بدء جلسة جديدة بنجاح!")
        st.rerun()

# =========================
# PAGE 1: 🏠 Home
# =========================

if page == "🏠 الرئيسية (Home)":
    st.markdown("""
    <div class="hero-container">
        <div class="hero-badge">⚡ Autonomous Multi-Agent Intelligence Suite</div>
        <div class="hero-title">منصة البحث والتحليل الذكي المتطورة</div>
        <div class="hero-subtitle">
            نظام متكامل قائم على أحدث تقنيات الوكلاء المستقلين (Multi-Agent System) والذاكرة الدائمة (Chroma Vector Database) 
            مدعوماً بنماذج اللغة الكبيرة عبر Groq لتنفيذ أبحاث معمقة، استخراج رؤى دقيقة، وتوليد تقارير تنفيذية عالية الجودة.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # KPI Grid
    memory_count = get_memory_count()
    total_searches = len(st.session_state.orchestrator.research_results)
    total_chats = len(st.session_state.messages)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-header">
                <span class="kpi-title">مهام البحث المنجزة</span>
                <span class="kpi-icon">🔍</span>
            </div>
            <div class="kpi-value">{total_searches}</div>
            <div class="kpi-subtext">Research Missions</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-header">
                <span class="kpi-title">رسائل المحادثة</span>
                <span class="kpi-icon">💬</span>
            </div>
            <div class="kpi-value">{total_chats}</div>
            <div class="kpi-subtext">Chat Interactions</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-header">
                <span class="kpi-title">وثائق الذاكرة</span>
                <span class="kpi-icon">🧠</span>
            </div>
            <div class="kpi-value">{memory_count}</div>
            <div class="kpi-subtext">Vector Store Items</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col4:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-header">
                <span class="kpi-title">فريق الوكلاء</span>
                <span class="kpi-icon">👥</span>
            </div>
            <div class="kpi-value">4</div>
            <div class="kpi-subtext">Specialized Agents</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    
    # Agents Showcase
    st.markdown("""
    <div class="panel-title">
        <span>🤖 فريق وكلاء الذكاء الاصطناعي المتخصص (AI Agent Fleet)</span>
    </div>
    """, unsafe_allow_html=True)
    
    ag_col1, ag_col2, ag_col3, ag_col4 = st.columns(4)
    
    with ag_col1:
        st.markdown("""
        <div class="agent-card">
            <div>
                <div class="agent-header">
                    <div class="agent-avatar">🔍</div>
                    <div>
                        <div class="agent-role">Research Analyst</div>
                        <div class="agent-spec">وكيل البحث وجمع البيانات</div>
                    </div>
                </div>
                <div class="agent-desc">
                    مسؤول عن البحث عبر محركات الويب وتصفح المواقع الإلكترونية وجمع مصادر المعلومات الموثوقة بدقة واستبعاد المحتوى المضلل.
                </div>
            </div>
            <div class="agent-pill-container">
                <span class="agent-pill">DuckDuckGo</span>
                <span class="agent-pill">WebScraper</span>
                <span class="agent-pill">Fact-Extraction</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with ag_col2:
        st.markdown("""
        <div class="agent-card">
            <div>
                <div class="agent-header">
                    <div class="agent-avatar">📊</div>
                    <div>
                        <div class="agent-role">Data Analyst</div>
                        <div class="agent-spec">وكيل التحليل واستخراج الأنماط</div>
                    </div>
                </div>
                <div class="agent-desc">
                    يحلل البيانات المجمعة بعمق، يكتشف الأنماط والاتجاهات الحديثة، ويقدم تقييمات موضوعية للمعلومات المتاحة.
                </div>
            </div>
            <div class="agent-pill-container">
                <span class="agent-pill">Trend Analysis</span>
                <span class="agent-pill">Pattern Recognition</span>
                <span class="agent-pill">Synthesis</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with ag_col3:
        st.markdown("""
        <div class="agent-card">
            <div>
                <div class="agent-header">
                    <div class="agent-avatar">✍️</div>
                    <div>
                        <div class="agent-role">Report Writer</div>
                        <div class="agent-spec">وكيل الصياغة والتقارير</div>
                    </div>
                </div>
                <div class="agent-desc">
                    يحول التحليلات والبيانات الخام إلى تقارير تنفيذية منظمة تشمل ملخصاً تنفيذياً، نتائج رئيسية، وتوصيات عملية مع توثيق المصادر.
                </div>
            </div>
            <div class="agent-pill-container">
                <span class="agent-pill">Executive Briefs</span>
                <span class="agent-pill">Summarization</span>
                <span class="agent-pill">Formatting</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with ag_col4:
        st.markdown("""
        <div class="agent-card">
            <div>
                <div class="agent-header">
                    <div class="agent-avatar">🛡️</div>
                    <div>
                        <div class="agent-role">QA Specialist</div>
                        <div class="agent-spec">وكيل الجودة والتحقق</div>
                    </div>
                </div>
                <div class="agent-desc">
                    يدقق المخرجات النهائية للتأكد من الدقة الواقعية، الاتساق المنطقي، جودة الصياغة، ويمنح تقييماً نهائياً للتقرير (Quality Score).
                </div>
            </div>
            <div class="agent-pill-container">
                <span class="agent-pill">Validation</span>
                <span class="agent-pill">Fact Check</span>
                <span class="agent-pill">Confidence Score</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
    
    # System Architecture Highlights
    st.markdown("""
    <div class="glass-panel">
        <div class="panel-title">⚡ هندسة المنصة المتكاملة (Platform Architecture)</div>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; color: #cbd5e1; font-size: 0.9rem;">
            <div style="background: rgba(255,255,255,0.03); padding: 16px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.05);">
                <div style="font-weight: 700; color: #6366f1; margin-bottom: 6px;">1. أوركسترا الوكلاء (CrewAI Orchestration)</div>
                <div>تنسيق انسيابي للمهام بين 4 وكلاء ذكاء اصطناعي متخصصين مع تبادل السياق وضمان عدم حدوث هلوسة بالاعتماد على أدوات البحث الفعلية.</div>
            </div>
            <div style="background: rgba(255,255,255,0.03); padding: 16px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.05);">
                <div style="font-weight: 700; color: #06b6d4; margin-bottom: 6px;">2. الذاكرة المتجهة (ChromaDB Vector Store)</div>
                <div>تخزين واسترجاع دلالي دائم (RAG) لجميع نتائج الأبحاث السابقة عبر نموذج تضمين HuggingFace MiniLM لاستخدامها في المحادثات اللاحقة.</div>
            </div>
            <div style="background: rgba(255,255,255,0.03); padding: 16px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.05);">
                <div style="font-weight: 700; color: #10b981; margin-bottom: 6px;">3. المساعد الذكي (NeuroBot Conversational AI)</div>
                <div>شات بوت مدعم بذاكرة سياقية كاملة للجلسة وأرشيف الأبحاث، قادر على الإجابة عن الاستفسارات بدقة واحترافية.</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# =========================
# PAGE 2: 🔍 Research Module
# =========================

elif page == "🔍 منصة البحث (Research)":
    st.markdown("""
    <div class="hero-container">
        <div class="hero-badge">🔍 Automated Research Engine & Document RAG</div>
        <div class="hero-title">منصة البحث المتعدد والتحليل الآلي للمستندات</div>
        <div class="hero-subtitle">
            اكتب أي موضوع أو ارفع ملفاتك (PDF, TXT, CSV) وسيتولى فريق الوكلاء الأربعة البحث والتحليل الكمي والمشاعر وصياغة التقرير التنفيذي والمخططات الانسيابية تلقائياً.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Source Mode Selector
    source_mode_display = st.radio(
        "اختر مصدر المعرفة للبحث / Knowledge Source:",
        [
            "🌐 بحث على الويب (Web Search)",
            "📄 تحليل مستند مرفوع (Document Upload)",
            "🔄 بحث هجين (Hybrid: Web + Document)"
        ],
        horizontal=True,
        index=0
    )
    
    source_mode = "web"
    uploaded_doc_text = ""
    uploaded_doc_name = ""
    
    if "مستند" in source_mode_display or "هجين" in source_mode_display:
        source_mode = "doc" if "مستند" in source_mode_display else "hybrid"
        uploaded_file = st.file_uploader(
            "📁 ارفع المستند المراد تحليله (PDF, TXT, CSV, MD, JSON):",
            type=["pdf", "txt", "md", "csv", "json"],
            key="research_uploader"
        )
        if uploaded_file:
            uploaded_doc_name = uploaded_file.name
            with st.spinner("📄 جاري استخراج نصوص المستند بدقة..."):
                uploaded_doc_text = extract_text_from_file(uploaded_file)
            st.success(f"✅ تم تحميل وقراءة المستند: **{uploaded_doc_name}** ({len(uploaded_doc_text):,} حرف)")
            with st.expander("👁️ معاينة مقتطف من محتوى المستند المرفوع"):
                st.text(uploaded_doc_text[:1200] + ("..." if len(uploaded_doc_text) > 1200 else ""))

    # Topic suggestions
    st.markdown("<div style='font-size: 0.85rem; color: #94a3b8; font-weight: 600; margin-top: 14px; margin-bottom: 8px;'>💡 اقتراحات لموضوعات بحثية سريعة:</div>", unsafe_allow_html=True)
    
    s_col1, s_col2, s_col3, s_col4 = st.columns(4)
    if s_col1.button("🤖 Agentic AI Frameworks 2026", use_container_width=True):
        st.session_state.active_query = "Agentic AI Frameworks and Autonomous LLM Systems in 2026"
    if s_col2.button("🧬 CRISPR Gene Editing Breakthroughs", use_container_width=True):
        st.session_state.active_query = "Recent Breakthroughs in CRISPR and Gene Editing Therapeutics"
    if s_col3.button("⚡ Quantum Computing in Cybersecurity", use_container_width=True):
        st.session_state.active_query = "Quantum Computing Impact on Post-Quantum Cryptography and Cybersecurity"
    if s_col4.button("🌱 Next-Gen Solid State Batteries", use_container_width=True):
        st.session_state.active_query = "Commercial Viability and Advances in Solid State EV Batteries"

    # Search Bar
    research_query = st.text_input(
        "أدخل موضوع البحث أو استفسارك حول المستند / Enter Research Query:",
        value=st.session_state.active_query,
        placeholder="مثال: تحليل شامل لاتجاهات الذكاء الاصطناعي، أو لخص النقاط الحرجة في المستند المرفق...",
        key="query_input"
    )
    
    run_col1, run_col2, run_col3 = st.columns([2, 1, 1])
    with run_col1:
        start_btn = st.button("🚀 إطلاق مهمة البحث والتحليل (Launch Mission)", use_container_width=True)
    with run_col2:
        if st.session_state.last_research_result:
            st.download_button(
                label="📥 تحميل (Markdown)",
                data=str(st.session_state.last_research_result.get('result', '')),
                file_name=f"research_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown",
                use_container_width=True
            )
    with run_col3:
        if st.session_state.last_research_result:
            html_report_data = generate_styled_html_report(
                st.session_state.last_research_result.get('query', 'Research Report'),
                st.session_state.last_research_result.get('result', ''),
                st.session_state.last_research_result.get('validation_report', ''),
                st.session_state.last_research_result.get('timestamp', '')
            )
            st.download_button(
                label="🌐 تحميل HTML (طباعة PDF)",
                data=html_report_data,
                file_name=f"research_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                mime="text/html",
                use_container_width=True
            )

    if start_btn:
        if not research_query.strip() and not uploaded_doc_text:
            st.warning("⚠️ يرجى إدخال موضوع للبحث أو رفع مستند أولاً.")
        elif source_mode == "doc" and not uploaded_doc_text:
            st.error("⚠️ لقد اخترت وضع 'تحليل مستند مرفوع' دون إرفاق مستند. يرجى رفع ملف أولاً.")
        else:
            final_query = research_query.strip() if research_query.strip() else f"تحليل شامل واستخراج رؤى من المستند: {uploaded_doc_name}"
            st.session_state.active_query = final_query
            
            with st.status("🔄 جاري تنفيذ مهمة البحث بواسطة فريق الوكلاء الأربعة...", expanded=True) as status_box:
                st.write("🔍 **الوكيل الباحث (Researcher):** يجمع ويفحص البيانات والمصادر الموثوقة...")
                st.write("📊 **وكيل التحليل (Data & Sentiment Analyst):** يستخرج الأرقام والإحصائيات ويقيم نبرة المصداقية...")
                st.write("✍️ **وكيل الصياغة (Report Writer):** يصيغ التقرير التنفيذي الشامل مع التوصيات...")
                st.write("🛡️ **وكيل الجودة (QA Specialist):** يدقق صحة البيانات ويمنح درجة الجودة...")
                
                try:
                    result = st.session_state.orchestrator.conduct_research(
                        query=final_query,
                        source_mode=source_mode,
                        doc_content=uploaded_doc_text,
                        doc_filename=uploaded_doc_name
                    )
                    st.session_state.last_research_result = result
                    
                    if result.get('status') == 'success':
                        status_box.update(label="✅ اكتملت المهمة بنجاح وحُفظ التقرير في الذاكرة المتجهة!", state="complete", expanded=False)
                        st.success("🎉 تم إنجاز البحث بنجاح، استعرض مخرجات فريق الوكلاء أدناه:")
                    else:
                        status_box.update(label="❌ حدث خطأ أثناء تنفيذ البحث", state="error", expanded=True)
                        st.error(f"تفاصيل الخطأ: {result.get('error', 'Unknown error')}")
                except Exception as e:
                    status_box.update(label="❌ فشل الاتصال أو التنفيذ", state="error")
                    st.error(f"حدث استثناء: {str(e)}")

    # Display Current / Last Result
    if st.session_state.last_research_result and st.session_state.last_research_result.get('status') == 'success':
        res = st.session_state.last_research_result
        
        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
        
        tab_report, tab_analysis, tab_mindmap, tab_qa, tab_raw, tab_meta = st.tabs([
            "📄 التقرير التنفيذي (Report)",
            "📊 التحليل الكمي والمشاعر (Analysis)",
            "🗺️ الخريطة التفاعلية (Mindmap)",
            "🛡️ تدقيق الجودة (QA Validation)",
            "🔍 المصادر والأدلة (Raw Sources)",
            "💾 بيانات الجلسة (Metadata)"
        ])
        
        with tab_report:
            st.markdown("""
            <div class="result-box">
            """, unsafe_allow_html=True)
            st.markdown(res.get('result', 'لا توجد بيانات متاحة'))
            st.markdown("</div>", unsafe_allow_html=True)
            
            with st.expander("📋 عرض نص التقرير للنسخ المباشر (Copy to Clipboard)"):
                st.code(res.get('result', ''), language="markdown")
            
        with tab_analysis:
            st.markdown("""
            <div class="glass-panel">
                <div class="panel-title">📊 تحليل وكيل البيانات والمشاعر (Data & Sentiment Insights)</div>
            """, unsafe_allow_html=True)
            st.markdown(res.get('analysis_report', 'لا يوجد تقرير تحليل تفصيلي منفصل.'))
            st.markdown("</div>", unsafe_allow_html=True)
            
        with tab_mindmap:
            st.markdown("""
            <div class="glass-panel">
                <div class="panel-title">🗺️ المخطط الانسيابي التفاعلي للموضوع (Mermaid Mindmap)</div>
                <div style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 15px;">
                    رسم بياني ديناميكي يوضح الهيكل المعرفي والعلاقات بين الأفكار الرئيسية للمهمة البحثية.
                </div>
            """, unsafe_allow_html=True)
            mermaid_code = res.get('mermaid_diagram', '')
            if mermaid_code:
                render_mermaid(mermaid_code)
                with st.expander("⚙️ كود المخطط (Mermaid.js Code)"):
                    st.code(mermaid_code, language="mermaid")
            else:
                st.info("لا يتوفر مخطط انسيابي لهذه الجلسة.")
            st.markdown("</div>", unsafe_allow_html=True)
            
        with tab_qa:
            st.markdown("""
            <div class="glass-panel">
                <div class="panel-title">🛡️ تقرير وكيل ضمان الجودة والتدقيق (Quality Assurance)</div>
            """, unsafe_allow_html=True)
            validation_text = res.get('validation_report', 'لا يوجد تقرير تحقق منفصل')
            st.info(validation_text)
            st.markdown("</div>", unsafe_allow_html=True)
            
        with tab_raw:
            st.markdown("""
            <div class="glass-panel">
                <div class="panel-title">🔍 البيانات والمصادر المستخرجة (الأدلة الخام)</div>
            """, unsafe_allow_html=True)
            st.code(res.get('raw_sources', 'لا تتوفر بيانات خام'), language="markdown")
            st.markdown("</div>", unsafe_allow_html=True)
            
        with tab_meta:
            st.markdown(f"""
            <div class="glass-panel">
                <div class="panel-title">📊 تفاصيل المهمة</div>
                <ul>
                    <li><b>الموضوع:</b> {res.get('query')}</li>
                    <li><b>نمط المصدر:</b> {res.get('source_mode', 'web').upper()} {f"({res.get('doc_filename')})" if res.get('doc_filename') else ""}</li>
                    <li><b>الوقت:</b> {res.get('timestamp')}</li>
                    <li><b>حالة الذاكرة:</b> تم التخزين في ChromaDB بنجاح</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)


# =========================
# PAGE 3: 💬 Intelligent Chat
# =========================

elif page == "💬 المحادثة الذكية (Chat)":
    st.markdown("""
    <div class="hero-container">
        <div class="hero-badge">🤖 NeuroBot AI Assistant & Document Q&A</div>
        <div class="hero-title">المساعد الذكي التفاعلي (NeuroBot)</div>
        <div class="hero-subtitle">
            تحاور مع NeuroBot المدعوم بذاكرة متجهة كاملة (ChromaDB) للبحث في أرشيف أبحاثك السابقة، أو ارفع مستنداً للتحاور المباشر حوله وطرح الأسئلة.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Document Q&A uploader in Chat
    chat_doc_col1, chat_doc_col2 = st.columns([3, 1])
    with chat_doc_col1:
        chat_uploaded_file = st.file_uploader(
            "📎 إرفاق مستند للتحاور حوله مع NeuroBot (PDF, TXT, CSV, MD - اختياري):",
            type=["pdf", "txt", "md", "csv", "json"],
            key="chat_file_uploader"
        )
    with chat_doc_col2:
        memory_search_enabled = st.toggle("🧠 البحث في ذاكرة الأبحاث", value=True, help="استرجاع المعلومات تلقائياً من الأبحاث السابقة عند الحاجة")
        
    chat_file_text = ""
    if chat_uploaded_file:
        with st.spinner("📄 جاري معالجة الملف المرفق..."):
            chat_file_text = extract_text_from_file(chat_uploaded_file)
        st.caption(f"✅ مرفق نشط: `{chat_uploaded_file.name}` ({len(chat_file_text):,} حرف مستخرج)")

    # Suggested Prompts
    st.markdown("<div style='font-size: 0.85rem; color: #94a3b8; font-weight: 600; margin-bottom: 8px;'>💡 اقتراحات محادثة سريعة:</div>", unsafe_allow_html=True)
    c_col1, c_col2, c_col3 = st.columns(3)
    
    chat_prompt = None
    if c_col1.button("🧠 ما هي الأبحاث المحفوظة في ذاكرتك الآن؟", use_container_width=True):
        chat_prompt = "ما هي الأبحاث والمعلومات المتوفرة لديك في الذاكرة حالياً؟"
    if c_col2.button("⚡ كيف يعمل فريق وكلاء الذكاء الاصطناعي؟", use_container_width=True):
        chat_prompt = "اشرح لي باختصار كيف يتعاون الوكلاء الأربعة في المنصة لإنتاج التقارير."
    if c_col3.button("📝 لخص أهم النقاط من الملف المرفق", use_container_width=True):
        chat_prompt = "لخص أهم 5 نقاط وتوصيات مستخرجة من الملف المرفق."
        
    chat_container = st.container()
    
    # Display Chat History
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
    # Chat Input
    user_input = st.chat_input("اكتب رسالتك لـ NeuroBot هنا...") or chat_prompt
    
    if user_input:
        msg_record = user_input + (f" 📎 ({chat_uploaded_file.name})" if chat_uploaded_file else "")
        st.session_state.messages.append({"role": "user", "content": msg_record})
        with st.chat_message("user"):
            st.markdown(user_input + (f"\n\n📎 *ملف مرفق: {chat_uploaded_file.name}*" if chat_uploaded_file else ""))
            
        with st.spinner("🤔 NeuroBot يفكر ويسترجع المعطيات..."):
            try:
                response = st.session_state.orchestrator.neurobot.chat(
                    user_input,
                    attached_doc_text=chat_file_text if chat_uploaded_file else None,
                    use_memory_search=memory_search_enabled
                )
                st.session_state.messages.append({"role": "assistant", "content": response})
                with st.chat_message("assistant"):
                    st.markdown(response)
            except Exception as e:
                st.error(f"❌ خطأ أثناء المحادثة: {str(e)}")


# =========================
# PAGE 4: 📊 Dashboard
# =========================

elif page == "📊 لوحة التحليلات (Dashboard)":
    st.markdown("""
    <div class="hero-container">
        <div class="hero-badge">📊 Analytics & Memory Dashboard</div>
        <div class="hero-title">لوحة التحليلات ومراقبة الذاكرة</div>
        <div class="hero-subtitle">
            متابعة دقيقة لنشاط المنصة، إحصائيات الأبحاث المنجزة، سجل الجلسات وفحص قاعدة بيانات التضمين الدلالي (ChromaDB).
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    research_list = st.session_state.orchestrator.research_results
    memory_count = get_memory_count()
    
    # Top Stats Cards
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.metric("📊 إجمالي الأبحاث", len(research_list), delta="+1" if len(research_list) > 0 else "0")
    with kpi2:
        st.metric("💬 رسائل المحادثة", len(st.session_state.messages))
    with kpi3:
        st.metric("🧠 عناصر الذاكرة الدائمة", memory_count)
    with kpi4:
        st.metric("⏱️ معرف الجلسة", st.session_state.orchestrator.session_id[-8:])
        
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    
    # Visual Analytics Chart
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.markdown("""
        <div class="glass-panel">
            <div class="panel-title">📈 توزيع مهام وكلاء الذكاء الاصطناعي</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Agent execution breakdown
        agent_data = pd.DataFrame({
            "الوكيل (Agent)": ["Researcher", "Analyzer", "Writer", "Validator"],
            "عدد المهام المنجزة": [
                max(len(research_list), 1) * 1,
                max(len(research_list), 1) * 1,
                max(len(research_list), 1) * 1,
                max(len(research_list), 1) * 1
            ]
        })
        chart = alt.Chart(agent_data).mark_bar(cornerRadiusTopLeft=8, cornerRadiusTopRight=8).encode(
            x=alt.X("الوكيل (Agent):N", sort=None),
            y="عدد المهام المنجزة:Q",
            color=alt.Color("الوكيل (Agent):N", scale=alt.Scale(range=["#6366f1", "#06b6d4", "#a855f7", "#10b981"])),
            tooltip=["الوكيل (Agent)", "عدد المهام المنجزة"]
        ).properties(height=260)
        st.altair_chart(chart, use_container_width=True)
        
    with chart_col2:
        st.markdown("""
        <div class="glass-panel">
            <div class="panel-title">🎯 مقياس دقة وملاءمة الأبحاث (Relevance Score)</div>
        </div>
        """, unsafe_allow_html=True)
        
        if research_list:
            scores_data = pd.DataFrame({
                "الموضوع": [r.topic[:18] + "..." for r in research_list],
                "درجة الملاءمة": [r.relevance_score * 100 for r in research_list]
            })
            score_chart = alt.Chart(scores_data).mark_line(point=True, color="#06b6d4").encode(
                x="الموضوع:N",
                y=alt.Y("درجة الملاءمة:Q", scale=alt.Scale(domain=[70, 100])),
                tooltip=["الموضوع", "درجة الملاءمة"]
            ).properties(height=260)
            st.altair_chart(score_chart, use_container_width=True)
        else:
            st.info("لم يتم تسجيل أي مهمة بحث حتى الآن لعرض المخطط البياني.")

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    
    # Research History Table
    st.markdown("""
    <div class="glass-panel">
        <div class="panel-title">📜 سجل الأبحاث السابقة في هذه الجلسة</div>
    </div>
    """, unsafe_allow_html=True)
    
    if research_list:
        for idx, res in enumerate(reversed(research_list), 1):
            with st.expander(f"🔹 {res.topic} — {res.timestamp}"):
                st.markdown(f"**المصدر:** `{res.source_url}` | **درجة الدقة:** `{res.relevance_score * 100:.1f}%`")
                st.markdown(f"**المحتوى التمهيدي:**\n{res.content}")
    else:
        st.info("لم يتم تنفيذ أبحاث في هذه الجلسة بعد. انتقل إلى صفحة 'منصة البحث' للبدء.")

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    
    # Vector Memory Interactive Inspector
    st.markdown("""
    <div class="glass-panel">
        <div class="panel-title">🔍 فاحص الذاكرة المتجهة (ChromaDB Memory Inspector)</div>
    </div>
    """, unsafe_allow_html=True)
    
    test_search_query = st.text_input("ابحث دلالياً في الذاكرة المخزنة (Semantic Search):", placeholder="اكتب كلمة مفتاحية للبحث في Chroma...")
    if test_search_query:
        mem_results = search_memory(test_search_query, k=3)
        if mem_results:
            st.success(f"تم العثور على {len(mem_results)} نتيجة مطابقة في الذاكرة:")
            for doc, score in mem_results:
                st.markdown(f"**Topic:** `{doc.metadata.get('topic', 'General')}` | **Similarity Distance:** `{score:.4f}`")
                st.text(doc.page_content[:300] + "...")
        else:
            st.warning("لم يتم العثور على نتائج متطابقة في الذاكرة.")


# =========================
# PAGE 5: ⚙️ Settings
# =========================

elif page == "⚙️ الإعدادات (Settings)":
    st.markdown("""
    <div class="hero-container">
        <div class="hero-badge">⚙️ System Configuration</div>
        <div class="hero-title">إعدادات النظام وإدارة الجلسات</div>
        <div class="hero-subtitle">
            تخصيص اسم المشروع، التحقق من مفاتيح واجهات برمجة التطبيقات (API Keys)، وإدارة حفظ واسترجاع الجلسات.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col_set1, col_set2 = st.columns(2)
    
    with col_set1:
        st.markdown("""
        <div class="glass-panel">
            <div class="panel-title">📌 إعدادات المشروع الحالي</div>
        </div>
        """, unsafe_allow_html=True)
        
        proj_name = st.text_input("اسم المشروع / Project Name:", value=st.session_state.orchestrator.project_name)
        if st.button("💾 حفظ اسم المشروع", use_container_width=True):
            st.session_state.orchestrator.project_name = proj_name
            st.success("تم تحديث اسم المشروع بنجاح!")
            
        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
        
        # API Health Check
        st.markdown("""
        <div class="glass-panel">
            <div class="panel-title">🔑 حالة الاتصال ومفاتيح API</div>
        </div>
        """, unsafe_allow_html=True)
        
        groq_status = bool(os.getenv("GROQ_API_KEY"))
        if groq_status:
            masked_key = os.getenv("GROQ_API_KEY")[:6] + "..." + os.getenv("GROQ_API_KEY")[-4:]
            st.success(f"✅ مفتاح Groq API متصل ومعرّف بنجاح (`{masked_key}`)")
        else:
            st.error("❌ مفتاح GROQ_API_KEY غير معرّف في ملف .env!")
            
        st.markdown(f"""
        - **نموذج الذكاء الاصطناعي:** `groq/openai/gpt-oss-20b`
        - **مجلد الذاكرة المتجهة:** `./memory_db`
        - **إصدار التضمين:** `all-MiniLM-L6-v2`
        """)

    with col_set2:
        st.markdown("""
        <div class="glass-panel">
            <div class="panel-title">💾 إدارة الجلسة والبيانات (Session Manager)</div>
        </div>
        """, unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("💾 حفظ الجلسة محلياً", use_container_width=True):
                os.makedirs(os.path.dirname(SESSION_FILE), exist_ok=True)
                st.session_state.orchestrator.save_session(SESSION_FILE)
                st.success("تم حفظ الجلسة في ملف JSON!")
        with c2:
            if os.path.exists(SESSION_FILE):
                try:
                    with open(SESSION_FILE, "r", encoding="utf-8") as f:
                        session_json = f.read()
                    st.download_button(
                        "📥 تصدير الجلسة (JSON)",
                        data=session_json,
                        file_name="research_session.json",
                        mime="application/json",
                        use_container_width=True
                    )
                except Exception as e:
                    st.caption(f"تعذر قراءة الجلسة: {e}")
                    
        st.markdown("---")
        
        st.markdown("### 🗑️ مسح البيانات وإعادة الضبط")
        if st.button("🗑️ مسح تاريخ المحادثات والأبحاث الحالية", use_container_width=True):
            st.session_state.messages = []
            st.session_state.orchestrator.research_results = []
            st.session_state.last_research_result = None
            st.success("تم مسح السجل بنجاح!")
            st.rerun()

# =========================
# Modern Footer
# =========================

st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; color: #64748b; font-size: 0.85rem; border-top: 1px solid rgba(255,255,255,0.08); padding-top: 24px;">
    <div style="font-weight: 700; color: #94a3b8; margin-bottom: 4px;">
        🧬 NeuroResearch Multi-Agent Platform &copy; 2026
    </div>
    <div>
        Powered by <b>CrewAI</b>, <b>LangChain</b>, <b>Groq LLMs</b>, <b>ChromaDB</b> & <b>Streamlit</b>
    </div>
</div>
""", unsafe_allow_html=True)

