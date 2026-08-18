import requests
import json
import os
import random

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "luna"

# Load training data for fine-tuning
TRAINING_DATA_FILE = "training_data.txt"

def load_training_data():
    """Load beauty knowledge base for few-shot learning"""
    try:
        with open(TRAINING_DATA_FILE, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return ""

TRAINING_DATA = load_training_data()

# System prompts for different genders with FINE-TUNING
SYSTEM_PROMPTS = {
    "female": """You are Luna, a high-end, trendy beauty guru and skincare specialist. 

INSTRUCTIONS:
1. Speak like a modern beauty influencer (warm, stylish, and highly knowledgeable about aesthetic treatments and trendy ingredients).
2. Avoid sounding like a doctor. Sound like a knowledgeable beauty consultant at a luxury spa.
3. Emphasize the "glow-up" aspect of skincare.
4. Use the beauty knowledge base below to inform your answers.
5. Provide specific, actionable advice with step numbers.
6. Mention ingredients and their benefits, highlighting modern trends.
7. Always mention SPF/sun protection when relevant.
8. Be inclusive of all skin tones, ages, and concerns.

BEAUTY KNOWLEDGE BASE:
{beauty_knowledge}

REMEMBER: 
- Give concrete steps numbered 1, 2, 3, etc.
- Explain WHY something works, not just WHAT to do.
- Mention timeframes for results (typically 2-8 weeks).
- Always recommend patch testing for sensitive skin.
- Keep the tone chic, professional, and beauty-focused.
""",
    
    "male": """You are Marcus, a straightforward and practical beauty expert specialized in grooming and skincare for men.

INSTRUCTIONS:
1. Be direct, practical, and no-nonsense
2. Think step-by-step before answering (chain-of-thought)
3. Use the beauty knowledge base below to inform your answers
4. Focus on simple, efficient routines (3-5 steps maximum)
5. Provide specific, measurable results
6. Consider active lifestyles and sports-related concerns
7. Acknowledge that skincare is self-care
8. Give realistic timeframes

BEAUTY KNOWLEDGE BASE:
{beauty_knowledge}

REMEMBER:
- Simplicity is key - minimal steps
- Focus on results and efficiency
- Explain the science briefly
- Be honest about what works and what doesn't
- Suggest products that deliver visible results quickly
""",
    
    "non-binary": """You are Alex, an inclusive and personalized beauty expert for everyone.

INSTRUCTIONS:
1. Respect all gender identities and expressions
2. Think step-by-step before answering (chain-of-thought)
3. Use the beauty knowledge base below to inform your answers
4. Customize recommendations based on individual preferences
5. Focus on personal goals and comfort
6. Be creative and supportive of experimental approaches
7. Provide scientifically-backed advice with flexibility
8. Honor diverse beauty standards

BEAUTY KNOWLEDGE BASE:
{beauty_knowledge}

REMEMBER:
- No stereotypes - adapt to their specific needs
- Ask clarifying questions if needed
- Suggest both traditional and unconventional options
- Focus on their individual skin concerns, not gender
- Be affirming and supportive of their choices
"""
}

def extract_relevant_examples(user_message, max_examples=2):
    """Extract relevant Q&A examples from training data"""
    # Look for Q&A examples in training data that relate to user's question
    examples = []
    keywords = ["acne", "skin", "makeup", "routine", "treatment", "dark circles", "pores", "retinol", "sunscreen"]
    
    # Check if user's message contains any keywords
    user_msg_lower = user_message.lower()
    for keyword in keywords:
        if keyword in user_msg_lower and "EXAMPLE Q&A" in TRAINING_DATA:
            # Extract a few relevant examples (this is simplified)
            start = TRAINING_DATA.find("EXAMPLE Q&A")
            if start != -1:
                examples_section = TRAINING_DATA[start:]
                return f"\nRELEVANT EXAMPLES FROM KNOWLEDGE BASE:\n{examples_section[:1500]}"  # First ~1500 chars
    
    return ""

def chat(user_message, gender_preference=None, user_name=None, use_fine_tuning=True):
    """Send message to fine-tuned Luna model with a clean, ultra-fast prompt"""
    name_str = f"My name is {user_name}. " if user_name else ""
    full_prompt = f"{name_str}{user_message}"
    
    payload = {
        "model": MODEL,
        "prompt": full_prompt,
        "stream": True,
        "options": {
            "temperature": 0.6,
            "top_p": 0.9,
            "repeat_penalty": 1.1,
        },
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=180, stream=True)
        response.raise_for_status()
        
        for line in response.iter_lines():
            if line:
                chunk = json.loads(line)
                word = chunk.get("response", "")
                print(word, end="", flush=True)
        return ""
    
    except requests.exceptions.ConnectionError:
        return "Error: Can't connect to Ollama. Make sure 'ollama serve' is running"
    except Exception as e:
        return f"Error: {str(e)}"

def setup_user_profile():
    """Setup user profile for personalization"""
    print("\n" + "=" * 50)
    print("Welcome to Lustra Beauty Chatbot!")
    print("=" * 50)
    
    # Get user name
    user_name = input("\nWhat's your name? ").strip()
    
    # Get gender preference
    print("\nHow would you like me to tailor advice?")
    print("1. 👩 Female")
    print("2. 👨 Male")
    print("3. 🌈 Non-binary/Other")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    gender_map = {
        "1": "female",
        "2": "male",
        "3": "non-binary"
    }
    
    gender_preference = gender_map.get(choice, "non-binary")
    
    # Get personality name
    personality_names = {
        "female": "Luna",
        "male": "Marcus",
        "non-binary": "Alex"
    }
    
    personality_name = personality_names[gender_preference]
    
    print(f"\n✨ Hello {user_name}! I'm {personality_name}, your personalized beauty expert.")
    print(f"I'm here to give you tailored beauty and skincare advice!\n")
    
    return user_name, gender_preference

def main():
    print("=" * 50)
    print("Lustra Beauty Chatbot (Local Neural Chat)")
    print("=" * 50)
    print("Powered by Ollama Neural Chat 3B\n")
    
    # Setup user profile
    user_name, gender_preference = setup_user_profile()
    
    print("Type 'quit' or 'exit' to stop. Type 'profile' to change settings.\n")
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print(f"\nThanks for chatting with me, {user_name}! Stay beautiful! 👋")
            break
        
        if user_input.lower() == 'profile':
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
