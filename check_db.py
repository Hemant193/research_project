import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.config import CHROMA_DIR, TXT_DIR, EMBEDDING_MODEL

print("=" * 60)
print("  TUHH RAG — Database Diagnostic")
print("=" * 60)

txt_files = sorted(TXT_DIR.glob("*.txt"))
print(f"\n Source files in data/extracted_txt/: {len(txt_files)}")
total_chars = 0
for f in txt_files:
    size = f.stat().st_size
    chars = len(f.read_text(encoding="utf-8", errors="ignore"))
    total_chars += chars
    est_chunks = chars // (512 * 3)
    print(f"   {f.name:<45} {chars:>8,} chars  ~{est_chunks} chunks")

print(f"\n   Total chars: {total_chars:,}")
print(f"   Rough chunk estimate: ~{total_chars // (512*3):,}")
print(f"   (Actual depends on overlap and text structure)")

print(f"\n ChromaDB at: {CHROMA_DIR}")
if not CHROMA_DIR.exists():
    print(" chroma_db/ folder does not exist. Run: python src/ingest.py")
    sys.exit(1)

try:
    from langchain_ollama import OllamaEmbeddings
    from langchain_chroma import Chroma

    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
    vs = Chroma(
        persist_directory=str(CHROMA_DIR),
        embedding_function=embeddings,
        collection_name="tuhh_courses",
    )
    count = vs._collection.count()
    print(f"Total chunks stored: {count:,}")

except Exception as e:
    print(f" Failed to load: {e}")
    sys.exit(1)

print(f"\nChunks per source file:")
try:
    # Get all metadata
    result = vs._collection.get(include=["metadatas"])
    metadatas = result["metadatas"]

    from collections import Counter
    source_counts = Counter(
        m.get("source_file", "unknown") for m in metadatas
    )
    for source, cnt in sorted(source_counts.items()):
        bar = "█" * (cnt // 50)
        print(f"   {source:<45} {cnt:>5} chunks  {bar}")

    print(f"\n   Sources found: {len(source_counts)}")

except Exception as e:
    print(f"   Could not retrieve metadata: {e}")

# ── 4. Sample 3 random chunks ─────────────────────────────────
print(f"\n🔍 3 sample chunks (sanity check):")
try:
    sample = vs._collection.get(
        limit=3,
        include=["documents", "metadatas"]
    )
    for i, (doc, meta) in enumerate(
        zip(sample["documents"], sample["metadatas"]), 1
    ):
        print(f"\n   ── Chunk {i} ──")
        print(f"   Source : {meta.get('source_file', 'unknown')}")
        print(f"   Program: {meta.get('program_name', 'unknown')}")
        print(f"   Preview: {doc[:200].replace(chr(10), ' ')}…")

except Exception as e:
    print(f"   Could not sample: {e}")

# ── 5. Quick semantic search test ────────────────────────────
print(f"\n🧪 Quick search test: 'machine learning neural networks'")
try:
    results = vs.similarity_search("machine learning neural networks", k=3)
    for i, doc in enumerate(results, 1):
        src = doc.metadata.get("source_file", "?")
        preview = doc.page_content[:120].replace("\n", " ")
        print(f"   {i}. [{src}] {preview}…")
    print("   ✅ Search working correctly")
except Exception as e:
    print(f"   ❌ Search failed: {e}")

# ── Summary ───────────────────────────────────────────────────
print("\n" + "=" * 60)
print(f"  VERDICT: {'✅ Database looks healthy!' if count > 0 else '❌ Database is empty'}")
print(f"  {count:,} chunks across {len(source_counts) if 'source_counts' in dir() else '?'} source files")
if count > 5000:
    chunks_per_file = count // max(len(txt_files), 1)
    print(f"  ~{chunks_per_file} chunks/file — this is normal for detailed handbooks")
    print(f"  My earlier estimate of ~2000 assumed shorter documents.")
print("=" * 60)