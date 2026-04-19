import sys
from pathlib import Path
from typing import Any, List
import numpy as np 
import src.config as config

sys.path.insert(0, str(Path(__file__).parent.parent))

from langchain_core.retrievers import BaseRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_community.retrievers import BM25Retriever
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings, ChatOllama
from sentence_transformers import CrossEncoder

from src.config import (
    TXT_DIR, CHUNK_SIZE, CHUNK_OVERLAP,
    EMBEDDING_MODEL, LLM_MODEL, RERANK_CANDIDATES,
)


# ── Helper: load + split docs for BM25 ───────────────────────
def _load_split_docs():
    """Load all .txt files and split — same chunking as ingest.py."""
    docs = []
    for f in sorted(TXT_DIR.glob("*.txt")):
        docs.extend(TextLoader(str(f), autodetect_encoding=True).load())

    return RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    ).split_documents(docs)


# Dense retriever
class DenseRetriever(BaseRetriever):
    """
    Standard cosine-similarity search over ChromaDB embeddings.

    Strength:  Understands semantics — "deep learning" matches a chunk
               that says "neural networks" even with no keyword overlap.
    Weakness:  If the embedding model hasn't seen domain-specific terms,
               it may miss them.
    """
    vector_store: Any
    k: int = 5

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        return self.vector_store.similarity_search(query, k=self.k)


# Cross-encoder reranking retriever
class RerankRetriever(BaseRetriever):
    """
    Two-stage pipeline:
      Stage 1 — Dense: fetch top-RERANK_CANDIDATES chunks (default 20).
      Stage 2 — Rerank: CrossEncoder scores every (query, chunk) pair;
                keep top-k.

    Why two stages?
      Embedding models run ONE forward pass per query (fast, O(1)).
      CrossEncoders attend to BOTH query and document together (slow,
      O(N)) — far more accurate but can't scale to the whole corpus.
      Solution: use fast embeddings to narrow to 20, then rerank with
      the accurate cross-encoder.

    Model: BAAI/bge-reranker-base (~270 MB).
    """
    vector_store: Any
    k: int = 5
    reranker: Any = None

    def __init__(self, vector_store, **kwargs):
        super().__init__(vector_store=vector_store, **kwargs)
        print("  Loading BGE reranker model (~270 MB) …")
        self.reranker = CrossEncoder("BAAI/bge-reranker-base")
        print(" Reranker ready.")

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        candidates = self.vector_store.similarity_search(
            query, k=RERANK_CANDIDATES
        )
        if not candidates:
            return []

        scores = self.reranker.predict(
            [[query, doc.page_content] for doc in candidates]
        )
        ranked = sorted(zip(scores, candidates), key=lambda x: x[0], reverse=True)
        return [doc for _, doc in ranked[: self.k]]


# HyDE retriever
class HyDERetriever(BaseRetriever):
    """
    Hypothetical Document Embeddings (Gao et al., 2022).
    Extended to support Multi-HyDE (generating N hypotheses).
    """
    vector_store: Any
    k: int = 5
    num_hypotheses: int = 1
    llm: Any = None
    embeddings: Any = None
    def __init__(self, vector_store, **kwargs):
        super().__init__(vector_store=vector_store, **kwargs)
        # NOTE: If num_hypotheses > 1, temperature MUST be > 0, 
        # otherwise the LLM will generate the exact same text 4 times.
        temp = 0.3 if self.num_hypotheses > 1 else 0.0
        self.llm        = ChatOllama(model=LLM_MODEL, temperature=temp)
        self.embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
        
    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        prompt = (
            "You are writing a passage from the TUHH module handbook. "
            "Write a short, factual, 3-sentence passage that answers: "
            f"{query}"
        )
        hypo = self.llm.invoke(prompt).content

        # --- LOG HYPOTHETICAL DOCUMENT ---
        log_filename = f"hyde_{config.LLM_MODEL.replace(':', '_')}.log"
        log_path = Path(__file__).parent.parent / "results" / log_filename
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"QUERY: {query}\nHYPOTHETICAL: {hypo}\n{'-'*80}\n")

        vec = self.embeddings.embed_query(hypo)
        retrieved_docs = self.vector_store.similarity_search_by_vector(vec, k=self.k)
        
        # --- NEW: Inject the hypothetical text into the first doc's metadata ---
        if retrieved_docs:
            retrieved_docs[0].metadata["hyde_hypothetical"] = hypo
        
        return retrieved_docs

# Factory
def get_retriever(strategy: str, vector_store, top_k: int = 5):
    """
    Return the correct retriever for a given strategy name.

    Args:
        strategy:     "Sparse (BM25)" | "Dense (Vector)" |
                      "Hybrid + Rerank" | "HyDE"
        vector_store: loaded Chroma instance
        top_k:        number of documents to return
    """
    print(f" Initialising: {strategy}")

    if strategy == "Sparse (BM25)":
        # BM25 works on raw text — no embeddings needed
        docs = _load_split_docs()
        return BM25Retriever.from_documents(docs, k=top_k)

    elif strategy == "Dense (Vector)":
        return DenseRetriever(vector_store=vector_store, k=top_k)

    elif strategy == "Hybrid + Rerank":
        return RerankRetriever(vector_store=vector_store, k=top_k)

    elif strategy == "HyDE":
        return HyDERetriever(vector_store=vector_store, k=top_k)

    else:
        valid = ["Sparse (BM25)", "Dense (Vector)", "Hybrid + Rerank", "HyDE"]
        raise ValueError(f"Unknown strategy '{strategy}'. Valid: {valid}")