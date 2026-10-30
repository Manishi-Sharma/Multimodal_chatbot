# Multimodal AI Chatbot MVP

This is a beginner-friendly multimodal AI chatbot that understands text, handles files, and will support RAG and web search.

## Features (Phase 1-4 MVP)
- Beautiful, modern chat UI (Streamlit)
- Backend API (FastAPI)
- Conversation history persistence (PostgreSQL)
- Real LLM Integration (Google GenAI SDK)
- Document Uploads (PDF, TXT, DOCX, MD)
- Retrieval-Augmented Generation (RAG via `pgvector`)
- Web Search capability toggle
- Emotional Support safety checks

## Architecture
- **Frontend**: Streamlit, Requests, Python
- **Backend**: Python, FastAPI, SQLAlchemy, PostgreSQL
- **Database**: PostgreSQL (requires `pgvector` extension)

## Prerequisites
- Python (v3.9+)
- PostgreSQL server running locally or accessible.

## Installation

### 1. Database Setup
1. Create a PostgreSQL database named `multimodal_ai`.
2. Ensure you have the credentials ready.

### 2. Backend Setup
```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

pip install -r requirements.txt

# Create the database tables
python init_db.py
```

### 3. Environment Variables
Copy `.env.example` to `.env` in the root directory and update your configuration. For Phase 1, make sure `DATABASE_URL` is correct.

### 4. Frontend Setup
```bash
pip install -r frontend/requirements.txt
```

## Running the Application

**Start the Backend**:
```bash
cd backend
# Make sure venv is activated
uvicorn app.main:app --reload
```
The API will run at `http://localhost:8000`. API docs available at `http://localhost:8000/docs`.

**Start the Streamlit Frontend**:
```bash
streamlit run frontend/app.py
```
Or directly from the root directory:
```bash
streamlit run app.py
```
The UI will run at `http://localhost:8501`.

## Roadmap
Current Status: **Phases 1-4 Complete**

Future features to be added:
- Image & Audio Uploads
- Document Editing & Generation
- Text-to-Speech & Image Generation Outputs
