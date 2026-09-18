import google.generativeai as genai
import os
from dotenv import load_dotenv
from logging_utils import scrub_secrets

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise SystemExit("Error: GOOGLE_API_KEY not set. Add it to your .env file (see .env.example).")

genai.configure(api_key=api_key)

print("🔎 Scanning your account for working embedding models...\n")

found_working = False

try:
    # 1. List all models available to you
    for m in genai.list_models():
        # Check if it supports embeddings
        if 'embedContent' in m.supported_generation_methods:
            print(f"👉 Found candidate: {m.name}")
            
            # 2. TEST IT immediately
            try:
                genai.embed_content(model=m.name, content="Hello World")
                print(f"   ✅ SUCCESS! This model works.")
                print(f"   --------------------------------------------------")
                print(f"   🚀 COPY THIS EXACT NAME INTO YOUR CODE: {m.name}")
                print(f"   --------------------------------------------------")
                found_working = True
                break # Stop after finding the first working one
            except Exception as e:
                print(f"   ❌ Failed to use. Error: {scrub_secrets(e)}")

    if not found_working:
        print("\n🚨 CRITICAL: No working embedding models found on this API Key.")
        print("Suggestion: Go to https://aistudio.google.com/ and create a NEW API Key.")

except Exception as e:
    print(f"Error connecting to Google: {scrub_secrets(e)}")