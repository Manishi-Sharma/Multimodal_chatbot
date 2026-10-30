from sqlalchemy.orm import Session
from app.services.ai.llm_service import llm_service
from app.services.rag.retriever import retriever
from app.services.search.web_search_service import web_search_service
from app.services.safety.safety_service import safety_service
from app.models.message import Message
from app.models.document import Document
from typing import List, Optional

class ChatOrchestrator:
    def handle_request(
        self, 
        user_message: str, 
        db: Session, 
        conversation_id: Optional[str] = None,
        attachments: Optional[List[str]] = None,
        use_web_search: bool = False, 
        use_rag: bool = True
    ) -> dict:
        context_parts = []
        sources = []
        system_instruction_parts = []

        # 0. Safety & Empathy Check
        safety_result = safety_service.check_message(user_message)
        if not safety_result["is_safe"]:
            return {
                "content": safety_result["response"],
                "sources": []
            }
            
        if safety_result.get("level") == "emotional_support":
            system_instruction_parts.append(safety_result["instruction"])

        # 1. Check for Document RAG
        if use_rag:
            chunks = retriever.retrieve_context(
                query=user_message, 
                db=db, 
                document_ids=attachments if attachments else None
            )
            if chunks:
                # Lookup filenames for clean citations
                doc_ids = list({c.document_id for c in chunks})
                doc_records = db.query(Document).filter(Document.id.in_(doc_ids)).all()
                doc_name_map = {d.id: d.filename for d in doc_records}

                doc_context = "Information from uploaded documents:\n"
                for i, chunk in enumerate(chunks):
                    fname = doc_name_map.get(chunk.document_id, "Document")
                    doc_context += f"[{i+1}] ({fname}) {chunk.content}\n"
                    sources.append({
                        "type": "document", 
                        "id": chunk.document_id,
                        "filename": fname,
                        "snippet": chunk.content[:160] + "..." if len(chunk.content) > 160 else chunk.content
                    })
                context_parts.append(doc_context)

        # 2. Check for Web Search Grounding
        if use_web_search:
            search_results = web_search_service.search(user_message, max_results=4)
            if search_results:
                web_context = "Information from web search:\n"
                for i, res in enumerate(search_results):
                    web_context += f"[{i+1}] {res['title']}: {res['snippet']}\n"
                    sources.append({
                        "type": "web", 
                        "title": res.get("title", ""),
                        "url": res.get("url", ""),
                        "snippet": res.get("snippet", "")
                    })
                context_parts.append(web_context)

        # 3. Retrieve Multi-Turn Conversation History
        chat_history = []
        if conversation_id:
            recent_db_messages = (
                db.query(Message)
                .filter(Message.conversation_id == conversation_id)
                .order_by(Message.created_at.desc())
                .limit(8)
                .all()
            )
            # Reverse to chronological order (oldest to newest)
            for m in reversed(recent_db_messages):
                chat_history.append({"role": m.role, "content": m.content})

        # 4. Assemble Final Context Prompt
        final_prompt = user_message
        if context_parts:
            final_prompt = (
                "Ground your answer in the following verified context. Cite document or web sources where appropriate:\n\n"
                + "\n\n".join(context_parts)
                + f"\n\nUser Question: {user_message}"
            )

        system_instruction = "\n".join(system_instruction_parts) if system_instruction_parts else (
            "You are a helpful, accurate, and articulate AI assistant. Answer the user's questions clearly. "
            "When context is provided from uploaded documents or search, use it to deliver factual, grounded responses."
        )

        # 5. Generate AI Response
        ai_content = llm_service.generate_response(
            prompt=final_prompt,
            system_instruction=system_instruction,
            chat_history=chat_history
        )

        return {
            "content": ai_content,
            "sources": sources
        }

chat_orchestrator = ChatOrchestrator()

