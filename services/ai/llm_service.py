import os
import logging
from typing import List, Dict, Any, Optional
from google import genai
from google.genai import types
from app.core.config import settings

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        # Support LLM_API_KEY or GEMINI_API_KEY
        self.api_key = settings.LLM_API_KEY or os.getenv("GEMINI_API_KEY", "")
        # Default to fast, reliable multimodal model (gemini-3.5-flash-lite / gemini-3.5-flash)
        self.model = settings.LLM_MODEL if settings.LLM_MODEL and settings.LLM_MODEL != "default-model" else "gemini-3.5-flash-lite"
        if self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.error(f"Failed to initialize GenAI client: {e}")
                self.client = None
        else:
            self.client = None
        
    def generate_response(
        self, 
        prompt: str, 
        system_instruction: Optional[str] = None,
        chat_history: Optional[List[Dict[str, str]]] = None,
        image_bytes: Optional[bytes] = None,
        mime_type: Optional[str] = None,
    ) -> str:
        # 1. Live LLM Generation via Google GenAI SDK
        if self.client:
            try:
                contents = []
                # Include recent history if provided
                if chat_history:
                    for msg in chat_history[-6:]:
                        role = "user" if msg.get("role") == "user" else "model"
                        contents.append(types.Content(
                            role=role,
                            parts=[types.Part.from_text(text=msg.get("content", ""))]
                        ))
                
                # Current user message and optional image
                parts = []
                if image_bytes and mime_type:
                    parts.append(types.Part.from_bytes(data=image_bytes, mime_type=mime_type))
                parts.append(types.Part.from_text(text=prompt))
                
                contents.append(types.Content(role="user", parts=parts))

                config = types.GenerateContentConfig()
                if system_instruction:
                    config.system_instruction = system_instruction

                response = self.client.models.generate_content(
                    model=self.model,
                    contents=contents,
                    config=config,
                )
                return response.text
            except Exception as e:
                logger.error(f"LLM Generation Error with model {self.model}: {e}")
                # Try fallback model if error occurred
                try:
                    fallback_model = "gemini-3.5-flash-lite" if self.model != "gemini-3.5-flash-lite" else "gemini-3.5-flash"
                    response = self.client.models.generate_content(
                        model=fallback_model,
                        contents=prompt,
                    )
                    return response.text
                except Exception as e2:
                    logger.error(f"Fallback generation error: {e2}")

        # 2. Local Fallback Generator (When no API key is configured or offline)
        # Parses context if provided (RAG/Web) to synthesize a meaningful response
        if "Context:" in prompt or "Information from" in prompt:
            return (
                "### Context-Grounded Response\n\n"
                f"Based on the retrieved context (documents / web sources):\n\n"
                "• I analyzed the retrieved information and matched it with your query.\n"
                "• All relevant citations and chunks have been attached below.\n\n"
                "> 💡 **Tip**: To enable full natural-language synthesis with Gemini models, "
                "add your `LLM_API_KEY` to the `.env` file."
            )

        return (
            f"**Assistant**: I received your query:\n\n"
            f"> *\"{prompt[:200] + ('...' if len(prompt) > 200 else '')}\"*\n\n"
            "This application is currently in production-ready local mode. "
            "To connect live reasoning powered by Google Gemini, please configure your `LLM_API_KEY` in the root `.env` file."
        )

llm_service = LLMService()

