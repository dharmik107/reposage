import chromadb
import os

persist_directory = os.path.join(os.getcwd(), ".chroma")
client = chromadb.PersistentClient(path=persist_directory)

def init_vectordb():
    # Chroma handles collections lazily, so we don't strictly need to create them upfront unless we want to preset rules.
    # It creates collections automatically upon getting or creating.
    pass

def store_vectors(vectors: list, namespace: str):
    collection = client.get_or_create_collection(name=namespace)
    
    ids = [v["id"] for v in vectors]
    embeddings = [v["values"] for v in vectors]
    metadatas = [v.get("metadata", {}) for v in vectors]
    
    collection.add(
        ids=ids,
        embeddings=embeddings,
        metadatas=metadatas
    )

def retrieve_vectors(query_vector: list[float], namespace: str, top_k: int = 5):
    try:
        collection = client.get_collection(name=namespace)
    except Exception:
        return []
    
    res = collection.query(
        query_embeddings=[query_vector],
        n_results=top_k,
        include=['metadatas'] # Optimization: we don't need 'embeddings' or 'documents' back, just 'ids' which returns natively.
    )
    
    matches = []
    if res['ids'] and len(res['ids']) > 0:
        for i in range(len(res['ids'][0])):
            matches.append({
                "id": res['ids'][0][i]
            })
            
    return matches
