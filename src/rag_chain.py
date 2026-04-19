import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from langchain_ollama import ChatOllama
from src.config import LLM_MODEL

PROMPT = """\
You are a helpful and encouraging academic advisor for TUHH \
(Technical University of Hamburg).

Use ONLY the context below (from the TUHH Module Handbook) to answer \
the student's question.  If the answer is not in the context, say:
"I don't have enough information about that in the provided documents."

Important:
- Describe the *program* or *module* (e.g. "Master in Data Science covers …"),
  not just raw module codes.
- Be concise and professional.
- If recommending a program, briefly explain WHY it matches the student's interests.

Context:
{context}

Question: {input}

Answer:"""


class RAGChain:
    """
    Exposes a single .invoke({"input": query}) method.
    """

    def __init__(self, retriever):
        self.retriever = retriever
        self.llm       = ChatOllama(model=LLM_MODEL, temperature=0, num_predict=60)

    def invoke(self, inputs: dict) -> dict:
        query = inputs.get("input") or inputs.get("query", "")

        docs = self.retriever.invoke(query)

        context = "\n\n─────\n\n".join(d.page_content for d in docs)

        prompt   = PROMPT.replace("{context}", context).replace("{input}", query)
        response = self.llm.invoke(prompt)

        return {
            "answer":  response.content,
            "context": docs,
            "input":   query,
        }


def get_qa_chain(retriever) -> RAGChain:
    return RAGChain(retriever)