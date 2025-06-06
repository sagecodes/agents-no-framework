from vector_store import rag_collection, embed_model

def preload_knowledge_base():
    docs = [
        "The sun is a star at the center of the solar system.",
        "Planets orbit the sun due to gravity.",
        "Stars generate energy through nuclear fusion.",
        "The Earth is the third planet from the sun.",
        "The moon orbits the Earth and affects tides.",
    ]
    ids = [f"doc-{i}" for i in range(len(docs))]
    embeddings = embed_model.encode(docs).tolist()
    rag_collection.add(documents=docs, embeddings=embeddings, ids=ids)
    print(f"✅ Preloaded {len(docs)} documents into RAG DB.")

if __name__ == "__main__":
    preload_knowledge_base()
