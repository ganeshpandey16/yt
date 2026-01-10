import json
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import JSONFormatter

class TranscriptService:
    def get_transcript(self,video_id: str) -> str:

        api = YouTubeTranscriptApi()
        transcript = api.fetch(video_id,
        languages=['en', 'en-US', 'en-GB','hi','hi-IN'])

        formatter = JSONFormatter()
        json_data = json.loads(formatter.format_transcript(transcript))

        return "\n".join(item["text"] for item in json_data)
