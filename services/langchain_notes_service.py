from langchain_text_splitters import RecursiveCharacterTextSplitter
from services.ai_notes_service import AINotesService
from domain.prompt_builder import PromptBuilder

class LangChainNotesService:
    def __init__(self):
        self.ai_service = AINotesService()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=3500,
            chunk_overlap=200
        )
    
    def generate_notes(self, transcript: str) -> str:
        
        chunks = self.text_splitter.split_text(transcript)
        chunk_notes = []
        for chunk in chunks:
            prompt = PromptBuilder.build(chunk)
            note = self.ai_service.generate_notes(prompt)
            chunk_notes.append(note)
        final_notes = self._merge_notes(chunk_notes)
        return final_notes
    def _merge_notes(self, notes: list[str]) -> str:
        return "\n\n".join(notes)