from fastapi import HTTPException
from gtts import gTTS
import os
import uuid
import json
from pathlib import Path
from groq import Groq
from app.config import settings

class SpeechService:
    def __init__(self):
        if not settings.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is required")

        # Use the plain API base (not the chat-completions URL)
        self.client = Groq(
            api_key=settings.GROQ_API_KEY,
            base_url=settings.GROQ_API_BASE  # e.g., "https://api.groq.com"
        )

        os.makedirs(settings.TEMP_DIR, exist_ok=True)
        os.makedirs(settings.AUDIO_RESPONSE_PATH, exist_ok=True)

    def text_to_speech(self, text: str) -> str:
        """Convert text to speech and save as MP3"""
        try:
            filename = f"response_{uuid.uuid4()}.mp3"
            file_path = os.path.join(settings.AUDIO_RESPONSE_PATH, filename)
            tts = gTTS(text=text, lang=settings.TTS_LANGUAGE)
            tts.save(file_path)
            return file_path
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error converting text to speech: {str(e)}")

    def speech_to_text(self, audio_file) -> str:
        """
        Convert speech to text using Groq's Whisper model.
        Accepts UploadFile or BytesIO. Will handle .filename or .name.
        """
        # Derive a filename (prefer .filename, else .name, else default)
        supplied_name = getattr(audio_file, "filename", None) or getattr(audio_file, "name", None) or "audio_file.mp3"
        ext = Path(supplied_name).suffix or ".mp3"
        temp_file_path = os.path.join(settings.TEMP_DIR, f"temp_{uuid.uuid4()}{ext}")

        try:
            # Ensure we read from the start for both UploadFile and BytesIO
            try:
                audio_file.seek(0)
            except Exception:
                pass

            # Read bytes and persist to a temp file
            content = audio_file.read()
            if not content:
                raise ValueError("Empty audio content")
            with open(temp_file_path, "wb") as f:
                f.write(content)

            # Call Groq Whisper
            with open(temp_file_path, "rb") as f:
                response = self.client.audio.transcriptions.create(
                    model=settings.WHISPER_MODEL,                 # e.g., "whisper-large-v3"
                    file=f,
                    response_format=settings.WHISPER_RESPONSE_FORMAT  # e.g., "text" | "json"
                )

            # Normalize response by format
            fmt = (settings.WHISPER_RESPONSE_FORMAT or "text").lower()

            # If SDK returns a simple string
            if isinstance(response, str):
                if fmt == "json":
                    try:
                        data = json.loads(response)
                        text = data.get("text", "")
                    except json.JSONDecodeError:
                        text = response.strip()
                else:
                    text = response.strip()
                if not text:
                    raise ValueError("No transcription received from Whisper")
                return text

            # If SDK returns an object with .text (common)
            if hasattr(response, "text"):
                text = getattr(response, "text") or ""
                if not text and fmt == "json" and hasattr(response, "json"):
                    try:
                        data = response.json()  # type: ignore
                        text = data.get("text", "")
                    except Exception:
                        pass
                if not text:
                    raise ValueError("No transcription received from Whisper")
                return text

            # If SDK returns a dict-like
            if isinstance(response, dict):
                text = response.get("text", "")
                if not text:
                    raise ValueError("No transcription received from Whisper")
                return text

            # Fallback: unknown type
            raise ValueError(f"Unexpected response type: {type(response)}")

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error converting speech to text: {str(e)}")

        finally:
            try:
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
            except Exception:
                pass

# Create service instance
speech_service = SpeechService()
