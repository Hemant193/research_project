from pathlib import Path

ROOT_DIR    = Path(__file__).parent.parent
DATA_DIR    = ROOT_DIR / "data"
PDF_DIR     = DATA_DIR / "pdfs"
TXT_DIR     = DATA_DIR / "extracted_txt"
JSON_DIR    = DATA_DIR / "json"
CHROMA_DIR  = ROOT_DIR / "chroma_db"  # Default name (Notebook will override this to chroma_db_512, etc.)
RESULTS_DIR = ROOT_DIR / "results"

for _d in [PDF_DIR, TXT_DIR, JSON_DIR, CHROMA_DIR, RESULTS_DIR]:
    _d.mkdir(parents=True, exist_ok=True)


LLM_MODEL       = "llama3.2:3b"          # Default LLM
EMBEDDING_MODEL = "mxbai-embed-large"

# Chunking strategy
CHUNK_SIZE    = 1024                      # Default chunk size
CHUNK_OVERLAP = 150                       # Default overlap

# Retrieval parameters
TOP_K             = 10
RERANK_CANDIDATES = 20
RERANK_CANDIDATES = 20