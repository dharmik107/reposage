from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict

from src.core.database import get_db, SessionLocal
from src.ingestion.cloner import clone_repo, cleanup_repo
from src.ingestion.parser import parse_repo
from src.ingestion.embedder import embedder
from src.storage.vector import store_vectors, init_vectordb
from src.storage.metadata import create_repository, insert_code_chunks
from src.agent.graph import process_query
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class IngestRequest(BaseModel):
    repo_url: str

class QueryRequest(BaseModel):
    repo_id: str
    question: str
    chat_history: List[Dict[str, str]] = []

@router.on_event("startup")
def startup_event():
    init_vectordb()
    # Ensure database tables exist
    from src.core.database import Base, engine
    Base.metadata.create_all(bind=engine)

@router.post("/ingest")
def ingest_repo(req: IngestRequest, db: Session = Depends(get_db)):
    repo = create_repository(db, req.repo_url)
    repo_id_str = str(repo.id)
    
    # Clone repo
    try:
        temp_dir = clone_repo(req.repo_url)
    except Exception as e:
        logger.error(f"Failed to clone repository: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"Failed to clone repository: {str(e)}")
        
    try:
        # Parse chunks
        chunks = parse_repo(temp_dir, repo_id_str)
        if not chunks:
            raise HTTPException(status_code=400, detail="No valid chunks extracted from repository")
            
        # Extract chunk texts
        chunk_texts = [c["chunk_text"] for c in chunks]
        
        # Insert metadata first to get generated UUIDs
        insert_code_chunks(db, chunks)
        
        # Now we need chunk IDs from db. Let's fetch them
        from src.core.database import CodeChunk
        import uuid
        db_chunks = db.query(CodeChunk).filter(CodeChunk.repo_id == uuid.UUID(repo_id_str)).all()
        
        # Align chunks based on text, or we can just pair them if order is preserved (simplified)
        # Instead, it's safer to embed directly from db chunks
        db_chunk_texts = [c.chunk_text for c in db_chunks]
        
        # Generate embeddings in batches to prevent OOM
        batch_size = 100
        for i in range(0, len(db_chunks), batch_size):
            batch = db_chunks[i:i + batch_size]
            batch_texts = [c.chunk_text for c in batch]
            
            embeddings = embedder.embed_chunks(batch_texts)
            
            vectors = []
            for j, db_chunk in enumerate(batch):
                vectors.append({
                    "id": str(db_chunk.id),
                    "values": embeddings[j],
                    "metadata": {
                        "file_path": db_chunk.file_path,
                        "function_name": db_chunk.function_name or "file_level",
                        "repo_id": repo_id_str
                    }
                })
            
            store_vectors(vectors, namespace=repo_id_str)
        
        return {
            "repo_id": repo_id_str,
            "status": "indexed",
            "files_processed": len(set(c.file_path for c in db_chunks))
        }
        
    finally:
        cleanup_repo(temp_dir)

@router.post("/query")
def query_repo(req: QueryRequest):
    try:
        response = process_query(req.repo_id, req.question, req.chat_history)
        return response
    except Exception as e:
        logger.error(f"Error executing query on repo {req.repo_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error executing query.")
