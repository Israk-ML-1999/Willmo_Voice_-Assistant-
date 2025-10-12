from pydantic import BaseModel
from typing import Optional, Literal, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel
# Request Models


class TTSRequest(BaseModel):
    text: str
    gender: str = "female"  # "male" or "female"

class TTSRequest(BaseModel):
    audio_url: str    

class VoiceToTextResponse(BaseModel):
    transcribed_text: str
    filename: str


    