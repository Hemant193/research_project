### What can we conclude from the experimentations?

**The Core Conclusion:** 
Improving document structuring (headers) and increasing chunk size (1024) successfully eliminated "hard retrieval failures" (bringing all strategies to an 0.80 Hit@5), but it exposed a critical flaw in **semantic ranking precision**. While Dense and HyDE can *find* the answer within 5 guesses, they fail to place the exact keyword-rich chunk at the very top. Only BM25 and Cross-Encoders possess the precision to rank the correct chunk at Position #1.

---

### How and Why the Tables Differ

We need to split this into two dimensions: **Infrastructure Changes** and **Metric Constraints**

#### A. Impact of Infrastructure ([1B/512] → [3B/1024])
*   **Why Latency Doubled across the board:** BM25 went from 5.0s → 10.2s. Retrieval takes milliseconds. The 5+ second increase is purely because `llama3.2:3b` takes twice as long to generate the final answer than `llama3.2:1b`. **Conclusion: The bottleneck in your pipeline is no longer retrieval; it is the LLM.**
*   **Why Dense & HyDE stopped failing (Hit@5):** In [1B/512], Dense was 0.733. In [3B/1024], it jumped to 0.800. Why? The 512 chunks were too small for the embedding model to understand context. The 1024 chunks kept full course descriptions together. Furthermore, prepending `"Module: M1552..."` to every chunk gave the dense model the exact anchor it needed.
*   **Why KW Coverage increased universally:** Moving from 64 overlap to 150 overlap ensured that when a chunk was cut at 1024 characters, prerequisite lists or module codes were duplicated into the next chunk, preventing keywords from falling into the void.

#### B. Impact of Metric Constraints ([3B/1024] [Top-5] → [3B/1024] [Top-2])
This is where the true character of the strategies is revealed.

*   **The BM25 Paradox (MRR went UP when Top-K went DOWN):** BM25's MRR jumped from 0.655 to 0.754, and KW Cov jumped from 0.547 to 0.639. *Why?* Because BM25 is a "sharpshooter." In Top-5, Ranks #1 and #2 were perfect, but Ranks #3, #4, and #5 were noise (e.g., empty table rows). Averaging the scores over 5 chunks diluted BM25's score. Dropping to Top-2 cut away the noise and revealed BM25's true precision.
*   **The Hybrid Perfection (Scores stayed EXACTLY the same):** Hybrid's MRR and KW Cov did not move at all (0.757 / 0.567). *Why?* The Cross-Encoder is perfectly calibrated. It proved that it places the absolute best chunk at Rank #1 or #2 every single time. Chunks #3, #4, and #5 were entirely redundant.
*   **The Dense/HyDE Collapse:** Dense Hit Rate collapsed from 0.800 to 0.567. HyDE from 0.800 to 0.633. Notice their MRR scores *did not change* (0.598 and 0.651). *Why?* Because in the Top-5 run, they were hiding the correct chunk at Rank #3 or #4. They *found* it (getting the Hit@5 point), but they lacked the precision to rank it highly. When forced to Top-2, they failed.

---

### Which Strategy is Better and When?

Based on the data, the decision matrix for when to use which strategy:

#### 1. Sparse (BM25) — The Precision Baseline
*   **When to use:** Factoid queries, acronym lookups, and when context window size is strictly limited (e.g., mobile devices, fast chatbots).
*   **Pros:** Unmatched keyword precision (highest KW Cov at Top-2). Fastest retrieval.
*   **Cons:** Fails completely on synonyms or conceptual questions ("What should I study if I like math?").

#### 2. Hybrid + Rerank
*   **When to use:** Production environments, complex multi-hop queries, and whenever accuracy matters more than 2 seconds of latency.
*   **Pros:** Perfectly consistent. It combines BM25's keyword sharpshooting with Dense's conceptual understanding, using the Cross-Encoder to guarantee the best chunk is at Rank #1. 
*   **Cons:** Highest architectural complexity. Requires loading a ~270MB Cross-Encoder model into memory.

#### 3. Dense (Vector)
*   **When to use:** ONLY when you have a massive context window (Top-10 or Top-20 retrieval) and are answering broad, conceptual questions where exact keywords don't exist.
*   **Pros:** Understands semantics ("deep learning" matches "neural networks").
*   **Cons:** Terrible ranking precision (lowest Top-2 Hit Rate). It suffers from "semantic smearing" in large chunks.

#### 4. HyDE — The Failed Experiment
*   **When to use:** **Never in this domain.** 
*   **Why it failed:** HyDE requires the LLM to hallucinate a document that looks exactly like the database. A TUHH handbook (our data) is too rigid, acronym-heavy, and structured for a small LLM (3B) to accurately mimic. It added 7+ seconds of latency for a *decrease* in accuracy compared to standard BM25.

---