# RepoSage

AI-Powered developer tool to deeply understand any GitHub repository through natural language.

## Setup

1. Configure `.env` with your API keys:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   NEON_DATABASE_URL=postgresql://user:password@endpoint/dbname
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run FastAPI backend server:
   ```bash
   uvicorn main:app --reload
   ```
4. Run Streamlit UI:
   ```bash
   streamlit run app.py
   ```
