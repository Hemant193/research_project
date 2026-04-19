from src.database import get_vector_store
from src.retrievers import get_retriever, load_docs_for_bm25
from src.rag_chain import get_qa_chain

def main():
    print("=" * 80)
    print("FULL PIPELINE TEST SUITE (Retrieval + Generation)")
    print("=" * 80)

    # 1. Initialize Database
    print("\n[1/3] Loading Vector Database...")
    try:
        vector_store = get_vector_store()
        print("✅ Database Loaded.")
    except Exception as e:
        print(f"❌ Failed to load DB: {e}")
        return

    # 2. Load Docs for BM25
    print("\n[2/3] Loading documents for BM25...")
    try:
        bm25_docs = load_docs_for_bm25()
        print(f"✅ Loaded {len(bm25_docs)} text chunks into memory.")
    except Exception as e:
        print(f"❌ Failed to load docs: {e}")
        return

    # 3. Define Test Query
    query = "I am interested in computers, math and physics, which master program suits me?"
    strategies = [
        "Sparse (BM25)",
        "Dense (Vector)", 
        "Hybrid + Rerank",
        "HyDE"
    ]

    print(f"\n[3/3] Running Query: '{query}'")
    print("-" * 80)

    # 4. Loop through strategies
    for strategy in strategies:
        print(f"\n\n>>> TESTING STRATEGY: {strategy} <<<")
        print("-" * 80)
        
        try:
            # Step A: Get Retriever
            retriever = get_retriever(strategy, vector_store, bm25_docs)
            
            # Step B: Get QA Chain (Modern API)
            print("⏳ Generating Answer via LLM (this may take a moment)...")
            qa_chain = get_qa_chain(retriever)
            
            # Step C: Run the full pipeline
            # Note: The modern API expects "input", not "query"
            response = qa_chain.invoke({"input": query})
            
            # Step D: Extract results
            # The new API returns "answer", "context", "input"
            answer_text = response["answer"]
            source_docs = response["context"] # Sources are now called 'context'
            
            # --- DISPLAY RESULTS ---
            
            # 1. The Final Answer
            print(f"\n🤖 LLM ANSWER:\n{answer_text}")
            
            # 2. The Sources
            print("\n📚 SOURCES USED:")
            for i, doc in enumerate(source_docs):
                source = doc.metadata.get('source', 'Unknown Source').split('/')[-1] # Just filename
                content_preview = doc.page_content[:200].replace('\n', ' ') + "..."
                print(f"  {i+1}. [{source}]: {content_preview}")

        except Exception as e:
            print(f"❌ ERROR in {strategy}: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()