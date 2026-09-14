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
MODEL_ID = "gemini-2.0-flash"

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

    def chat(self, user_message: str) -> str:
        """
        Process user message and generate response
        معالجة رسالة المستخدم وتوليد الرد
        """
        try:
            # Build conversation context
            contents = self._build_conversation_context(user_message)
            
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
                    content=user_message,
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


if __name__ == "__main__":
    demo_neurobot()
