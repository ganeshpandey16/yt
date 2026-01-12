import os
import dotenv

dotenv.load_dotenv()

#config for notion
NOTION_API_KEY = os.getenv("NOTION_API_KEY")

#config for Open Router 
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL = "nvidia/nemotron-3-nano-30b-a3b:free"
APP_TITLE = "YT Notes Generator"
APP_REFERER = "http://localhost"

#config for qdrant
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
COLLECTION_NAME = "youtube_notes"