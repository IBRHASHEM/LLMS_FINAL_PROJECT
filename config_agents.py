"""
Configuration file for all AI Agents
تكوين جميع وكلاء الذكاء الاصطناعي المتخصصة
"""

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
    model="groq/gemma2-9b-it",  # ✅ النموذج الصحيح (محدّث)
    temperature=0,
    max_tokens=800,
    api_key=GROQ_API_KEY,
)

llm_fast = LLM(
    model="groq/gemma2-9b-it",  # ✅ النموذج الصحيح (محدّث)
    temperature=0.2,
    max_tokens=800,
    api_key=GROQ_API_KEY,
)

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
        return results[:1000]  # Limit results
    except Exception as e:
        return f"Search error: {str(e)}"


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
        return clean_text[:1500]  # Return first 1500 chars
    except Exception as e:
        return f"Scraping error: {str(e)}"


@tool
def analyze_sentiment_tool(text: str) -> str:
    """
    Analyze the sentiment and tone of given text
    تحليل المشاعر والنبرة في النص
    """
    try:
        from transformers import pipeline
        sentiment_pipeline = pipeline(
            "text-classification",
            model="distilbert-base-uncased-finetuned-sst-2-english"
        )
        result = sentiment_pipeline(text[:512])  # Limit to 512 chars
        return str(result)
    except Exception as e:
        return f"Sentiment analysis error: {str(e)}"


@tool
def summarize_text_tool(text: str) -> str:
    """
    Summarize the given text using abstractive summarization
    تلخيص النص باستخدام التلخيص الحسوبي
    """
    try:
        from transformers import pipeline
        summarizer = pipeline(
            "summarization",
            model="facebook/bart-large-cnn"
        )
        # Split text into chunks if too long
        max_length = 1024
        text = text[:max_length]
        
        if len(text.split()) > 100:
            summary = summarizer(text, max_length=150, min_length=50, do_sample=False)
            return summary[0]['summary_text']
        else:
            return text
    except Exception as e:
        return f"Summarization error: {str(e)}"


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
    role="Research Specialist",
    goal="Search and extract relevant information from multiple sources accurately",
    backstory="""
    You are an expert research specialist with deep knowledge in information gathering.
    You use web search and document scraping to find reliable, up-to-date information.
    You verify facts from multiple sources and provide URLs for transparency.
    You never make up information and always cite your sources.
    
    أنت متخصص بحث خبير لديك معرفة عميقة في جمع المعلومات.
    تستخدم البحث على الويب لإيجاد معلومات موثوقة.
    تتحقق من الحقائق من مصادر متعددة وتوفر روابط.
    """,
    tools=[web_search_tool, web_scraper_tool],
    llm=llm,
    max_iter=4,
    allow_delegation=False,
    verbose=True
)


analyzer_agent = Agent(
    role="Data Analyst",
    goal="Analyze collected information and extract meaningful insights",
    backstory="""
    You are a skilled data analyst with expertise in pattern recognition.
    You examine information critically, identify trends, and extract key insights.
    You provide statistical analysis when relevant and explain complex concepts clearly.
    You structure information in a logical, easy-to-understand format.
    
    أنت محلل بيانات ماهر متخصص في التعرف على الأنماط.
    تفحص المعلومات بعناية وتستخرج الرؤى الرئيسية.
    """,
    tools=[analyze_sentiment_tool],
    llm=llm,
    max_iter=3,
    allow_delegation=False,
    verbose=True
)


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
    max_iter=3,
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
    'llm_fast',
    'web_search_tool'
]
