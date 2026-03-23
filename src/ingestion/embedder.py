from langchain_huggingface import HuggingFaceEmbeddings

class Embedder:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    def embed_chunks(self, texts: list[str]) -> list[list[float]]:
        return self.embeddings.embed_documents(texts)
    
    def embed_query(self, query: str) -> list[float]:
        return self.embeddings.embed_query(query)

embedder = Embedder()
