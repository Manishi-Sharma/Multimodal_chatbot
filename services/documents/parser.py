import os
import pypdf
import docx

class DocumentParser:
    def parse(self, file_path: str, file_type: str) -> str:
        if file_path.endswith('.pdf') or 'pdf' in file_type:
            return self._parse_pdf(file_path)
        elif file_path.endswith('.docx') or 'wordprocessingml' in file_type:
            return self._parse_docx(file_path)
        elif file_path.endswith('.txt') or file_path.endswith('.md') or 'text' in file_type:
            return self._parse_text(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

    def _parse_pdf(self, file_path: str) -> str:
        text = ""
        with open(file_path, "rb") as file:
            reader = pypdf.PdfReader(file)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        return text

    def _parse_docx(self, file_path: str) -> str:
        doc = docx.Document(file_path)
        return "\n".join([paragraph.text for paragraph in doc.paragraphs])

    def _parse_text(self, file_path: str) -> str:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

parser = DocumentParser()
