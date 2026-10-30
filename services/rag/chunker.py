from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.core.config import settings

class DocumentChunker:
    def __init__(self):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            length_function=len,
            is_separator_regex=False,
        )

    def chunk_text(self, text: str) -> list[str]:
        return self.splitter.split_text(text)

chunker = DocumentChunker()
