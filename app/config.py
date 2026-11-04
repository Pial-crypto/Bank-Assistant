from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

FAQ_PATH = BASE_DIR / "data" / "bank-faq.csv"

EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"

TOP_K = 3


SIMILARITY_THRESHOLD = 0.55

OLLAMA_MODEL = "qwen2.5:3b"
OLLAMA_URL = "http://localhost:11434/api/chat"