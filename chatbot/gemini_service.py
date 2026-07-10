import os
from dotenv import load_dotenv
from AI.settings import settings

load_dotenv()

def generate_response(prompt: str) -> str:
    """
    Generates response using either OpenAI (if configured in settings) or Gemini API key.
    Includes robust error boundaries and fallbacks.
    """
    # 1. Try OpenAI if configured
    if settings.llm_provider == "openai" and settings.openai_api_key:
        try:
            from openai import OpenAI
            api_key = settings.openai_api_key.get_secret_value() if hasattr(settings.openai_api_key, "get_secret_value") else settings.openai_api_key
            client = OpenAI(api_key=api_key)
            resp = client.chat.completions.create(
                model=settings.openai_model or "gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are the ASB AI Advisor, a friendly numerology expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            print(f"[Chatbot LLM] OpenAI call failed: {e}. Trying Gemini fallback.")

    # 2. Try Gemini API
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=gemini_key)
            model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"[Chatbot LLM] Gemini call failed: {e}")

    # 3. Fallback
    return "Thank you for asking! I'm here to guide you on your numerological path. For detailed insights, please try our 'Guided Reading' flow by clicking the button below."