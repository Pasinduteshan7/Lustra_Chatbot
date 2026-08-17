"""
STEP 2 of the RAG pipeline.

Embeds every chunk from chunks.json into a vector, and builds a FAISS
index for fast similarity search.

Run once after chunk_data.py, and again any time chunks.json changes:
    python build_index.py

Produces: index.faiss
"""
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

CHUNKS_FILE = "chunks.json"
INDEX_FILE = "index.faiss"

# Small (~80MB), fast on CPU, good enough quality for this use case.
# Downloads once from HuggingFace, then cached locally.
MODEL_NAME = "all-MiniLM-L6-v2"


def main():
    with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    texts = [c["text"] for c in chunks]

    print(f"Loading embedding model '{MODEL_NAME}' (downloads on first run)...")
    model = SentenceTransformer(MODEL_NAME)

    print(f"Embedding {len(texts)} chunks...")
    embeddings = model.encode(texts, show_progress_bar=True, normalize_embeddings=True)
    embeddings = np.array(embeddings, dtype="float32")

    dim = embeddings.shape[1]
    # Normalized vectors + inner product = cosine similarity search
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)

    faiss.write_index(index, INDEX_FILE)
    print(f"Saved FAISS index with {index.ntotal} vectors ({dim}-dim) -> {INDEX_FILE}")


if __name__ == "__main__":
    main()
