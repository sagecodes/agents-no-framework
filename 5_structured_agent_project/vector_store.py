import chromadb
from sentence_transformers import SentenceTransformer
from config import CHROMA_DB_PATH, EMBED_MODEL_NAME

chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
rag_collection = chroma_client.get_or_create_collection("rag_demo")

embed_model = SentenceTransformer(EMBED_MODEL_NAME)
