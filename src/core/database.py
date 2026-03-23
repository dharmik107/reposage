from sqlalchemy import create_engine, Column, String, Integer, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.dialects.postgresql import UUID
import uuid
import datetime
from .config import settings

engine = create_engine(
    settings.NEON_DATABASE_URL.replace("postgres://", "postgresql://", 1),
    pool_pre_ping=True,    # Checks connection liveness before using it out of the pool
    pool_recycle=300,      # Recycle connections after 5 minutes to prevent stale drops by Neon serverless
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Repository(Base):
    __tablename__ = "repositories"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    repo_url = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class CodeChunk(Base):
    __tablename__ = "code_chunks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    repo_id = Column(UUID(as_uuid=True), index=True)
    file_path = Column(String)
    function_name = Column(String, nullable=True)
    language = Column(String)
    start_line = Column(Integer)
    end_line = Column(Integer)
    chunk_text = Column(String)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
