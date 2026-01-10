from utils.file_writer import FileWriter
from utils.youtube_utils import YouTubeURLParser
from services.transcript_service import TranscriptService
from services.ai_notes_service import AINotesService
from domain.prompt_builder import PromptBuilder

def main():
    url = input("Enter the YouTube video URL: ").strip()
    video_id = YouTubeURLParser.extract_video_id(url)

    transcript_service = TranscriptService()
    transcript = transcript_service.get_transcript(video_id)

    prompt = PromptBuilder.build(transcript)

    ai_service = AINotesService()
    notes = ai_service.generate_notes(prompt)

    FileWriter.write("output/captions.txt", transcript)    
    FileWriter.write("output/ai_notes.md", notes)

    print("✅ Transcript saved to output/captions.txt")
    print("✅ AI notes saved to output/ai_notes.md")
if __name__ == "__main__":
    main()