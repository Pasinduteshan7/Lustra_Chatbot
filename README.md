# 🌸 Lustra — AI Beauty Chatbot with Fine-Tuned LLM & RAG

<div align="center">

**An intelligent beauty and skincare chatbot powered by a locally fine-tuned LLM (Qwen 2.5 3B) with Retrieval-Augmented Generation (RAG).**

Built with ❤️ by the Lustra Team

[![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-Frontend-black?logo=next.js&logoColor=white)](https://nextjs.org/)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-purple)](https://ollama.ai/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

## 📌 Overview

Lustra is a personalized beauty and skincare AI assistant that runs **100% locally** using an open-source Large Language Model. Unlike cloud-based chatbots, Lustra offers complete privacy while delivering expert-level skincare advice through:

- 🧠 **Fine-Tuned LLM** — A Qwen 2.5 3B model fine-tuned with LoRA/QLoRA on curated beauty conversations using [Unsloth](https://github.com/unslothai/unsloth) on Google Colab.
- 📚 **RAG Pipeline** — Retrieval-Augmented Generation using FAISS vector search + Sentence Transformers to ground responses in verified skincare facts.
- 🎭 **Persona System** — Three distinct AI personalities (Luna, Marcus, Alex) tailored for different user preferences.
- ⚡ **Real-Time Streaming** — Word-by-word response streaming via Ollama for an instant, ChatGPT-like experience.

---

## ✨ Features

| Feature | Description |
|:--------|:------------|
| 🔬 **Fine-Tuned Model** | Custom LoRA-trained model (`luna`) that natively understands skincare terminology, beauty routines, and ingredient science |
| 📖 **RAG Knowledge Base** | FAISS-indexed beauty facts retrieved dynamically per question — no hallucinated product names |
| 🎭 **3 Expert Personas** | **Luna** (trendy beauty guru), **Marcus** (no-nonsense men's grooming), **Alex** (inclusive, gender-neutral) |
| 💬 **Streaming Responses** | Real-time word-by-word output — no waiting for the full response |
| 🌐 **FastAPI Backend** | Production-ready REST API (`/chat`, `/health`) with CORS support for frontend integration |
| 🖥️ **Next.js Frontend** | Modern web UI for chatting with the bot |
| 🔒 **100% Local & Private** | All inference runs on your machine via Ollama — zero data leaves your device |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        USER INPUT                           │
│                   "I have pimples help"                      │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────┐
│              FastAPI Backend (main.py)                        │
│                                                              │
│  1. Retriever searches FAISS index for relevant facts        │
│  2. Builds a lightweight prompt with retrieved context        │
│  3. Sends prompt to fine-tuned "luna" model via Ollama        │
│  4. Streams response back word-by-word                       │
└──────────────────────┬──────────────────────────────────────┘
                       │
          ┌────────────┴────────────┐
          ▼                         ▼
┌──────────────────┐     ┌──────────────────┐
│   FAISS Index    │     │  Ollama (luna)   │
│  (index.faiss)   │     │  Fine-tuned LLM  │
│  + chunks.json   │     │  Qwen 2.5 3B     │
└──────────────────┘     └──────────────────┘
```

---

## 📂 Project Structure

```
chatbot_project/
├── main.py                  # FastAPI backend (REST API with RAG + Ollama)
├── chatbot.py               # CLI chatbot (terminal interface with streaming)
├── chatbot_rag.py           # CLI chatbot with RAG pipeline
│
├── retriever.py             # FAISS vector search retriever
├── chunk_data.py            # Splits training_data.txt into indexed chunks
├── build_index.py           # Builds FAISS vector index from chunks
├── chunks.json              # Pre-processed knowledge chunks
├── index.faiss              # Pre-built FAISS similarity index
├── training_data.txt        # Beauty knowledge base (facts, routines, Q&A)
│
├── prepare_dataset.py       # Generates fine-tuning dataset (JSONL)
├── fine_tune_dataset.jsonl  # 37+ curated Luna conversations for LoRA training
├── FINETUNING_COLAB_GUIDE.md # Step-by-step Colab fine-tuning instructions
├── FINE_TUNING_GUIDE.md     # Prompt engineering & soft fine-tuning guide
│
├── model/                   # Fine-tuned GGUF model weights
│   └── qwen2.5-3b-instruct.Q4_K_M.gguf
├── Modelfile                # Ollama model registration file
│
├── frontend/                # Next.js web frontend
├── requirements.txt         # Python dependencies
└── setup.bat                # Windows one-click setup script
```

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+**
- **[Ollama](https://ollama.ai/)** installed and running (`ollama serve`)
- **Git**

### 1. Clone & Install

```bash
git clone https://github.com/<your-username>/lustra-beauty-chatbot.git
cd lustra-beauty-chatbot

# Create virtual environment & install dependencies
python -m venv venv
.\venv\Scripts\Activate.ps1   # Windows
pip install -r requirements.txt
```

### 2. Register the Fine-Tuned Model with Ollama

```bash
ollama create luna -f Modelfile
```

### 3. Run the CLI Chatbot

```bash
python chatbot.py
```

### 4. Or Run the FastAPI Backend

```bash
uvicorn main:app --reload --port 8000
```

Then send requests to `http://localhost:8000/chat`:

```json
{
  "message": "I have pimples, what should I do?",
  "gender_preference": "female",
  "user_name": "Sarah"
}
```

---

## 🧠 Fine-Tuning Pipeline

This project uses **LoRA (Low-Rank Adaptation)** fine-tuning to teach the base model Luna's persona, tone, and beauty expertise.

### Training Data
- **37+ curated conversations** covering acne, routines, ingredients, makeup, men's grooming, hair care, trending topics, and more.
- Generated via `prepare_dataset.py` → `fine_tune_dataset.jsonl`

### Training Process
1. Base model: `Qwen2.5-3B-Instruct`
2. Fine-tuned with [Unsloth](https://github.com/unslothai/unsloth) on Google Colab (free T4 GPU)
3. Exported to 4-bit GGUF (`Q4_K_M`) for local Ollama inference
4. Full step-by-step guide: [`FINETUNING_COLAB_GUIDE.md`](FINETUNING_COLAB_GUIDE.md)

### Why Fine-Tuning + RAG?
| Approach | Pros | Cons |
|:---------|:-----|:-----|
| Prompt Engineering Only | Easy to set up | Slow (huge prompts), inconsistent tone |
| Fine-Tuning Only | Fast responses, consistent persona | Can't update knowledge dynamically |
| **Fine-Tuning + RAG** ✅ | **Fast, consistent, and dynamically grounded** | Requires initial training effort |

---

## 🎭 Personas

| Persona | Name | Style |
|:--------|:-----|:------|
| 👩 Female | **Luna** | High-end beauty guru — chic, trendy, encouraging |
| 👨 Male | **Marcus** | Straightforward grooming expert — practical, no-nonsense |
| 🌈 Non-binary | **Alex** | Inclusive beauty expert — personalized, experimental |

---

## 🛠️ Tech Stack

| Layer | Technology |
|:------|:-----------|
| **LLM** | Qwen 2.5 3B (fine-tuned with LoRA via Unsloth) |
| **Inference** | Ollama (local, private, GPU/CPU) |
| **RAG** | FAISS + Sentence Transformers (`all-MiniLM-L6-v2`) |
| **Backend** | FastAPI + Pydantic |
| **Frontend** | Next.js (TypeScript) |
| **Model Format** | GGUF (Q4_K_M quantization) |

---

## 📈 Roadmap

- [x] CLI chatbot with prompt engineering
- [x] RAG pipeline (FAISS + Sentence Transformers)
- [x] FastAPI REST API backend
- [x] Fine-tuning pipeline (Unsloth + LoRA on Colab)
- [x] Real-time streaming responses
- [x] Next.js web frontend
- [ ] Flutter mobile app integration
- [ ] Conversation history & memory
- [ ] MongoDB storage for user profiles
- [ ] Product recommendation engine
- [ ] Multi-language support

---

## 🤝 Contributing

Contributions are welcome! To improve Luna's knowledge:

1. Add Q&A pairs to `prepare_dataset.py`
2. Run `python prepare_dataset.py` to regenerate `fine_tune_dataset.jsonl`
3. Re-train on Google Colab following `FINETUNING_COLAB_GUIDE.md`

---

## 📄 License

This project is licensed under the MIT License.

---

<div align="center">

**Built with 💖 by the Lustra Team**

*"Your AI beauty expert — private, fast, and always on your side."*

</div>
