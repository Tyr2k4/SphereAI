import google.generativeai as genai
import os
from dotenv import load_dotenv
from logging_utils import scrub_secrets

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise SystemExit("Error: GOOGLE_API_KEY not set. Add it to your .env file (see .env.example).")

genai.configure(api_key=api_key)

print("--- Checking Available Models ---")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"Error: {scrub_secrets(e)}")