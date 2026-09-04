"""
Lustra Beauty Chatbot - FastAPI Backend

Wraps the RAG pipeline (retriever.py) + Ollama call into HTTP endpoints
that the Next.js frontend calls.

Run:
    uvicorn main:app --reload --port 8000

Prerequisites (same as before, run once in this folder):
    python chunk_data.py   (if you edit training_data.txt)
    python build_index.py  (if chunks.json changed)
Or just copy the chunks.json + index.faiss you already built.
"""
import time
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Literal

from retriever import Retriever

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "luna_v3"

app = FastAPI(title="Lustra Beauty Chatbot API")

# Allow the Next.js dev server (and later your deployed frontend) to call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",       # Next.js dev server
        "http://127.0.0.1:3000",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

print("Loading knowledge base + embedding model...")
retriever = Retriever()
print("Ready.")

SYSTEM_PROMPTS = {
    "female": (
        "You are Luna, a high-end, trendy beauty guru and chic skincare specialist. "
        "Tone: Warm, enthusiastic, chic, and encouraging. Use friendly, glamorous phrases (like 'Hey gorgeous! ✨' or 'darling') "
        "and sprinkle tasteful emojis (✨, 💖, 🌸, 💧). "
        "Blend your glamorous guru persona with scientifically grounded skincare routines."
    ),

    "male": (
        "You are Marcus, a sharp, practical men's grooming specialist. "
        "Tone: Direct, confident, brotherly, and no-nonsense (3-5 step routines max, 💪, 💈). "
        "Focus on efficiency, active lifestyles, and no-fluff facts."
    ),

    "non-binary": (
        "You are Alex, an inclusive, modern, and supportive beauty specialist for everyone. "
        "Tone: Welcoming, creative, affirming, and personalized (✨, 🌿, 💫). "
        "Customize routines to personal preferences with an open, encouraging style."
    ),
}

PERSONA_NAMES = {"female": "Luna", "male": "Marcus", "non-binary": "Alex"}


class ChatRequest(BaseModel):
    message: str
    gender_preference: Literal["female", "male", "non-binary"] = "non-binary"
    user_name: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    persona_name: str
    retrieved_topics: list[str]
    response_time_seconds: float


def build_prompt(user_message: str, gender_preference: str, user_name: Optional[str]) -> tuple[str, list[str]]:
    persona = SYSTEM_PROMPTS.get(gender_preference, SYSTEM_PROMPTS["non-binary"])

    retrieved = retriever.search(user_message, top_k=2)
    topics = [r["heading"] for r in retrieved]

    if retrieved:
        knowledge_block = "\n\n".join(
            f"[{r['heading']}] (relevance: {r['score']:.2f})\n{r['text']}"
            for r in retrieved
        )
    else:
        knowledge_block = (
            "No specific facts matched this question in the knowledge base. "
            "Answer using general skincare/beauty knowledge, and don't invent specifics."
        )

    name_line = f"\nThe user's name is {user_name}; greet them warmly and use it naturally." if user_name else ""

    prompt = f"""{persona}{name_line}

RELEVANT KNOWLEDGE FOR THIS QUESTION:
{knowledge_block}

USER QUESTION: {user_message}

INSTRUCTIONS:
- Answer using the knowledge above where relevant.
- Keep your signature lively, warm persona and emojis (✨, 💖) throughout the response!
- Give a clear, numbered routine or step-by-step guidance with realistic timeframes.
- Never sound like a robotic medical manual — speak like an expert beauty friend and mentor.

ANSWER:"""
    return prompt, topics


@app.get("/health")
def health():
    return {"status": "ok", "chunks_loaded": len(retriever.chunks)}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    prompt, topics = build_prompt(req.message, req.gender_preference, req.user_name)

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "keep_alive": "30m",
        "options": {
            "temperature": 0.7,
            "top_p": 0.9,
        },
    }

    try:
        start = time.time()
        resp = requests.post(OLLAMA_URL, json=payload, timeout=180)
        elapsed = time.time() - start
        resp.raise_for_status()
        answer = resp.json().get("response", "No response received")
    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=503, detail="Can't connect to Ollama. Make sure 'ollama serve' is running.")
    except requests.exceptions.ReadTimeout:
        raise HTTPException(status_code=504, detail="Ollama took too long to respond.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return ChatResponse(
        response=answer,
        persona_name=PERSONA_NAMES.get(req.gender_preference, "Alex"),
        retrieved_topics=topics,
        response_time_seconds=round(elapsed, 1),
    )