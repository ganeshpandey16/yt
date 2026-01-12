import time
from utils.file_writer import FileWriter
from utils.youtube_utils import YouTubeURLParser
from services.transcript_service import TranscriptService
from services.langchain_notes_service import LangChainNotesService
from domain.prompt_builder import PromptBuilder

from integrations.notion_mcp_client import NotionMCPClient
from integrations.rag_implementation import MarkdownVectorStore
from config.settings import QDRANT_API_KEY, QDRANT_URL, COLLECTION_NAME


def main():
    url = input("Enter the YouTube video URL: ").strip()
    start = time.time()

    video_id = YouTubeURLParser.extract_video_id(url)

    transcript_service = TranscriptService()
    transcript = transcript_service.get_transcript(video_id)

    notes_service = LangChainNotesService()
    prompt = PromptBuilder.build(transcript)
    notes = notes_service.generate_notes(prompt)

    FileWriter.write("output/captions.txt", transcript)
    FileWriter.write("output/ai_notes.md", notes)

    notion_client = NotionMCPClient()

    notion_prompt = f"""
    Create a Notion page titled "Notes"
    and add the following markdown content as paragraphs:

{notes}
"""
    notion_client.run(notion_prompt)

    vector_store = MarkdownVectorStore(
        qdrant_url=QDRANT_URL,
        qdrant_api_key=QDRANT_API_KEY,
        collection_name=COLLECTION_NAME,
    )

    ingest_result = vector_store.ingest_markdown("output/ai_notes.md")
    doc_id = ingest_result["doc_id"]

    print(f"✅ Notes stored in Notion")
    print(f"✅ Notes indexed in Qdrant (doc_id={doc_id})")

    print("RAG chat started. Type 'exit' to quit.\n")

    while True:
        query = input("You: ").strip()
        if query.lower() in {"exit", "quit"}:
            break

        result = vector_store.query(
            query_text=query,
            doc_id=doc_id,
        )

        print("Context-based answer:")
        print(result["context"])

if __name__ == "__main__":
    main()
