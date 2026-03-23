from sqlalchemy.orm import Session
from src.core.database import CodeChunk, Repository
import uuid

def create_repository(db: Session, repo_url: str):
    repo = Repository(repo_url=repo_url)
    db.add(repo)
    db.commit()
    db.refresh(repo)
    return repo

def get_repository(db: Session, repo_id: str):
    return db.query(Repository).filter(Repository.id == uuid.UUID(repo_id)).first()

def insert_code_chunks(db: Session, chunks_data: list[dict]):
    chunks = []
    for cd in chunks_data:
        chunk = CodeChunk(
            repo_id=uuid.UUID(cd["repo_id"]),
            file_path=cd["file_path"],
            function_name=cd["function_name"],
            language=cd["language"],
            start_line=cd["start_line"],
            end_line=cd["end_line"],
            chunk_text=cd["chunk_text"]
        )
        chunks.append(chunk)
    db.add_all(chunks)
    db.commit()

def get_chunks_by_ids(db: Session, chunk_ids: list[str]):
    if not chunk_ids:
        return []
    return db.query(CodeChunk).filter(CodeChunk.id.in_([uuid.UUID(cid) for cid in chunk_ids])).all()
