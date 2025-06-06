from utils.decorators import tool
from vector_store import rag_collection, embed_model

@tool(agent="rag")
def search_vector_db(query, top_k=3):
    """Searches the vector DB for relevant documents."""
    query_embedding = embed_model.encode(query).tolist()
    results = rag_collection.query(query_embeddings=[query_embedding], n_results=top_k)
    docs = results["documents"][0] if "documents" in results else []
    return docs
