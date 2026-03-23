import chromadb
import os

client = chromadb.PersistentClient(path=os.path.join(os.getcwd(), ".chroma"))
print([col.name for col in client.list_collections()])