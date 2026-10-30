import os
import streamlit as st
import requests
from typing import List, Dict, Any, Optional

# --- Configuration & Theme Setup ---
st.set_page_config(
    page_title="Multimodal AI Assistant",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    .stApp {
        background: radial-gradient(circle at top left, #131722, #0d0f15 80%);
    }

    /* Sidebar aesthetics */
    [data-testid="stSidebar"] {
        background-color: #11141e !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }

    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.03em;
        margin-bottom: 1rem;
    }
    .status-online {
        background: rgba(34, 197, 94, 0.15);
        color: #4ade80;
        border: 1px solid rgba(34, 197, 94, 0.3);
    }
    .status-offline {
        background: rgba(239, 68, 68, 0.15);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }

    .card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 0.8rem;
    }

    .starter-card {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        padding: 12px;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    .starter-card:hover {
        background: rgba(99, 102, 241, 0.15);
        border-color: rgba(99, 102, 241, 0.4);
    }

    .doc-pill {
        display: inline-block;
        background: rgba(99, 102, 241, 0.15);
        color: #a5b4fc;
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 6px;
        padding: 2px 8px;
        font-size: 0.75rem;
        margin-right: 4px;
        margin-bottom: 4px;
    }

    .chat-header-bar {
        padding: 10px 16px;
        background: rgba(255, 255, 255, 0.03);
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
</style>
""", unsafe_allow_html=True)

# --- Default API Configuration ---
DEFAULT_API_URL = os.getenv("API_URL", "http://localhost:8000/api")

# --- Session State Initialization ---
if "api_url" not in st.session_state:
    st.session_state.api_url = DEFAULT_API_URL
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None
if "conversation_title" not in st.session_state:
    st.session_state.conversation_title = "New Chat"
if "messages" not in st.session_state:
    st.session_state.messages = []
if "selected_doc_ids" not in st.session_state:
    st.session_state.selected_doc_ids = []
if "use_web_search" not in st.session_state:
    st.session_state.use_web_search = False
if "refresh_conv_trigger" not in st.session_state:
    st.session_state.refresh_conv_trigger = 0


# --- API Helper Functions ---
def check_api_health(api_url: str) -> dict:
    try:
        res = requests.get(f"{api_url}/health", timeout=2)
        if res.status_code == 200:
            data = res.json()
            return {"online": True, **data}
    except Exception:
        pass
    return {"online": False}



def get_conversations(api_url: str) -> List[Dict[str, Any]]:
    try:
        res = requests.get(f"{api_url}/conversations/", timeout=4)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return []


def create_conversation(api_url: str, title: str) -> Optional[str]:
    try:
        res = requests.post(f"{api_url}/conversations/", json={"title": title}, timeout=5)
        if res.status_code in (200, 201):
            return res.json().get("id")
    except Exception as e:
        st.error(f"Error creating conversation: {e}")
    return None


def get_conversation_messages(api_url: str, conv_id: str) -> List[Dict[str, Any]]:
    try:
        res = requests.get(f"{api_url}/conversations/{conv_id}/messages", timeout=5)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return []


def delete_conversation(api_url: str, conv_id: str) -> bool:
    try:
        res = requests.delete(f"{api_url}/conversations/{conv_id}", timeout=4)
        return res.status_code == 200
    except Exception:
        return False


def get_documents(api_url: str) -> List[Dict[str, Any]]:
    try:
        res = requests.get(f"{api_url}/documents/", timeout=4)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return []


def upload_document(api_url: str, uploaded_file) -> Optional[Dict[str, Any]]:
    try:
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type or "application/octet-stream")}
        res = requests.post(f"{api_url}/documents/upload", files=files, timeout=30)
        if res.status_code in (200, 201):
            return res.json()
        else:
            st.error(f"Upload failed: {res.text}")
    except Exception as e:
        st.error(f"Error uploading document: {e}")
    return None


def delete_document(api_url: str, doc_id: str) -> bool:
    try:
        res = requests.delete(f"{api_url}/documents/{doc_id}", timeout=5)
        return res.status_code == 200
    except Exception:
        return False


def send_chat_message(api_url: str, conv_id: str, message: str, web_search: bool, attachments: List[str]) -> Optional[Dict[str, Any]]:
    try:
        payload = {
            "conversation_id": conv_id,
            "message": message,
            "web_search": web_search,
            "attachments": attachments,
        }
        res = requests.post(f"{api_url}/chat/", json=payload, timeout=60)
        if res.status_code == 200:
            return res.json()
        else:
            st.error(f"Server error ({res.status_code}): {res.text}")
    except Exception as e:
        st.error(f"Connection failed: {e}")
    return None


# --- Sidebar UI ---
with st.sidebar:
    st.title("⚡ Multimodal AI")
    
    # Backend & System Health Check
    health_info = check_api_health(st.session_state.api_url)
    if health_info.get("online"):
        db_type = health_info.get("database", "db").upper()
        llm_status = "Gemini Live" if health_info.get("llm_configured") else "Local Mode"
        st.markdown(
            f'<div class="status-badge status-online">● Backend Online ({db_type})</div>',
            unsafe_allow_html=True
        )
        st.caption(f"🧠 Model: {llm_status} | 🗄️ DB: {db_type}")
    else:
        st.markdown('<div class="status-badge status-offline">● Backend Offline</div>', unsafe_allow_html=True)
        st.caption("Start FastAPI backend on `localhost:8000`.")


    # New Chat Button
    if st.button("➕ New Chat", use_container_width=True, type="primary"):
        st.session_state.conversation_id = None
        st.session_state.conversation_title = "New Chat"
        st.session_state.messages = []
        st.session_state.selected_doc_ids = []
        st.rerun()

    st.divider()

    # Capabilities & Settings Section
    st.subheader("⚙️ Settings & Tools")
    st.session_state.use_web_search = st.toggle(
        "🌐 Web Search",
        value=st.session_state.use_web_search,
        help="Enable real-time search grounding for responses",
    )

    with st.expander("🔗 API Endpoint", expanded=False):
        new_url = st.text_input("FastAPI Base URL", value=st.session_state.api_url)
        if new_url != st.session_state.api_url:
            st.session_state.api_url = new_url
            st.rerun()

    st.divider()

    # Documents Section (RAG)
    st.subheader("📄 Document Library (RAG)")
    uploaded_file = st.file_uploader(
        "Upload document (PDF, TXT, DOCX, MD)",
        type=["pdf", "txt", "docx", "md"],
        help="Documents are chunked, embedded and saved into pgvector for Retrieval Augmented Generation",
    )
    if uploaded_file is not None:
        if st.button(f"Upload '{uploaded_file.name}'", key="upload_btn", use_container_width=True):
            with st.spinner("Uploading and indexing..."):
                doc = upload_document(st.session_state.api_url, uploaded_file)
                if doc:
                    st.success(f"Uploaded {doc.get('filename')}!")
                    st.rerun()

    # List of available documents
    docs = get_documents(st.session_state.api_url)
    if docs:
        st.caption("Select documents to attach to prompt context:")
        doc_options = {d["id"]: f"{d['filename']} ({d.get('processing_status', 'ready')})" for d in docs}
        selected_docs = st.multiselect(
            "Attach to chat",
            options=list(doc_options.keys()),
            format_func=lambda x: doc_options.get(x, x),
            default=[d_id for d_id in st.session_state.selected_doc_ids if d_id in doc_options],
        )
        st.session_state.selected_doc_ids = selected_docs

        with st.expander("Manage Documents", expanded=False):
            for d in docs:
                c1, c2 = st.columns([4, 1])
                c1.write(f"📄 **{d['filename']}**")
                if c2.button("🗑️", key=f"del_doc_{d['id']}", help="Delete document"):
                    delete_document(st.session_state.api_url, d["id"])
                    st.rerun()
    else:
        st.caption("No documents uploaded yet.")

    st.divider()

    # Conversation History List
    st.subheader("💬 Chat History")
    conversations = get_conversations(st.session_state.api_url)
    if conversations:
        for conv in conversations:
            c_col1, c_col2 = st.columns([5, 1])
            is_active = conv["id"] == st.session_state.conversation_id
            label = conv.get("title") or "Untitled Conversation"
            if len(label) > 24:
                label = label[:24] + "..."
            
            button_label = f"👉 {label}" if is_active else label
            if c_col1.button(button_label, key=f"conv_{conv['id']}", use_container_width=True):
                st.session_state.conversation_id = conv["id"]
                st.session_state.conversation_title = conv.get("title") or "Conversation"
                # Load existing messages
                raw_messages = get_conversation_messages(st.session_state.api_url, conv["id"])
                st.session_state.messages = [
                    {"role": m.get("role", "assistant"), "content": m.get("content", "")}
                    for m in raw_messages
                ]
                st.rerun()

            if c_col2.button("✖", key=f"del_conv_{conv['id']}", help="Delete chat"):
                delete_conversation(st.session_state.api_url, conv["id"])
                if st.session_state.conversation_id == conv["id"]:
                    st.session_state.conversation_id = None
                    st.session_state.conversation_title = "New Chat"
                    st.session_state.messages = []
                st.rerun()
    else:
        st.caption("No saved conversations.")


# --- Main Chat Area ---
# Header
header_cols = st.columns([3, 1])
with header_cols[0]:
    title_text = st.session_state.conversation_title
    st.markdown(f"### 💬 {title_text}")
with header_cols[1]:
    indicators = []
    if st.session_state.use_web_search:
        indicators.append("🌐 Web Search ON")
    if st.session_state.selected_doc_ids:
        indicators.append(f"📄 {len(st.session_state.selected_doc_ids)} Doc(s) Attached")
    if indicators:
        st.caption(" | ".join(indicators))

# Render conversation messages
if not st.session_state.messages:
    # Empty State Welcome
    st.markdown("""
    <div style="text-align: center; padding: 2.5rem 1rem; opacity: 0.85;">
        <h2>Welcome to Multimodal AI Assistant</h2>
        <p style="color: #94a3b8; font-size: 1.1rem; max-width: 600px; margin: 0 auto;">
            Powered by FastAPI, Google GenAI SDK, pgvector RAG, and Web Grounding.
            Ask questions, upload and query your knowledge base, or search the web.
        </p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class="card">
            <h4>📄 Document RAG</h4>
            <p style="font-size:0.85rem; color:#94a3b8;">Upload PDFs, DOCX, or text files in the sidebar and chat with their contents.</p>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="card">
            <h4>🌐 Web Grounding</h4>
            <p style="font-size:0.85rem; color:#94a3b8;">Toggle Web Search to ground answers in real-time internet data.</p>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="card">
            <h4>🧠 Persistent Memory</h4>
            <p style="font-size:0.85rem; color:#94a3b8;">Full multi-turn dialogue memory stored in PostgreSQL.</p>
        </div>
        """, unsafe_allow_html=True)

# Render conversation messages with citations
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sources"):
            with st.expander("🔍 View Sources & Grounding Citations", expanded=False):
                for s in msg["sources"]:
                    if s.get("type") == "document":
                        st.markdown(f"📄 **{s.get('filename', 'Document')}**")
                        if s.get("snippet"):
                            st.caption(f"> \"{s.get('snippet')}\"")
                    elif s.get("type") == "web":
                        title = s.get("title") or s.get("url")
                        url = s.get("url", "#")
                        st.markdown(f"🌐 [{title}]({url})")
                        if s.get("snippet"):
                            st.caption(f"> \"{s.get('snippet')}\"")

# Quick Action Buttons for Attached Documents (Phase 5: Document Assistant)
if st.session_state.selected_doc_ids:
    st.markdown("##### ⚡ Quick Document Assistant Actions")
    qa_col1, qa_col2, qa_col3 = st.columns(3)
    if qa_col1.button("📑 Executive Summary", key="btn_summary", use_container_width=True):
        st.session_state.pending_prompt = "Please provide a comprehensive executive summary of the attached document(s), highlighting key themes."
        st.rerun()
    if qa_col2.button("🔑 Key Insights & Data", key="btn_insights", use_container_width=True):
        st.session_state.pending_prompt = "Extract the top 5 most important insights and data points from the attached document(s)."
        st.rerun()
    if qa_col3.button("❓ Generate Q&A Quiz", key="btn_quiz", use_container_width=True):
        st.session_state.pending_prompt = "Generate 3 thoughtful questions and answers based strictly on the attached document content."
        st.rerun()

# Chat Input Handler
chat_input_val = st.chat_input("Ask a question, analyze a document, or explore any topic...")
user_input = None

if "pending_prompt" in st.session_state and st.session_state.pending_prompt:
    user_input = st.session_state.pending_prompt
    st.session_state.pending_prompt = None
elif chat_input_val:
    user_input = chat_input_val

if user_input:
    # 1. Display user message immediately
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # 2. Check or create conversation
    active_cid = st.session_state.conversation_id
    if not active_cid:
        # Create a conversation with initial title
        auto_title = user_input.strip()[:35] + ("..." if len(user_input) > 35 else "")
        created_id = create_conversation(st.session_state.api_url, auto_title)
        if created_id:
            active_cid = created_id
            st.session_state.conversation_id = created_id
            st.session_state.conversation_title = auto_title
        else:
            # Fallback local identifier if backend creation failed
            active_cid = "local-temp-session"

    # 3. Call backend chat API with assistant spinner
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response_data = send_chat_message(
                api_url=st.session_state.api_url,
                conv_id=active_cid,
                message=user_input,
                web_search=st.session_state.use_web_search,
                attachments=st.session_state.selected_doc_ids,
            )

        if response_data and "content" in response_data:
            bot_reply = response_data["content"]
            sources = response_data.get("sources", [])
            st.markdown(bot_reply)
            if sources:
                with st.expander("🔍 View Sources & Grounding Citations", expanded=False):
                    for s in sources:
                        if s.get("type") == "document":
                            st.markdown(f"📄 **{s.get('filename', 'Document')}**")
                            if s.get("snippet"):
                                st.caption(f"> \"{s.get('snippet')}\"")
                        elif s.get("type") == "web":
                            title = s.get("title") or s.get("url")
                            url = s.get("url", "#")
                            st.markdown(f"🌐 [{title}]({url})")
                            if s.get("snippet"):
                                st.caption(f"> \"{s.get('snippet')}\"")
            st.session_state.messages.append({"role": "assistant", "content": bot_reply, "sources": sources})
        else:
            fallback_err = "⚠️ Could not receive response from the backend. Please ensure the backend is running at `" + st.session_state.api_url + "`."
            st.markdown(fallback_err)
            st.session_state.messages.append({"role": "assistant", "content": fallback_err})

    st.rerun()

