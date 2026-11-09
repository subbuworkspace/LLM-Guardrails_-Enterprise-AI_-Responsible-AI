"""
Gemini Service

Handles communication with Google's Gemini API.
"""
from google import genai
from config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
)
# ============================================================
# Gemini Client
# ============================================================
client = genai.Client(
    api_key=GEMINI_API_KEY
)
# ============================================================
# Generate Response
# ============================================================
def generate_response(prompt: str) -> str:
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
    )
    return response.text or ""