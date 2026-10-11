from google import genai

from .config import GEMINI_API_KEY, GEMINI_MODEL


def generate(prompt: str) -> str:
    if not GEMINI_API_KEY:
        return (
            "Gemini is not configured. Add GEMINI_API_KEY to your .env file, restart the app, "
            "and ask again. Retrieval is working, but generation requires the API key."
        )
    client = genai.Client(api_key=GEMINI_API_KEY)
    response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
    return response.text or "Gemini returned an empty response."

