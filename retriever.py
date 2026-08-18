"""
STEP 3 of the RAG pipeline.

Loaded once when the chatbot starts. On every user message, embeds the
question and returns the most relevant knowledge chunks from the index.
"""
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

CHUNKS_FILE = "chunks.json"
INDEX_FILE = "index.faiss"
MODEL_NAME = "all-MiniLM-L6-v2"


class Retriever:
    def __init__(self):
        with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
            self.chunks = json.load(f)
        self.index = faiss.read_index(INDEX_FILE)
        self.model = SentenceTransformer(MODEL_NAME)

    def search(self, query, top_k=3, min_score=0.25):
        """Return up to top_k chunks whose similarity score clears min_score.

        min_score filters out irrelevant matches (e.g. small talk like "hi")
        so we don't stuff the prompt with unrelated facts.
        """
        query_vec = self.model.encode([query], normalize_embeddings=True)
        query_vec = np.array(query_vec, dtype="float32")

        scores, indices = self.index.search(query_vec, top_k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1 or score < min_score:
                continue
            chunk = self.chunks[idx]
            results.append({
                "text": chunk["text"],
                "heading": chunk["heading"],
                "score": float(score),
            })
        return results
