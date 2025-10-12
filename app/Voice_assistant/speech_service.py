from fastapi import HTTPException
import os
import uuid
import json
import asyncio
from pathlib import Path
from openai import OpenAI
from app.config import settings
import langdetect

class SpeechService:
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required")

        # Use OpenAI client
        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_API_BASE
        )

        # Ensure audio directory exists
        os.makedirs(settings.AUDIO_RESPONSE_PATH, exist_ok=True)
        print(f"[TTS] Audio directory path: {settings.AUDIO_RESPONSE_PATH}")
        print(f"[TTS] Audio directory exists: {os.path.exists(settings.AUDIO_RESPONSE_PATH)}")
        print(f"[TTS] Audio directory is writable: {os.access(settings.AUDIO_RESPONSE_PATH, os.W_OK)}")

    async def text_to_speech(self, text: str, gender: str = "female") -> str:
        """Convert text to speech using OpenAI TTS with gender selection and language detection"""
        try:
            # Detect language
            try:
                detected_lang = langdetect.detect(text)
            except:
                detected_lang = "en"  # fallback to English
            
            # Map gender to OpenAI voice
            voice_map = {
                "male": "echo",
                "female": "sage"
            }
            
            voice = voice_map.get(gender.lower(), "coral")
            
            # Generate unique filename
            filename = f"response_{uuid.uuid4()}.mp3"
            file_path = os.path.join(settings.AUDIO_RESPONSE_PATH, filename)
            
            # Enhanced logging for debugging file paths
            print(f"[TTS] Audio path configuration:")
            print(f"[TTS] - AUDIO_RESPONSE_PATH: {settings.AUDIO_RESPONSE_PATH}")
            print(f"[TTS] - Target file path: {file_path}")
            print(f"[TTS] - Path exists: {os.path.exists(settings.AUDIO_RESPONSE_PATH)}")
            print(f"[TTS] - Path is writable: {os.access(settings.AUDIO_RESPONSE_PATH, os.W_OK)}")
            print(f"[TTS] - Path absolute: {os.path.abspath(settings.AUDIO_RESPONSE_PATH)}")
            
            # Use streaming response to write directly to file
            def sync_write():
                with self.client.audio.speech.with_streaming_response.create(
                    model="gpt-4o-mini-tts",
                    voice=voice,
                    input=text
                ) as response:
                    response.stream_to_file(str(file_path))
            
            # Run the sync operation in the background
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, sync_write)
            
            # Enhanced logging for file save verification
            file_exists = os.path.exists(file_path)
            file_size = os.path.getsize(file_path) if file_exists else 0
            print(f"[TTS] File save status:")
            print(f"[TTS] - Path: {file_path}")
            print(f"[TTS] - Exists: {file_exists}")
            print(f"[TTS] - Size: {file_size} bytes")
            print(f"[TTS] - Readable: {os.access(file_path, os.R_OK) if file_exists else False}")
            
            if not file_exists or file_size == 0:
                raise HTTPException(status_code=500, detail=f"Failed to save audio file or file is empty at: {file_path}")
            
            # Build public URL
            base_url = getattr(settings, "AUDIO_PUBLIC_URL", None) or getattr(settings, "AUDIO_BASE_URL", None) or "http://localhost:8089"
            audio_url = f"{base_url.rstrip('/')}/audio/{filename}"
            print(f"[TTS] Returning public URL: {audio_url}")
            
            return audio_url
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error converting text to speech: {str(e)}")

    def speech_to_text(self, audio_file) -> str:
        """
        Convert speech to text using OpenAI's Whisper model.
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

            # Call OpenAI Whisper
            with open(temp_file_path, "rb") as f:
                response = self.client.audio.transcriptions.create(
                    model=settings.WHISPER_MODEL,                 # e.g., "whisper-1"
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
