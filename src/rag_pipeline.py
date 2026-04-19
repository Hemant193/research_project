import os
import re
from pathlib import Path
from typing import List

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

TXT_DIR = Path("extracted_txt")
CHROMA_DIR = Path("chroma_db")

def load_documents() -> List[Document]:
    docs = []
    for txt_file in TXT_DIR.glob("*.txt"):
        program_name = txt_file.stem.replace("_", " ").title()
        with open(txt_file, "r", encoding="utf-8") as f:
            text = f.read()
        doc = Document(
            page_content=text,
            metadata={
                "source": str(txt_file),
                "program": program_name,
                "file_type": "txt"
            }
        )
        docs.append(doc)
    print(f"Loaded {len(docs)} documents")
    return docs

def chunk_docs(documents: List[Document]) -> List[Document]:
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = text_splitter.split_documents(documents)
    
    # Try to tag module chunks
    for chunk in chunks:
        content_start = chunk.page_content[:300]
        if "Module M" in content_start or re.search(r'M[0-9]{4}', content_start):
            code_match = re.search(r'Module\s*([A-Z0-9\-]+)', content_start, re.IGNORECASE)
            if code_match:
                chunk.metadata["module_code"] = code_match.group(1).strip()
            chunk.metadata["chunk_type"] = "module"
        else:
            chunk.metadata["chunk_type"] = "general"
    
    print(f"Created {len(chunks)} chunks")
    return chunks

def build_vectorstore(chunks: List[Document]):
    embeddings = HuggingFaceEmbeddings(
        model_name="intfloat/multilingual-e5-large-instruct",
        model_kwargs={"device": "mps" if torch.backends.mps.is_available() else "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )
    
    # Optional: delete old DB to start fresh (comment out to append)
    if CHROMA_DIR.exists():
        import shutil
        shutil.rmtree(CHROMA_DIR)
    
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(CHROMA_DIR),
        collection_name="tuhh_handbooks"
    )
    print("Vector store created and persisted")
    return vectorstore

def test_rag(vectorstore, query: str, k: int = 6):
    retriever = vectorstore.as_retriever(search_kwargs={"k": k})
    results = retriever.invoke(query)
    
    print(f"\nQuery: {query}")
    print(f"Top {len(results)} retrieved chunks:")
    for i, doc in enumerate(results, 1):
        print(f"\n--- Chunk {i} ---")
        print(f"Source: {doc.metadata['source']}")
        print(f"Program: {doc.metadata.get('program', 'N/A')}")
        print(f"Type: {doc.metadata.get('chunk_type', 'general')}")
        if "module_code" in doc.metadata:
            print(f"Module code: {doc.metadata['module_code']}")
        content = doc.page_content[:400] + "..." if len(doc.page_content) > 400 else doc.page_content
        print(content)
        print("-" * 80)

if __name__ == "__main__":
    import torch  # for mps check
    docs = load_documents()
    chunks = chunk_docs(docs)
    vectorstore = build_vectorstore(chunks)
    
    test_queries = [
        "Which modules are in the core qualification of Data Science?",
        "What are the entry requirements for Master's in Data Science?",
        "Which modules focus on machine learning or AI?",
        "What is the duration and language of the program?",
        "List modules related to mathematics or statistics",
        "What career prospects does the Data Science program offer?"
    ]
    
    for q in test_queries:
        test_rag(vectorstore, q)