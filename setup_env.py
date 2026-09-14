"""
Run this once to set up your .env file correctly.
Usage: python setup_env.py
"""
import sys

print("Which API are you setting up?")
print("  1. Anthropic (sk-ant-...)")
print("  2. Groq (gsk_...)")
choice = input("Enter 1 or 2: ").strip()

key = input("Paste your API key: ").strip()

if choice == "2":
    if not key.startswith("gsk_"):
        print("Warning: Groq keys usually start with gsk_ — double check your key.")
    content = f"GROQ_API_KEY={key}\nGROQ_MODEL=llama-3.3-70b-versatile\n"
else:
    if not key.startswith("sk-ant"):
        print("Warning: Anthropic keys usually start with sk-ant — double check your key.")
    content = f"ANTHROPIC_API_KEY={key}\nANTHROPIC_MODEL=claude-3-5-sonnet-20241022\n"

with open(".env", "w", encoding="utf-8") as f:
    f.write(content)

print("✓ .env written successfully")

import dotenv, os
dotenv.load_dotenv(".env", override=True)
if choice == "2":
    loaded = os.getenv("GROQ_API_KEY", "")
    print(f"✓ Verified: GROQ_API_KEY loaded, length={len(loaded)}")
else:
    loaded = os.getenv("ANTHROPIC_API_KEY", "")
    print(f"✓ Verified: ANTHROPIC_API_KEY loaded, length={len(loaded)}")
