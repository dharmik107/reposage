from typing import TypedDict, List, Dict
from src.ingestion.embedder import embedder
from src.storage.vector import retrieve_vectors
from src.storage.metadata import get_chunks_by_ids
from src.core.database import SessionLocal
from src.agent.llm import generate_answer, rewrite_question

class GraphState(TypedDict):
    question: str
    repo_id: str
    query_embedding: List[float]
    retrieved_docs: List[Dict]
    context_str: str
    answer: str
    retry_count: int
    chat_history: list

def embed_query_node(state: GraphState) -> GraphState:
    query = state["question"]
    embedding = embedder.embed_query(query)
    return {"query_embedding": embedding}

def retrieve_node(state: GraphState) -> GraphState:
    embedding = state["query_embedding"]
    repo_id = state["repo_id"]
    
    matches = retrieve_vectors(embedding, namespace=repo_id, top_k=5)
    chunk_ids = [match['id'] for match in matches]
    
    with SessionLocal() as db:
        chunks = get_chunks_by_ids(db, chunk_ids)
    
    chunk_map = {str(c.id): c for c in chunks}
    ordered_chunks = [chunk_map[cid] for cid in chunk_ids if cid in chunk_map]
    
    retrieved_docs = []
    for chunk in ordered_chunks:
        retrieved_docs.append({
            "file": chunk.file_path,
            "function": chunk.function_name,
            "lines": f"{chunk.start_line}-{chunk.end_line}",
            "text": chunk.chunk_text
        })
        
    return {"retrieved_docs": retrieved_docs}

def context_builder_node(state: GraphState) -> GraphState:
    docs = state["retrieved_docs"]
    context_parts = []
    for doc in docs:
        context_parts.append(
            f"File: {doc['file']}\nFunction: {doc['function']}\nLines: {doc['lines']}\nCode:\n{doc['text']}"
        )
    return {"context_str": "\n\n---\n\n".join(context_parts)}

def generator_node(state: GraphState) -> GraphState:
    question = state["question"]
    context = state["context_str"]
    chat_history = state.get("chat_history", [])
    
    answer = generate_answer(question, context, chat_history)
    return {"answer": answer}

def rewrite_node(state: GraphState) -> GraphState:
    question = state["question"]
    new_question = rewrite_question(question)
    retry_count = state.get("retry_count", 0) + 1
    return {"question": new_question, "retry_count": retry_count}
