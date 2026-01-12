import requests
from config.settings import (
    OPENROUTER_API_KEY,
    OPENROUTER_MODEL,
    OPENROUTER_URL,
    APP_TITLE,
    APP_REFERER,
)


class AIService:
    def __init__(self):
        if not OPENROUTER_API_KEY:
            raise RuntimeError("Set OPENROUTER_API_KEY in environment variables")

        self.headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": APP_REFERER,
            "X-Title": APP_TITLE,
        }

    def llm_with_tools(
        self,
        system_prompt: str,
        user_prompt: str,
        tools: list,
    ):
        response = requests.post(
            url=OPENROUTER_URL,
            headers=self.headers,
            json={
                "model": OPENROUTER_MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "tools": tools,
                "tool_choice": "auto",
            },
        )

        if response.status_code != 200:
            raise RuntimeError(
                f"OpenRouter API error {response.status_code}: {response.text}"
            )

        return response.json()
