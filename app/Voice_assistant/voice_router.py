from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
import io
import os

from app.Voice_assistant.voice_request import VoiceToTextResponse, TTSRequest
from app.Voice_assistant.speech_service import speech_service

router = APIRouter(tags=["Voice Assistant"])


@router.post("/voice-to-text", response_model=VoiceToTextResponse, summary="Convert voice to text")
async def convert_voice_to_text(audio: UploadFile = File(...)):
    """Convert uploaded voice file to text using Whisper"""

    # Allowed MIME types for MP3, WAV, and AAC
    allowed_types = {
    "audio/mpeg",      # MP3
    "audio/wav",       # WAV
    "audio/aac",       # AAC
    "audio/mp4",       # M4A (iPhone)
    "audio/x-m4a",     # Another M4A MIME
    "audio/vnd.dlna.adts",  # AAC (ADTS container - Android)
    "application/octet-stream"  # fallback when client doesn't send proper type
    }


    # Validate content type
    if not audio.content_type or audio.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {audio.content_type}. Allowed types are: MP3, WAV, AAC."
        )

    try:
        audio_content = await audio.read()
        if not audio_content:
            raise HTTPException(status_code=400, detail="Audio file is empty")

        audio_file = io.BytesIO(audio_content)
        audio_file.name = audio.filename or "audio_file.mp3"

        transcribed_text = speech_service.speech_to_text(audio_file)

        if not transcribed_text:
            raise HTTPException(status_code=500, detail="No transcription received from service")

        return VoiceToTextResponse(
            transcribed_text=transcribed_text,
            filename=audio.filename
        )

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing audio: {str(e)}")


@router.post("/text-to-speech", summary="Convert text to speech")
async def convert_text_to_speech(request: TTSRequest):
    """Convert text to speech and return audio file with gender selection"""
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    if request.gender not in ["male", "female"]:
        raise HTTPException(status_code=400, detail="Gender must be 'male' or 'female'")

    try:
        # Call the async text_to_speech method
        audio_url = await speech_service.text_to_speech(request.text, request.gender)
        return {"audio_url": audio_url}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error converting text to speech: {str(e)}")