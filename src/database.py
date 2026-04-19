import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

from src.config import (
    TXT_DIR, CHROMA_DIR,
    EMBEDDING_MODEL, CHUNK_SIZE, CHUNK_OVERLAP,
)


def _extract_tuhh_metadata(text: str) -> dict:
    """
    Rule-based extraction tailored for TUHH format.
    Looks for "Module M1552: Advanced Machine Learning" and "Course L2322"
    """
    metadata = {
        "module_code": "Unknown",
        "module_name": "Unknown Module",
        "course_code": "Unknown",
        "ects": 0
    }
    
    # 1. Extract Module Code and Name
    mod_match = re.search(r"Module\s(M\d+):\s*(.+)", text)
    if mod_match:
        metadata["module_code"] = mod_match.group(1).strip()
        metadata["module_name"] = mod_match.group(2).strip()
        
    # 2. Extract specific Course Code (if the chunk is about a specific course like L2322)
    crs_match = re.search(r"Course\s(L\d+):", text)
    if crs_match:
        metadata["course_code"] = crs_match.group(1).strip()
        
    # 3. Extract ECTS (Looks for "Credit points 6" or the "CP 3" in the table row)
    ects_match = re.search(r"Credit points\s+(\d+)", text)
    if not ects_match:
        # Fallback: find "CP 3" or "CP 6" usually near the top of a module/course block
        ects_match = re.search(r"\bCP\s+(\d+)", text)
        
    if ects_match:
        try:
            metadata["ects"] = int(ects_match.group(1))
        except ValueError:
            pass

    return metadata


def ingest(embeddings) -> Chroma:
    txt_files = sorted(TXT_DIR.glob("*.txt"))
    if not txt_files:
        print(f"No .txt files in {TXT_DIR}")
        sys.exit(1)

    # Custom separators for TUHH handbooks!
    # We tell the chunker: TRY TO SPLIT AT "Course L" FIRST. 
    # This prevents cutting a course description in half.
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=[
            "Course L",    # Split courses into their own chunks
            "Module M",    # Split modules into their own chunks
            "\n\n",        # Paragraph breaks
            "\n",          # Line breaks
            ". ",          # Sentences
            " ",           # Words
            ""             # Fallback
        ],
    )

    all_docs = []

    for txt in txt_files:
        stem = txt.stem
        program_name = stem.replace("_", " ").replace("-", " ")
        print(f"\nProcessing: {stem}.txt")

        raw = TextLoader(str(txt), autodetect_encoding=True).load()
        chunks = splitter.split_documents(raw)
        print(f"   → Split into {len(chunks)} logical chunks")

        for i, chunk in enumerate(chunks):
            # 1. Extract rich metadata from the text
            meta = _extract_tuhh_metadata(chunk.page_content)
            
            # 2. Re-attach the string that the chunker used to split on
            if chunk.page_content.startswith(" "):
                if "L" in chunk.page_content[:5] and meta["course_code"] != "Unknown":
                    chunk.page_content = "Course " + chunk.page_content.lstrip()
                elif "M" in chunk.page_content[:5] and meta["module_code"] != "Unknown":
                    chunk.page_content = "Module " + chunk.page_content.lstrip()

            # 3. Build a highly descriptive header for the Embedding model
            header = (
                f"Program: {program_name} | "
                f"Module: {meta['module_code']} - {meta['module_name']}"
            )
            # Only add course code if this chunk is specifically about a course
            if meta["course_code"] != "Unknown":
                header += f" | Course: {meta['course_code']}"
            
            header += f" | ECTS: {meta['ects']}\n\n"
            
            # 4. Prepend header to chunk content
            chunk.page_content = header + chunk.page_content
            
            # 5. Attach metadata to ChromaDB
            chunk.metadata.update({
                "source_file": stem,
                "program_name": program_name,
                "module_code": meta["module_code"],
                "module_name": meta["module_name"],
                "course_code": meta["course_code"],
                "ects": meta["ects"],
                "chunk_index": i,
            })

        all_docs.extend(chunks)

    total = len(all_docs)
    print(f"\nTotal chunks to embed: {total}")
    print(f"Embedding with '{EMBEDDING_MODEL}' via Ollama …")

    vs = Chroma.from_documents(
        documents=all_docs,
        embedding=embeddings,
        persist_directory=str(CHROMA_DIR),
        collection_name="tuhh_courses",
    )

    print(f"\nIngestion complete — {total} structured chunks stored.")
    return vs


def get_vector_store() -> Chroma:
    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)

    db_exists = CHROMA_DIR.exists() and any(CHROMA_DIR.iterdir())

    if db_exists:
        print("Loading existing ChromaDB …")
        try:
            vs = Chroma(
                persist_directory=str(CHROMA_DIR),
                embedding_function=embeddings,
                collection_name="tuhh_courses",
            )
            count = vs._collection.count()
            if count == 0:
                print("DB folder exists but is empty.")
                sys.exit(1)
            print(f"✅ Loaded {count} chunks.")
            return vs
        except Exception as e:
            print(f"Load failed: {e}")
            sys.exit(1)

    print("No ChromaDB found — building …")
    return ingest(embeddings)


if __name__ == "__main__":
    vs = get_vector_store()
    count = vs._collection.count()
    print(f"\n{'═'*50}")
    print(f"  ChromaDB ready — {count} structured chunks")
    print(f"{'═'*50}")