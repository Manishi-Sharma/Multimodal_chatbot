from duckduckgo_search import DDGS
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class WebSearchService:
    def __init__(self):
        self.api_key = settings.WEB_SEARCH_API_KEY
        
    def search(self, query: str, max_results: int = 4) -> list[dict]:
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))
                formatted = []
                for res in results:
                    formatted.append({
                        "title": res.get("title", ""),
                        "url": res.get("href", res.get("link", "")),
                        "snippet": res.get("body", res.get("snippet", ""))
                    })
                if formatted:
                    return formatted
        except Exception as e:
            logger.warning(f"DuckDuckGo search error: {e}")
            
        # Fallback if rate limited or offline
        return [
            {
                "title": f"Search Query: {query}",
                "url": f"https://duckduckgo.com/?q={query.replace(' ', '+')}",
                "snippet": f"Web results for '{query}'."
            }
        ]

web_search_service = WebSearchService()

