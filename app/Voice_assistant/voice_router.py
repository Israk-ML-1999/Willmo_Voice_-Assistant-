from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
import io

from app.Voice_assistant.voice_request import VoiceToTextResponse, TTSRequest
from app.Voice_assistant.speech_service import speech_service

router = APIRouter(tags=["Voice Assistant"])


@router.post("/voice-to-text", response_model=VoiceToTextResponse, summary="Convert voice to text")
async def convert_voice_to_text(audio: UploadFile = File(...)):
    """Convert uploaded voice file to text using Whisper"""
    if not audio.content_type or not audio.content_type.startswith('audio/'):
        raise HTTPException(
            status_code=400,
            detail=f"File must be an audio file. Got content type: {audio.content_type}"
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
        audio_file_path = speech_service.text_to_speech(request.text, request.gender)
        return FileResponse(
            audio_file_path,
            media_type="audio/mpeg",
            filename="response.mp3"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error converting text to speech: {str(e)}")
