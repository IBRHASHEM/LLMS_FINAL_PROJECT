"""
Streamlit App - Main UI for Intelligent Document Analysis & Research Platform
واجهة Streamlit - الواجهة الرئيسية لنظام تحليل الوثائق والبحث الذكي
"""

import streamlit as st
import json
import os
from datetime import datetime
from orchestrator import IntelligentResearchOrchestrator  # ✅ الاستيراد الصحيح
from neurobot_chat import NeuroBot

SESSION_FILE = os.path.join(os.path.dirname(__file__), "conversations", "current_session.json")

# =========================
# Page Configuration
# =========================

st.set_page_config(
    page_title="🔬 Intelligent Research Platform",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        color: #1f77b4;
        text-align: center;
        font-size: 3em;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .subtitle {
        color: #666;
        text-align: center;
        font-size: 1.2em;
        margin-bottom: 30px;
    }
    .section-header {
        color: #1f77b4;
        font-size: 1.8em;
        font-weight: bold;
        margin-top: 20px;
        margin-bottom: 10px;
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 10px;
    }
    .info-box {
        background-color: #e8f4f8;
        padding: 15px;
        border-radius: 5px;
        border-left: 4px solid #1f77b4;
        margin: 10px 0;
    }
    .success-box {
        background-color: #e8f5e9;
        padding: 15px;
        border-radius: 5px;
        border-left: 4px solid #28a745;
        margin: 10px 0;
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

# =========================
# Sidebar Navigation
# =========================

st.sidebar.title("📋 Navigation")
page = st.sidebar.radio(
    "اختر الصفحة:",
    ["🏠 Home", "🔍 Research", "💬 Chat", "📊 Dashboard", "⚙️ Settings"]
)

# =========================
# Main Content
# =========================

if page == "🏠 Home":
    st.markdown('<div class="main-header">🤖 Intelligent Research Platform</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Powered by Multi-Agent AI System | LLMs | Vector Database | Memory Management</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📚 Total Searches", len(st.session_state.orchestrator.research_results))
    
    with col2:
        st.metric("💬 Conversations", len(st.session_state.messages))
    
    with col3:
        st.metric("🔄 Session ID", st.session_state.orchestrator.session_id[:10])
    
    st.markdown("---")
    
    st.markdown("### Features")
    st.markdown("""
    - 🔍 **Advanced Research**: Multi-source search and analysis
    - 👥 **Multi-Agent System**: Specialized AI agents for different tasks
    - 💾 **Memory Management**: Store and retrieve past research
    - 💬 **Smart Chat**: Context-aware conversational AI
    - 📊 **Analytics Dashboard**: Visualize research insights
    """)

elif page == "🔍 Research":
    st.markdown('<div class="section-header">🔍 Research Module</div>', unsafe_allow_html=True)
    
    research_query = st.text_input("Enter your research query:", placeholder="Search for any topic...")
    
    if st.button("🚀 Start Research", key="research_button"):
        if research_query:
            with st.spinner("🔄 Conducting research..."):
                try:
                    result = st.session_state.orchestrator.conduct_research(research_query)
                    
                    if result.get('status') == 'success':
                        st.success("✅ Research completed successfully!")
                        st.markdown("### 📋 Results")
                        st.write(result.get('result', 'No results'))
                    else:
                        st.error(f"❌ Research failed: {result.get('error', 'Unknown error')}")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        else:
            st.warning("⚠️ Please enter a research query")

elif page == "💬 Chat":
    st.markdown('<div class="section-header">💬 Intelligent Chat</div>', unsafe_allow_html=True)
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    user_input = st.chat_input("اكتب رسالتك هنا...")
    
    if user_input:
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        with st.chat_message("user"):
            st.write(user_input)
        
        # Get bot response
        with st.spinner("🤔 Thinking..."):
            try:
                response = st.session_state.orchestrator.neurobot.chat(user_input)
                st.session_state.messages.append({"role": "assistant", "content": response})
                
                with st.chat_message("assistant"):
                    st.write(response)
            except Exception as e:
                st.error(f"❌ Chat error: {str(e)}")

elif page == "📊 Dashboard":
    st.markdown('<div class="section-header">📊 Analytics Dashboard</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "📊 Total Reports",
            len(st.session_state.orchestrator.research_results),
            delta="+1" if len(st.session_state.orchestrator.research_results) > 0 else "0"
        )
    
    with col2:
        st.metric(
            "💬 Chat Messages",
            len(st.session_state.messages)
        )
    
    with col3:
        st.metric(
            "⏱️ Session Duration",
            st.session_state.orchestrator.session_id
        )
    
    # Research history
    if st.session_state.orchestrator.research_results:
        st.markdown("### 📜 Research History")
        for i, result in enumerate(st.session_state.orchestrator.research_results[-5:], 1):
            st.write(f"{i}. **{result.get('topic', 'Unknown')}** - {result.get('timestamp', 'N/A')}")

elif page == "⚙️ Settings":
    st.markdown('<div class="section-header">⚙️ Settings</div>', unsafe_allow_html=True)
    
    st.subheader("Project Settings")
    
    project_name = st.text_input(
        "Project Name:",
        value=st.session_state.orchestrator.project_name
    )
    
    if st.button("💾 Save Settings"):
        st.session_state.orchestrator.project_name = project_name
        st.success("✅ Settings saved successfully!")
    
    st.markdown("---")
    
    st.subheader("Session Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💾 Save Session"):
            os.makedirs(os.path.dirname(SESSION_FILE), exist_ok=True)
            st.session_state.orchestrator.save_session(SESSION_FILE)
            st.success("✅ Session saved successfully!")
    
    with col2:
        if st.button("🗑️ Clear History"):
            st.session_state.messages = []
            st.session_state.orchestrator.research_results = []
            st.success("✅ History cleared successfully!")

# =========================
# Footer
# =========================

st.markdown("---")
st.markdown("""
<center>
    <p>🔬 Intelligent Research Platform | Powered by Multi-Agent AI System</p>
    <p>Made with ❤️ using LangChain, CrewAI, and Streamlit</p>
</center>
""", unsafe_allow_html=True)
