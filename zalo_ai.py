import google.generativeai as genai
from config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro")

def get_ai_response(message_text):
    try:
        prompt = f"Khách nhắn: \"{message_text}\"\nHãy phản hồi một cách tự nhiên, lịch sự."
        response = model.generate_content(prompt)
        if hasattr(response, 'text'):
            return response.text.strip()
        print(f"[AI] Không có phản hồi text: {response}")
        return None
    except Exception as e:
        print(f"[AI ERROR] {e}")
        return None
