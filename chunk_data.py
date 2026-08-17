"""
STEP 1 of the RAG pipeline.

Converts training_data.txt (one big text file) into chunks.json
(a list of small, self-contained pieces of knowledge).

Why this matters: embedding a whole 2000-word file as one vector is useless —
it blurs everything together. Embedding one fact / routine / Q&A pair at a
time means retrieval can actually find the piece that matches the question.

Run this every time you edit training_data.txt:
    python chunk_data.py
"""
import json
import re

INPUT_FILE = "training_data.txt"
OUTPUT_FILE = "chunks.json"


def parse_chunks(text):
    """Split the file into chunks, grouped under their nearest section heading."""
    chunks = []
    current_heading = "General"
    buffer = []

    def flush_buffer():
        if buffer:
            content = "\n".join(buffer).strip()
            if content:
                chunks.append({
                    "heading": current_heading,
                    "text": f"{current_heading}:\n{content}",
                })
            buffer.clear()

    for raw_line in text.splitlines():
        line = raw_line.strip()

        # A heading looks like "SKINCARE FACTS:" or "Routine for Oily Skin:"
        # (short, ends in a colon, isn't a bullet or a Q/A line)
        is_heading = (
            line.endswith(":")
            and len(line) < 60
            and not line.startswith("-")
            and not line.startswith("Q:")
            and not line.startswith("A:")
        )

        if is_heading:
            flush_buffer()
            current_heading = line.rstrip(":")
            continue

        if line == "":
            flush_buffer()
            continue

        buffer.append(line)

    flush_buffer()
    return chunks


def split_qa_pairs(chunks):
    """Break the EXAMPLE Q&A block into ONE chunk PER question, not one giant blob."""
    final_chunks = []
    for chunk in chunks:
        if "Q:" in chunk["text"] and "A:" in chunk["text"]:
            pairs = re.findall(r"Q:\s*(.+?)\s*A:\s*(.+?)(?=\nQ:|\Z)", chunk["text"], re.DOTALL)
            if pairs:
                for q, a in pairs:
                    final_chunks.append({
                        "heading": "Example Q&A",
                        "text": f"Q: {q.strip()}\nA: {a.strip()}",
                    })
                continue
        final_chunks.append(chunk)
    return final_chunks


def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        text = f.read()

    chunks = parse_chunks(text)
    chunks = split_qa_pairs(chunks)

    for i, c in enumerate(chunks):
        c["id"] = i

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)

    print(f"Parsed {len(chunks)} chunks from {INPUT_FILE} -> {OUTPUT_FILE}")
    for c in chunks[:5]:
        preview = c["text"][:70].replace("\n", " ")
        print(f"  [{c['id']}] {c['heading']}: {preview}...")


if __name__ == "__main__":
    main()
