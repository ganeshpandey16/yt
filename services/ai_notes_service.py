import google.generativeai as genai
from config.settings import GEMINI_API_KEY, MODEL_NAME

class AINotesService:
    def __init__(self):
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel(MODEL_NAME)

    def generate_notes(self, prompt: str) -> str:
        response = self.model.generate_content(prompt)
        return response.text