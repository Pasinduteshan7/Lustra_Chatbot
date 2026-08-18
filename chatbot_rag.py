"""
Lustra Beauty Chatbot - RAG Edition

Same CLI experience as chatbot.py, but the knowledge injected into each
prompt is now RETRIEVED based on the actual question, instead of always
being the first 2000 characters of training_data.txt.

Prerequisites (run once, in order):
    python chunk_data.py
    python build_index.py

Then run this file same as before:
    python chatbot_rag.py
"""
import requests
import time
from retriever import Retriever

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "luna"

print("Loading knowledge base + embedding model (first run may take ~10-20s)...")
retriever = Retriever()
print("Ready.\n")

SYSTEM_PROMPTS = {
    "female": """You are Luna, a friendly and empowering beauty expert specialized in skincare and makeup for women.
Be warm, supportive, and conversational. Focus on confidence and self-expression.
Be inclusive of all skin tones, ages, and concerns.""",

    "male": """You are Marcus, a straightforward and practical beauty expert specialized in grooming and skincare for men.
Be direct and no-nonsense. Prefer simple, efficient routines (3-5 steps max).
Consider active lifestyles and be honest about what works.""",

    "non-binary": """You are Alex, an inclusive and personalized beauty expert for everyone.
Respect all gender identities. Customize recommendations to individual preferences and comfort,
not gendered assumptions. Be creative and supportive of experimental approaches.""",
}


def build_prompt(user_message, gender_preference, user_name):
    persona = SYSTEM_PROMPTS.get(gender_preference, SYSTEM_PROMPTS["non-binary"])

    retrieved = retriever.search(user_message, top_k=3)
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

    name_line = f"\nThe user's name is {user_name}; use it naturally, not every sentence." if user_name else ""

    prompt = f"""{persona}{name_line}

RELEVANT KNOWLEDGE FOR THIS QUESTION:
{knowledge_block}

USER QUESTION: {user_message}

INSTRUCTIONS:
- Answer using the knowledge above where it's relevant. Don't force-fit facts that don't apply.
- Give a clear, numbered response for anything procedural (a routine, steps, tips).
- Mention realistic timeframes for results where relevant.
- If the knowledge above doesn't cover the question, say so honestly rather than making things up.

ANSWER:"""
    return prompt


def chat(user_message, gender_preference=None, user_name=None):
    prompt = build_prompt(user_message, gender_preference, user_name)

    print(f"\n[DEBUG] Prompt length: {len(prompt)} characters")

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.7,
            "top_p": 0.9,
        },
    }

    try:
        start = time.time()
        response = requests.post(OLLAMA_URL, json=payload, timeout=180)
        elapsed = time.time() - start
        print(f"[DEBUG] Ollama responded in {elapsed:.1f}s")

        response.raise_for_status()
        return response.json().get("response", "No response received")
    except requests.exceptions.ConnectionError:
        return "Error: Can't connect to Ollama. Make sure 'ollama serve' is running"
    except requests.exceptions.ReadTimeout:
        return "Error: Ollama took longer than 180s to respond. Something's stuck."
    except Exception as e:
        return f"Error: {str(e)}"


def setup_user_profile():
    print("\n" + "=" * 50)
    print("Welcome to Lustra Beauty Chatbot! (RAG Edition)")
    print("=" * 50)

    user_name = input("\nWhat's your name? ").strip()

    print("\nHow would you like me to tailor advice?")
    print("1. Female")
    print("2. Male")
    print("3. Non-binary/Other")
    choice = input("\nEnter your choice (1-3): ").strip()

    gender_map = {"1": "female", "2": "male", "3": "non-binary"}
    gender_preference = gender_map.get(choice, "non-binary")

    personality_names = {"female": "Luna", "male": "Marcus", "non-binary": "Alex"}
    personality_name = personality_names[gender_preference]

    print(f"\nHello {user_name}! I'm {personality_name}, your personalized beauty expert.\n")
    return user_name, gender_preference


def main():
    print("=" * 50)
    print("Lustra Beauty Chatbot (RAG + Local Neural Chat)")
    print("=" * 50)

    user_name, gender_preference = setup_user_profile()
    print("Type 'quit' or 'exit' to stop. Type 'profile' to change settings.\n")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in ["quit", "exit", "q"]:
            print(f"\nThanks for chatting with me, {user_name}! Stay beautiful!")
            break

        if user_input.lower() == "profile":
            user_name, gender_preference = setup_user_profile()
            continue

        if not user_input:
            continue

        print("\nBeauty Expert: ", end="", flush=True)
        response = chat(user_input, gender_preference=gender_preference, user_name=user_name)
        print(response)
        print()


if __name__ == "__main__":
    main()
