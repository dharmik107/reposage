<div align="center">
  <h1>🧠 RepoSage</h1>
  <p><strong>AI-Powered Repository Intelligence</strong></p>
  <p>Deeply understand any GitHub repository through natural language queries.</p>
  <br />
  <p><a href="https://youtu.be/af1oExZqtCA?si=-kIVK2Jxxb9r8TrR"><strong>🎥 Watch the Demo Video</strong></a></p>
</div>

---

## ✨ Core Features

- **Automated Repository Ingestion**: Simply paste a GitHub URL, and RepoSage will clone, parse, and deeply index the entire codebase in minutes.
- **Conversational AI Interface**: Chat with your codebase. Ask complex questions like *"Where is authentication handled?"* or *"How does the payment flow work?"*
- **Context-Aware Memory**: RepoSage remembers the context of your conversation, allowing for seamless, multi-turn follow-up questions.
- **Precise Code References**: Every AI answer is backed by exact file paths, relevant function names, and line numbers, taking you straight to the source truth.

## 🛠️ Tech Stack

**Frontend & UI**
- **Streamlit**: Fast, interactive chat interface.

**Backend Services**
- **FastAPI & Uvicorn**: High-performance API backend.
- **PostgreSQL (Neon)** & **SQLAlchemy**: Relational database for metadata and persistent app state.

**AI & Machine Learning**
- **Groq API**: Lightning-fast LLM inference.
- **LangChain & LangGraph**: Agentic orchestration, RAG pipelines, and conversational memory.
- **HuggingFace (`sentence-transformers`)**: High-quality open-source text embeddings.
- **ChromaDB**: Blazing-fast local vector database for semantic search.
- **GitPython**: Seamless repository cloning and management.

## ⚙️ How It Works

1. **Ingest & Parse**: You provide a GitHub repository URL. RepoSage clones the repo using `GitPython` and structurally parses the files.
2. **Embed & Index**: The codebase is split into semantic chunks. `HuggingFace` generates high-dimensional embeddings which are stored in `ChromaDB`.
3. **Semantic Query**: When you ask a question, your prompt is embedded and `ChromaDB` retrieves the most cryptically relevant code snippets.
4. **Generate Response**: `LangChain/LangGraph` constructs a context-rich prompt and queries the `Groq LLM` to synthesize an accurate, reference-backed answer based on your chat history and the retrieved code.

## 🚀 Quick Setup

1. **Configure Environment**  
   Create a `.env` file in the root directory:
   ```env
   GROQ_API_KEY=your_groq_api_key
   HF_TOKEN=your_huggingface_token
   NEON_DATABASE_URL=postgresql://user:password@endpoint/dbname
   ```

2. **Install Dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the API Backend**  
   ```bash
   uvicorn main:app --reload
   ```

4. **Launch the User Interface**  
   ```bash
   streamlit run app.py
   ```
