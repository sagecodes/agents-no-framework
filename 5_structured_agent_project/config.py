import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
assert OPENAI_API_KEY is not None, "❌ OPENAI_API_KEY is not set!"

CHROMA_DB_PATH = "./chroma_rag"
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"
