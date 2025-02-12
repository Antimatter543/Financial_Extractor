"""
config.py

This script:
- Loads API keys and environment variables from `.env`
- Ensures that required variables (like GEMINI API key) are set
- Provides a function to initialize the GenAI client

Functions:
- get_genai_client(): Returns a configured GenAI client instance.
"""

import os
from dotenv import load_dotenv
from google import genai



def get_genai_client():
    """Returns an authenticated GenAI client instance."""
    # Load environment variables from .env file
    load_dotenv()

    # Fetch API key from environment
    api_key = os.getenv("GEMINI_KEY")
    if not api_key:
        raise ValueError("❌ No API key found. Please check your .env file.")

    print("✅ API key loaded successfully!")

    
    return genai.Client(api_key=api_key)
